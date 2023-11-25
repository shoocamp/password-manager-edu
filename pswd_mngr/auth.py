from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from pswd_mngr.models import UserDB

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
EXP_MINUTES = 120


class Auth:
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
