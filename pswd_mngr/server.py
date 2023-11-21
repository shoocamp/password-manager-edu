import logging
from typing import Annotated

from fastapi import FastAPI, HTTPException

from pswd_mngr.models import PasswordItemBase, Response, ResponseOK
from pswd_mngr.storage import PasswordStorage

logger = logging.getLogger(__name__)

app = FastAPI()

storage = PasswordStorage()


@app.post("/passwords/")
def create_password_item(item: PasswordItemBase) -> Response:
    logger.info(f"password item: {item}")
    storage.save_password(item)
    return ResponseOK(message="password was created")


@app.get("/passwords/")
def get_passwords() -> Response:
    result = []
    for v in storage.get_passwords():
        result.append(v)

    return ResponseOK(data=result)


@app.get("/passwords/{item_id}")
def get_password(item_id: str) -> Response:
    password = storage.get_password(item_id)
    if password is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return ResponseOK(data=password)


@app.patch("/passwords/{item_id}")
def update_password(item_id: str, new_password: str) -> Response:
    password_item = storage.update_password(item_id, new_password)
    if password_item is None:
        raise HTTPException(status_code=404, detail="Password updated failed")
    return ResponseOK(data=password_item)


@app.delete("/passwords/{item_id}")
def del_password(item_id: str) -> Response:
    res = storage.del_password(item_id)
    if not res:
        raise HTTPException(status_code=404, detail="Password deletion failed")
    return ResponseOK(message="Password removed successfully")
