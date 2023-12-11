from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from pswd_mngr.models import UserDB
from pswd_mngr.storage import PasswordStorage

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
EXP_MINUTES = 120


class Auth:
    def __init__(self, storage: PasswordStorage):
        self.storage = storage

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)

    def authenticate_user(self, username: str, password: str) -> Optional[UserDB]:
        user = self.storage.get_user_by_name(username)
        if user and Auth.verify_password(password, user.password):
            return user

    @staticmethod
    def encode_token(user: UserDB) -> str:
        data = {
            "sub": user.name,
            "user_id": user.id,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=EXP_MINUTES)
        }
        return jwt.encode(data, SECRET_KEY, ALGORITHM)

    @staticmethod
    def decode_token(token: str = Depends(oauth2_scheme)):
        try:
            data = jwt.decode(token, SECRET_KEY, [ALGORITHM])
            return data
        except jwt.exceptions.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Session Expired')
        except jwt.exceptions.InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Invalid Token')
