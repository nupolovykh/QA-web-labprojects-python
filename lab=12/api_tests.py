import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from main import app

# task 2. Tests for API. Nikita Polovykh 107б1
client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello world!"}

@pytest.mark.parametrize("user_data", [
    {"index": 1, "name": "Alice", "role": "admin"},
    {"index": 2, "name": "Bob", "role": "user"},
    {"index": 3, "name": "Charlie", "role": "guest"},
])
def test_create_user(user_data):
    response = client.post("/user", json=user_data)
    assert response.status_code == 200
    assert response.json() == user_data

def test_create_user_with_duplicate_index():
    response = client.post("/user", json={"index": 1, "name": "Alice", "role": "admin"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Index already exists"}

def test_get_users():
    response = client.get("/user")
    assert response.status_code == 200
    assert len(response.json()) == 3

@pytest.mark.parametrize("user_index, expected_name", [
    (1, "Alice"),
    (2, "Bob"),
    (3, "Charlie"),
])
def test_get_existing_user(user_index, expected_name):
    response = client.get(f"/user/{user_index}")
    assert response.status_code == 200
    assert response.json() == {"index": user_index, "name": expected_name, "role": "admin"} \
        if user_index == 1 else \
        {"index": user_index, "name": expected_name, "role": "user" if user_index == 2 else "guest"}

def test_get_user_with_nonexistent_index():
    response = client.get("/user/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

@pytest.mark.parametrize("user_index", [1, 2, 3])
def test_delete_existing_user(user_index):
    response = client.delete(f"/user/{user_index}")
    assert response.status_code == 200
    assert response.json() == {"detail": "User deleted"}

def test_delete_nonexistent_user():
    response = client.delete("/user/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}