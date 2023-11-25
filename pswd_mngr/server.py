import logging
import uuid
from typing import Annotated

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from pswd_mngr.auth import Auth
from pswd_mngr.models import PasswordItemBase, Response, ResponseOK, UserDB, PasswordItemDB, UserOut
from pswd_mngr.storage import PasswordStorage

logger = logging.getLogger(__name__)

app = FastAPI()
storage = PasswordStorage()
auth = Auth()


@app.post("/passwords/")
def create_password_item(item: PasswordItemBase, token: Annotated[UserDB, Depends(auth.decode_token)]) -> Response:
    logger.info(f"password item: {item}")
    response = storage.save_password(PasswordItemDB(**item.model_dump(), id=str(uuid.uuid4()),user_id=token["user_id"]))
    return response


@app.get("/passwords/")
def get_passwords(token: Annotated[UserDB, Depends(auth.decode_token)]) -> Response:
    result = []
    for v in storage.get_passwords(token["user_id"]):
        result.append(v)

    return ResponseOK(data=result)


@app.get("/passwords/{item_id}")
def get_password(item_id: str, token: Annotated[UserDB, Depends(auth.decode_token)]) -> Response:
    password = storage.get_password(item_id, token["user_id"])
    if password is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return ResponseOK(data=password)


@app.patch("/passwords/{item_id}")
def update_password(item_id: str, new_password: str,
                    token: Annotated[UserDB, Depends(auth.decode_token)]) -> Response:
    password_item = storage.update_password(item_id, new_password, token["user_id"])
    if password_item is None:
        raise HTTPException(status_code=404, detail="Password updated failed")
    return ResponseOK(data=password_item)


@app.delete("/passwords/{item_id}")
def del_password(item_id: str, token: Annotated[UserDB, Depends(auth.decode_token)]) -> Response:
    res = storage.del_password(item_id, token["user_id"])
    if not res:
        raise HTTPException(status_code=404, detail="Password deletion failed")
    return ResponseOK(message="Password removed successfully")


@app.post("/signup")
def create_user(user: UserOut) -> Response:
    res = storage.create_user(user)
    return ResponseOK(message="user was created", data=res)


@app.post("/login")
def login(user: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_from_db = storage.get_user_from_db(user)
    if user_from_db is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid credentials",
                            headers={"WWW-Authenticate": "Bearer"})
    return {"access_token": auth.encode_token(user_from_db)}


