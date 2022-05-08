from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_start():
    response = client.get("/")
    assert response.status_code == 200


def test_login():
    response = client.post("/api/v1/signup", json={"username": "dragex", "email": "wejoined@uni.co", "password": "hellousersigned789"})
    assert response.status_code == 200
