from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from auth.service import AuthService
from auth.schemas import Token, UserLogin, SessionInfo
from auth.dependencies import get_current_user
from tables.users import User
import schemas.users as user_schemas
from auth.sso import github_sso
from monitoring.monitoring import track_user_registration, logger

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=Token)
@track_user_registration
async def register(
    user_data: user_schemas.UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
    ):
    'Регистрация пользователя при помощи почты и пароля.'
    try:
        user_agent = request.headers.get("user-agent")
        
        logger.info(
            "registration_started",
            email=user_data.email,
            user_agent=user_agent
        )
        
        result = await AuthService.register_user(db, user_data, user_agent)
        
        logger.info(
            "registration_completed",
            email=user_data.email,
            has_tokens=bool(result.access_token)
        )
        
        return result
        
    except Exception as e:
        # Логируем ошибку регистрации
        logger.error(
            "registration_failed",
            email=user_data.email,
            error=str(e),
            error_type=type(e).__name__
        )
        raise

@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db)
    ):
    logger.info(
            "login_attempt",
            email=user_data.email
    )
    return await AuthService.login_user(db, user_data, request)

@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    db: AsyncSession = Depends(get_db)
    ):
    'Получить новые access token и refresh token.'
    return await AuthService.refresh_session(db, request)

@router.post("/logout")
async def logout(
    request: Request,
    db: AsyncSession = Depends(get_db)
    ):
    'Удалить refresh token. access token при этом будет действовать ещё некоторое время вплоть до окончания времени истечение токена.'
    logger.info(
            "logout"
    )
    if refresh_token:
        await AuthService.delete_refresh_session(request)
    
    return {"message": "Successfully logged out"}

@router.get("/sessions", response_model = list[SessionInfo])
async def get_my_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
    ):
    logger.info(
            "get_all_user_sessions",
            user_id=current_user.user_id
    )
    'Показать все сессии пользователя.'
    return await AuthService.get_user_sessions(current_user.id)

@router.get("/me", response_model=user_schemas.User)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    'Показать данные текущего пользователя.'
    logger.info(
            "getting_user_info",
             user_id=current_user.user_id
    )
    return current_user

# Redirect на страничку github для авторизации
@router.get("/github")
async def github_login():
    'Вход через github'
    return await github_sso.get_login_redirect()

@router.get("/github/callback", response_model=Token)
async def github_callback(
    request: Request,
    db: AsyncSession = Depends(get_db)
    ):
    'Callback для авторизации через github. Здесь получаем токены.'
    return await AuthService.get_github_callback(db, request)