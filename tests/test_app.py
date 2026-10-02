import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def activities(monkeypatch):
    activity_data = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["student@mergington.edu"],
        }
    }
    monkeypatch.setattr(app_module, "activities", activity_data)
    return activity_data


@pytest.fixture
def test_client():
    return TestClient(app_module.app)


def test_root_redirects_to_static_page(test_client):
    # Arrange

    # Act
    response = test_client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_static_page_is_available(test_client):
    # Arrange

    # Act
    response = test_client.get("/static/index.html")

    # Assert
    assert response.status_code == 200


def test_get_activities_returns_activity_data(test_client, activities):
    # Arrange
    expected_activities = activities

    # Act
    response = test_client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_participant(test_client, activities):
    # Arrange
    email = "newstudent@mergington.edu"

    # Act
    response = test_client.post(
        "/activities/Chess Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(test_client, activities):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = test_client.post(
        "/activities/Chess Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }


def test_signup_returns_not_found_for_unknown_activity(test_client, activities):
    # Arrange
    email = "newstudent@mergington.edu"

    # Act
    response = test_client.post(
        "/activities/Unknown Activity/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_requires_email(test_client, activities):
    # Arrange

    # Act
    response = test_client.post("/activities/Chess Club/signup")

    # Assert
    assert response.status_code == 422


def test_unregister_removes_participant(test_client, activities):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = test_client.delete(
        "/activities/Chess Club/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_returns_not_found_for_unknown_activity(test_client, activities):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = test_client.delete(
        "/activities/Unknown Activity/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_returns_not_found_for_unregistered_email(
    test_client, activities
):
    # Arrange
    email = "notregistered@mergington.edu"

    # Act
    response = test_client.delete(
        "/activities/Chess Club/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }