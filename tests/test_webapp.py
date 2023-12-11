from fastapi.testclient import TestClient
from pswd_mngr.server import app
from datetime import datetime as dt

client = TestClient(app)


def sign_up():
    data = {
        "name": f"Test_User+{dt.now().timestamp()}",
        "password": "123"
    }

    response = client.post("/signup/", json=data, headers={"Content-Type": "application/json"})
    assert response.status_code == 200, response.text
    return data


def login(username, password):
    response = client.post("/login", data={"username": username, "password": password},
                           headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def test_get_passwords():
    credentials = sign_up()
    access_token = login(credentials['name'], credentials['password'])

    response = client.get("/passwords/", headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == 200, f"response: {response.text}"
    data = response.json()
    assert data['status'] == 'ok'
    assert data['data'] == []


def test_create_password():
    credentials = sign_up()
    access_token = login(credentials['name'], credentials['password'])

    data = {
        "name": f"alex@gmail.com+{dt.now().timestamp()}",
        "site": "vk.com",
        "password": "123dgds"
    }

    response = client.post("/passwords/", headers={"Authorization": f"Bearer {access_token}"}, json=data)
    assert response.status_code == 200, response.text
    item_id = response.json()['data']['uuid']

    response = client.get(f"/passwords/{item_id}", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    actual_data = response.json()['data']

    assert actual_data["name"] == data["name"]
    assert actual_data["site"] == data["site"]
    assert actual_data["password"] == data["password"]

    response = client.get(f"/passwords/", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    actual_data = response.json()['data']
    assert len(actual_data) == 1, actual_data
