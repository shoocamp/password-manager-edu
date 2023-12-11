def test_get_passwords(client):
    response = client.get("/passwords/")

    assert response.status_code == 200, f"response: {response.text}"
    data = response.json()
    assert data['status'] == 'ok'
    assert data['data'] == []


def test_create_password(client, password_item):
    response = client.post("/passwords/", json=password_item)
    assert response.status_code == 200, response.text
    item_id = response.json()['data']['uuid']

    response = client.get(f"/passwords/{item_id}")
    assert response.status_code == 200
    actual_data = response.json()['data']

    assert actual_data["name"] == password_item["name"]
    assert actual_data["site"] == password_item["site"]
    assert actual_data["password"] == password_item["password"]

    response = client.get(f"/passwords/")
    assert response.status_code == 200
    actual_data = response.json()['data']
    assert len(actual_data) == 1, actual_data
