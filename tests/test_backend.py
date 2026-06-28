import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(autouse=True)
def reset_activities():
    original_state = copy.deepcopy(app_module.activities)
    yield
    app_module.activities = copy.deepcopy(original_state)


@pytest.fixture()
def client():
    return TestClient(app_module.app)


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_the_available_activities(client):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert "Programming Class" in payload
    assert payload["Chess Club"]["participants"][0]["email"] == "michael@mergington.edu"


def test_signup_adds_a_new_participant_to_the_activity(client):
    response = client.post(
        "/activities/Chess Club/signup?email=student@example.com&name=Alex"
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Signed up Alex for Chess Club"

    activities = client.get("/activities").json()
    participant = next(
        item for item in activities["Chess Club"]["participants"] if item["email"] == "student@example.com"
    )
    assert participant["name"] == "Alex"


def test_signup_rejects_duplicate_participant(client):
    response = client.post("/activities/Chess Club/signup?email=michael@mergington.edu")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_removes_the_requested_participant(client):
    response = client.delete("/activities/Chess Club/participants/michael@mergington.edu")

    assert response.status_code == 200
    assert response.json()["message"] == "Removed michael@mergington.edu from Chess Club"

    activities = client.get("/activities").json()
    assert not any(
        participant.get("email") == "michael@mergington.edu"
        for participant in activities["Chess Club"]["participants"]
    )


def test_unregister_returns_404_for_unknown_participant(client):
    response = client.delete("/activities/Chess Club/participants/unknown@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
