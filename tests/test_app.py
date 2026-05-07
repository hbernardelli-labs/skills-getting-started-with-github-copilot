import copy

from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


def setup_function():
    # Preserve the original activities state before each test.
    setup_function.original_activities = copy.deepcopy(activities)


def teardown_function():
    # Restore original activities state after each test.
    activities.clear()
    activities.update(setup_function.original_activities)


def test_get_activities_returns_activity_list():
    response = client.get("/activities")

    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert isinstance(response.json(), dict)


def test_signup_for_activity_success():
    activity_name = "Art Studio"
    email = "newstudent@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_for_activity_not_found():
    response = client.post("/activities/Nonexistent/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_for_activity_already_registered():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_delete_signup_success():
    activity_name = "Programming Class"
    email = "emma@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_delete_signup_not_registered():
    activity_name = "Gym Class"
    email = "unknown@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student not signed up for this activity"


def test_delete_signup_activity_not_found():
    response = client.delete("/activities/Nonexistent/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
