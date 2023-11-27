from datetime import datetime, timedelta, timezone

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

storage = PasswordStorage()


class Auth:
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)

    @staticmethod
    def authenticate_user(username: str, password: str) -> UserDB:
        user = storage.get_user_by_name(username)
        if not user:
            return False
        if not Auth.verify_password(password, user.password):
            return False
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
