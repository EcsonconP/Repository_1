from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app, follow_redirects=False)


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_success():
    response = client.post("/activities/Chess%20Club/signup?email=newstudent@example.com")
    assert response.status_code == 200
    result = response.json()
    assert "Signed up" in result["message"]
    # Verify added
    response = client.get("/activities")
    data = response.json()
    assert "newstudent@example.com" in data["Chess Club"]["participants"]


def test_signup_duplicate():
    # First signup
    client.post("/activities/Programming%20Class/signup?email=dup@example.com")
    # Duplicate
    response = client.post("/activities/Programming%20Class/signup?email=dup@example.com")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_delete_participant():
    # Add first
    client.post("/activities/Gym%20Class/signup?email=del@example.com")
    # Delete
    response = client.delete("/activities/Gym%20Class/participants/del@example.com")
    assert response.status_code == 200
    result = response.json()
    assert "Removed" in result["message"]
    # Verify removed
    response = client.get("/activities")
    data = response.json()
    assert "del@example.com" not in data["Gym Class"]["participants"]


def test_delete_nonexistent_participant():
    response = client.delete("/activities/Chess%20Club/participants/nonexistent@example.com")
    assert response.status_code == 400
    assert "not found" in response.json()["detail"]


def test_signup_invalid_activity():
    response = client.post("/activities/Invalid%20Activity/signup?email=test@example.com")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"