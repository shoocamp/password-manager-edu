from datetime import datetime as dt
from typing import Optional
from pydantic import BaseModel


class PasswordItemBase(BaseModel):
    name: str
    site: Optional[str] = None
    password: str


class PaaswordItemDB(PasswordItemBase):
    id: str
    user_id: int | None = None
    created_at: dt = dt.now()
    updated_at: dt = dt.now()

    @staticmethod
    def from_db(res: tuple) -> 'PasswordItem':
        return PasswordItemBase(
            id=res[0],
            user_id=res[1],
            name=res[2],
            site=res[3],
            password=res[4],
            created_at=dt.fromtimestamp(res[5]),
            updated_at=dt.fromtimestamp(res[6])
        )

    def to_db(self):
        ...


class PasswordItemOut(BaseModel):
    created_at: dt = dt.now()
    updated_at: dt = dt.now()
    user_id: int | None = None


class User(BaseModel):
    id: int | None = None
    name: str
    password: str
