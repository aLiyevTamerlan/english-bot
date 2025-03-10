from app.crud.base import CRUDBase
from app.models import User
from app.schema.user_schema import UserCreateSchema, UserUpdateSchema


class CRUDuser(CRUDBase[User, UserCreateSchema, UserUpdateSchema]):
    pass



user_crud_obj = CRUDuser(User)