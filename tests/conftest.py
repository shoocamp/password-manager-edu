from datetime import datetime as dt

import pytest
from fastapi.testclient import TestClient

from pswd_mngr.server import app

fastapi_client = TestClient(app)


@pytest.fixture
def sign_up():
    data = {
        "name": f"Test_User+{dt.now().timestamp()}",
        "password": "123"
    }

    response = fastapi_client.post("/signup/", json=data, headers={"Content-Type": "application/json"})
    assert response.status_code == 200, response.text
    return data


@pytest.fixture
def login(sign_up):
    response = fastapi_client.post("/login", data={"username": sign_up['name'], "password": sign_up['password']},
                                   headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


@pytest.fixture
def client(login):
    client = TestClient(app)
    client.headers = {"Authorization": f"Bearer {login}"}
    return client


@pytest.fixture
def password_item():
    return {
        "name": f"alex@gmail.com+{dt.now().timestamp()}",
        "site": "vk.com",
        "password": "123dgds"
    }
