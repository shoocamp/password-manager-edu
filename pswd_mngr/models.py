import uuid
from datetime import datetime as dt
from typing import Optional
from pydantic import BaseModel


class PasswordItemBase(BaseModel):
    name: str
    site: Optional[str] = None
    password: str


class PasswordItemDB(PasswordItemBase):
    id: str
    user_id: int | None = None
    created_at: dt = dt.now()
    updated_at: dt = dt.now()

    @staticmethod
    def from_db(res: tuple) -> 'PasswordItemBase':
        return PasswordItemBase(
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
        return PasswordItemDB(**item.dict(), id=str(uuid.uuid4()))


class PasswordItemOut(PasswordItemBase):
    created_at: dt = dt.now()
    updated_at: dt = dt.now()
    user_id: int | None = None

    @staticmethod
    def from_db(res: tuple) -> 'PasswordItemOut':
        return PasswordItemOut(
            user_id=res[1],
            name=res[2],
            site=res[3],
            password=res[4],
            created_at=dt.fromtimestamp(res[5]),
            updated_at=dt.fromtimestamp(res[6])
        )


class User(BaseModel):
    id: int | None = None
    name: str
    password: str
