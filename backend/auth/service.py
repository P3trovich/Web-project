from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status, Request
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy.ext.asyncio import AsyncSession
from config import settings
from tables.users import User
from sqlalchemy import select
from auth.schemas import Token, UserLogin
import schemas.users as user_schemas
from auth.sso import github_sso
from redis_cache.redis_client import get_redis
import json
from datetime import datetime

ph = PasswordHasher()

class AuthService:

    def verify_password(plain_password: str, hashed_password: str) -> bool:
        if hashed_password is None:
            return False
        try:
            return ph.verify(hashed_password, plain_password)
        except VerifyMismatchError:
            return False

    def get_password_hash(password: str) -> str:
        return ph.hash(password)

    def create_access_token(data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    def create_refresh_token(data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=int(settings.REFRESH_TOKEN_EXPIRE_DAYS))
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    def verify_token(token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None

    async def create_refresh_session(user_id: int, refresh_token: str, user_agent: str = None):
        expires_at = datetime.utcnow() + timedelta(days=int(settings.REFRESH_TOKEN_EXPIRE_DAYS))

        redis_client = await get_redis()
        session_key = f"refresh_session:{refresh_token}"
        session_dict = {
            "user_id": user_id,
            "refresh_token": refresh_token,
            "user_agent": user_agent,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expires_at.isoformat()
        }
        # 300 секунд
        expire_seconds = 300
        await redis_client.set(session_key, json.dumps(session_dict), ex=expire_seconds)
        user_key = f"sessions_for_user_id:{user_id}"
        # Создаём новую хеш-таблицу с единственным refresh_token
        # или добавляем к существующей хещ-таблице значение refresh_token
        await redis_client.sadd(user_key, refresh_token)
        # Выставляем время жизни кеша
        await redis_client.expire(user_key, expire_seconds)

    async def get_refresh_session(refresh_token: str) -> Optional[dict]:
        redis_client = await get_redis()
        session_key = f'refresh_session:{refresh_token}'
        cached_session = await redis_client.get(session_key)
        if cached_session:
            print("Сессия есть в кеше! Возвращаем...")
            # Возвращаем словарь python
            return json.loads(cached_session)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No session was found"
            )

    async def delete_refresh_session(request: Request):
        refresh_token = request.headers.get("Authorization", "").replace("Bearer ", "")
        redis_client = await get_redis()
        # Получаем сессию чтобы узнать user_id
        session = await AuthService.get_refresh_session(refresh_token)
        if session:
            user_id = session.get("user_id")

            session_key = f"refresh_session:{refresh_token}"
            await redis_client.delete(session_key)

            if user_id:
                user_key = f'sessions_for_user_id:{user_id}'
                await redis_client.srem(user_key, refresh_token)

            return {"message": "Successfully logged out"}
        else:
            from main import get_hawk
            hawk = get_hawk()
            hawk.send(ValueError("Couldn't find a session"), {"status_code": "404"})
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Refresh session not found"
            )

    async def get_user_sessions(user_id: int):
        redis_client = await get_redis()
        user_key = f'sessions_for_user_id:{user_id}'
        refresh_tokens = await redis_client.smembers(user_key)

        sessions = []
        for token in refresh_tokens:
            session = await AuthService.get_refresh_session(token)
            if session:
                sessions.append(session)
        
        return sessions

    async def create_or_update_user_from_github(db: AsyncSession, sso_user) -> User:
        github_id = sso_user.id
        email = sso_user.email
        name = sso_user.display_name or sso_user.email.split('@')[0]
        avatar = sso_user.picture

        result = await db.execute(select(User).where(User.github_id == github_id))
        user = result.scalar_one_or_none()
        
        if user:
            if name and user.name != name:
                user.name = name
            if avatar and user.avatar != avatar:
                user.avatar = avatar
            if email and user.email != email:
                user.email = email
            await db.commit()
            await db.refresh(user)
        else:
            user = User(
                github_id=github_id,
                email=email or f"{github_id}@github.user",
                name=name,
                avatar=avatar,
                password=None 
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        
        return user
    
    async def create_user_tokens(db: AsyncSession, user: User, user_agent: str = None) -> Token:
        access_token = AuthService.create_access_token(data={"user_id": user.id, "email": user.email})
        refresh_token = AuthService.create_refresh_token(data={"user_id": user.id})
        
        await AuthService.create_refresh_session(user.id, refresh_token, user_agent)
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    
    async def register_user(db: AsyncSession, user_data: user_schemas.UserCreate, user_agent: str = None) -> Token:
        result = await db.execute(select(User).where(User.email == user_data.email))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            from main import get_hawk
            hawk = get_hawk()
            hawk.send(ValueError("Couldn't create user"), {"status_code": "409"})
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        password = AuthService.get_password_hash(user_data.password)
        user = User(
            name=user_data.name,
            email=user_data.email,
            password=password,
            avatar=user_data.avatar
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        return await AuthService.create_user_tokens(db, user, user_agent)
    
    async def login_user(db: AsyncSession, user_data: UserLogin, request: Request) -> Token:
        
        result = await db.execute(select(User).where(User.email == user_data.email))
        user = result.scalar_one_or_none()
        if not user or not AuthService.verify_password(user_data.password, user.password):
            from main import get_hawk
            hawk = get_hawk()
            hawk.send(ValueError("Couldn't login user"), {"status_code": "401"})
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
                
            )
        
        user_agent = request.headers.get("user-agent")
        
        return await AuthService.create_user_tokens(db, user, user_agent)
    
    async def refresh_session(db: AsyncSession, request: Request):
        user_agent = request.headers.get("user-agent")
        refresh_token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not refresh_token:
            from main import get_hawk
            hawk = get_hawk()
            hawk.send(ValueError("Refresh token problem"), {"status_code": "401"})
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token required"
            )

        payload = AuthService.verify_token(refresh_token)
        if not payload:
            from main import get_hawk
            hawk = get_hawk()
            hawk.send(ValueError("Refresh token problem"), {"status_code": "401"})
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        session = await AuthService.get_refresh_session(refresh_token)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh session not found"
            )
    
        user_id = payload.get("user_id")
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            from main import get_hawk
            hawk = get_hawk()
            hawk.send(ValueError("Couldn't find a user"), {"status_code": "401"})
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        await AuthService.delete_refresh_session(request)

        return await AuthService.create_user_tokens(db, user, user_agent)
    
    async def get_github_callback(db: AsyncSession, request: Request):
        try:
            user = await github_sso.verify_and_process(request)           
            db_user = await AuthService.create_or_update_user_from_github(db, user)
            user_agent = request.headers.get("user-agent")

            return await AuthService.create_user_tokens(db, db_user, user_agent)
        
        except Exception as e:
            print(f"GitHub OAuth error: {e}")
            from main import get_hawk
            hawk = get_hawk()
            hawk.send(ValueError(f"GitHub OAuth error: {e}"), {"status_code": "401"})
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="GitHub authentication failed"
            )