from api._model import (
    _User,
    _User_Type
)


class User(_User):
    __tablename__ = "_user"


class User_Type(_User_Type):
    __tablename__ = "_user_type"
