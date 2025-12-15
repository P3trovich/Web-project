from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from tables.users import User
import schemas.users as user_schemas
from auth.service import AuthService
from sqlalchemy import select
from monitoring.monitoring import logger

class UserService:

    async def create_user(db: AsyncSession, user: user_schemas.UserCreate):
        result = await db.execute(select(User).where(User.email == user.email))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            logger.error(
                "failed_creating_user",
                user_id=user.user_id
            )
            raise HTTPException(status_code=409, detail="Email already exists")
        
        password = AuthService.get_password_hash(user.password)
        user = User(
            name=user.name,
            email=user.email,
            password=password,
            avatar=user.avatar
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
        result = await db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_user(db: AsyncSession, user_id: int):
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_email(db: AsyncSession, email: str):
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()