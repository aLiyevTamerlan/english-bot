from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Type, TypeVar, Generic, Optional, List
from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeMeta

ModelType = TypeVar("ModelType", bound=DeclarativeMeta)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: int) -> Optional[ModelType]:
        stmt = select(self.model)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        return db.query(self.model).filter(self.model.id == id).first()

    async def get_all(self, db: AsyncSession) -> List[ModelType]:
        return db.query(self.model).all()

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        obj_data = obj_in.dict()
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    async def bulk_create(self, db: AsyncSession, obj_in_list: List[CreateSchemaType]) -> List[ModelType]:
        try:
            obj_dicts = [obj.model_dump() for obj in obj_in_list]
            stmt = insert(self.model).values(obj_dicts)
            db.execute(stmt)
            db.commit()
        except Exception as e:
            db.rollback()
            raise e

    async def update(self, db: AsyncSession, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        obj_data = obj_in.dict(exclude_unset=True)
        for key, value in obj_data.items():
            setattr(db_obj, key, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: int) -> ModelType:
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj
