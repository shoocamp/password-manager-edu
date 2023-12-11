import argparse
import logging
import uuid
import tomllib

from typing import Annotated

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from pswd_mngr.auth import Auth
from pswd_mngr.models import PasswordItemBase, Response, ResponseOK, UserDB, PasswordItemDB, UserIn
from pswd_mngr.storage import PasswordStorage, DuplicateError

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', default="config.toml")
args = parser.parse_args()
config = tomllib.load(open(args.config, "rb"))
logger.info(config)

app = FastAPI()
storage = PasswordStorage(config['database']['name'])
auth = Auth(storage)


@app.post("/passwords/")
def create_password_item(item: PasswordItemBase, token: Annotated[UserDB, Depends(auth.decode_token)]) -> Response:
    try:
        saved_item = storage.save_password(
            PasswordItemDB(**item.model_dump(), uuid=str(uuid.uuid4()), user_id=token["user_id"]))
    except DuplicateError as e:
        logger.error(f"Error when save password: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return ResponseOK(data=saved_item)


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
    row_deleted = storage.del_password(item_id, token["user_id"])
    if row_deleted == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{item_id} wasn't updated")

    if row_deleted > 1:
        logger.error(f"storage.del_password delete more then one password ({row_deleted})")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return ResponseOK(message="Password removed successfully")


@app.post("/signup")
def create_user(user: UserIn) -> Response:
    user.password = Auth.get_password_hash(user.password)
    try:
        res = storage.create_user(user)
    except DuplicateError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return ResponseOK(message="user was created", data=res)


@app.post("/login")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = Auth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"access_token": auth.encode_token(user)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", log_level="info", reload=True)
