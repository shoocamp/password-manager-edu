import uuid
from datetime import datetime as dt
from enum import Enum
from typing import Optional, Any

from pydantic import BaseModel


class Status(str, Enum):
    OK = 'ok'
    ERROR = 'error'


class Response(BaseModel):
    status: Status
    message: str | None = None
    data: Any = None


class ResponseOK(Response):
    status: Status = Status.OK


class PasswordItemBase(BaseModel):
    name: str
    site: Optional[str] = None
    password: str


class PasswordItemDB(PasswordItemBase):
    id: str | None
    user_id: int | None = None
    created_at: dt = dt.now()
    updated_at: dt = dt.now()

    @staticmethod
    def from_db(res: tuple) -> 'PasswordItemBase':
        return PasswordItemDB(
            id=res[0],
            user_id=res[1],
            name=res[2],
            site=res[3],
            password=res[4],
            created_at=dt.fromtimestamp(res[5]),
            updated_at=dt.fromtimestamp(res[6])
        )

    @staticmethod
    def to_db(item: PasswordItemBase) -> 'PasswordItemDB':
        return PasswordItemDB(**item.model_dump(), id=str(uuid.uuid4()))


class PasswordItemOut(PasswordItemBase):
    id: str | None
    user_id: int | None = None
    created_at: dt
    updated_at: dt

    @staticmethod
    def from_db(res: tuple) -> 'PasswordItemOut':
        return PasswordItemOut(
            id=res[0],
            user_id=res[1],
            name=res[2],
            site=res[3],
            password=res[4],
            created_at=dt.fromtimestamp(res[5]),
            updated_at=dt.fromtimestamp(res[6])
        )


class UserOut(BaseModel):
    name: str
    password: str


class UserDB(UserOut):
    id: int | None = None

    @staticmethod
    def from_db(res: tuple) -> 'UserDB':
        return UserDB(
            id=res[0],
            name=res[1],
            password=res[2]
        )
