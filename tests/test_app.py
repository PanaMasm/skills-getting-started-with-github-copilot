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


def test_unregister_participant_removes_their_name_from_activity(client):
    response = client.delete("/activities/Chess Club/participants/michael@mergington.edu")

    assert response.status_code == 200
    assert response.json()["message"] == "Removed michael@mergington.edu from Chess Club"

    activities = client.get("/activities").json()
    assert not any(participant.get("email") == "michael@mergington.edu" for participant in activities["Chess Club"]["participants"])


def test_signup_accepts_name_and_stores_it_for_display(client):
    response = client.post(
        "/activities/Chess Club/signup?email=student@example.com&name=Alex"
    )

    assert response.status_code == 200
    activities = client.get("/activities").json()
    participant = next(
        item for item in activities["Chess Club"]["participants"] if item["email"] == "student@example.com"
    )
    assert participant["name"] == "Alex"
