from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Update
from telegram.ext import ContextTypes
# from fastapi import Depends
from app.database import get_session
from app.models import User
from app.typing.model_types import UserModelType
from fast_depends import inject, Depends

@inject
async def get_current_user(update: Update, context: ContextTypes.DEFAULT_TYPE, db: AsyncSession = Depends(get_session)) -> str:
    stmt = select(User)
    result = await db.execute(stmt)
    users = result.scalars().all()
    print(users)
    print(update.effective_user)
    return "good"