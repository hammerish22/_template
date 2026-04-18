from api._model import (
    _Counterparty,
    _Counterparty_Type
)


class Counterparty_Type(_Counterparty_Type):
    __tablename__ = "_counterparty_type"


class Counterparty(_Counterparty):
    __tablename__ = "_counterparty"
