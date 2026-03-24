import copy
import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(autouse=True)
def client():
    original_activities = copy.deepcopy(app_module.activities)
    with TestClient(app_module.app) as test_client:
        yield test_client
    app_module.activities = original_activities


def test_root_redirect(client):
    # arrange: none
    # act
    response = client.get("/")
    # assert
    assert response.status_code == 307
    assert "/static/index.html" in response.headers["location"]


def test_get_activities(client):
    # arrange: none
    # act
    response = client.get("/activities")
    # assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) >= 3
    assert "Chess Club" in data


def test_signup_for_activity_success(client):
    # arrange
    activity_name = "Chess Club"
    new_email = "teststudent@mergington.edu"
    # act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": new_email})
    # assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for {activity_name}"}
    assert new_email in app_module.activities[activity_name]["participants"]


def test_signup_for_activity_already_signed(client):
    # arrange
    activity_name = "Chess Club"
    already_email = "michael@mergington.edu"
    # act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": already_email})
    # assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_unregister_participant_success(client):
    # arrange
    activity_name = "Chess Club"
    leave_email = "michael@mergington.edu"
    # act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": leave_email})
    # assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {leave_email} from {activity_name}"}
    assert leave_email not in app_module.activities[activity_name]["participants"]


def test_unregister_participant_not_found(client):
    # arrange
    activity_name = "Chess Club"
    missing_email = "nonexistent@mergington.edu"
    # act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": missing_email})
    # assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
