from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services.comments import CommentService
import schemas.comments as comment_schemas
from auth.dependencies import verify_comment_access
from monitoring.monitoring import logger

router = APIRouter(prefix="/comments", tags=["comments"])

@router.get("/", response_model=list[comment_schemas.Comment])
async def read_comments(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
    ):
    logger.info(
            "getting_comments"
    )
    return await CommentService.get_comments(db=db, skip=skip, limit=limit)

@router.put("/{comment_id}", response_model=comment_schemas.Comment)
async def update_comment(
    comment_id: int,
    comment_update: comment_schemas.CommentCreate,
    db: AsyncSession = Depends(get_db),
    _ = Depends(verify_comment_access)
    ):
    logger.info(
            "updating_comment_by_comment_id",
            comment_id=comment_id
    )
    updated_comment = await CommentService.update_comment(
        db=db, 
        comment_id=comment_id, 
        comment_update=comment_update
    )
    return updated_comment

@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    _ = Depends(verify_comment_access)
):
    logger.info(
            "deleting_comment_by_comment_id",
            comment_id=comment_id
    )
    await CommentService.delete_comment(db=db, comment_id=comment_id)
    return {"message": "Comment deleted successfully"}