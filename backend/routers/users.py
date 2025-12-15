from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services.users import UserService
import schemas.users as user_schemas
from auth.dependencies import get_current_user
from monitoring.monitoring import logger

router = APIRouter(prefix="/users", tags=["users"])

'''@router.post("/", response_model=user_schemas.User)
def create_user(user: user_schemas.UserCreate, db: Session = Depends(get_db)):
    return UserService.create_user(db=db, user=user)'''

@router.get("/", response_model=list[user_schemas.User])
async def read_users(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
    ):
    logger.info(
            "getting_users",
             user_id=current_user.user_id
    )
    users = await UserService.get_users(db=db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=user_schemas.User)
async def read_user(
    user_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
    ):
    user = await UserService.get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user