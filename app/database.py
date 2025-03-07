from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncAttrs

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings


engine = create_async_engine(settings.DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()  

Base = declarative_base(cls=AsyncAttrs)