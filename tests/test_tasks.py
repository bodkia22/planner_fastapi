def test_create_task(authenticated_client):
    response = authenticated_client.post(
        "/tasks/",
        json={"title": "Test Task", "description": "This is a test task."},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test Task"


def test_get_tasks(authenticated_client):
    authenticated_client.post(
        "/tasks/",
        json={"title": "Test Task 1", "description": "This is the first test task."},
    )
    authenticated_client.post(
        "/tasks/",
        json={"title": "Test Task 2", "description": "This is the second test task."},
    )

    response = authenticated_client.get("/tasks/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_task_by_id(authenticated_client):
    create_response = authenticated_client.post(
        "/tasks/",
        json={"title": "Test Task", "description": "This is a test task."},
    )
    task_id = create_response.json()["id"]

    response = authenticated_client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["id"] == task_id


def test_delete_task(authenticated_client):
    create_response = authenticated_client.post(
        "/tasks/",
        json={"title": "Test Task", "description": "This is a test task."},
    )

    task_id = create_response.json()["id"]

    response = authenticated_client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["detail"] == "Task deleted"


def test_delete_nonexistent_task(authenticated_client):
    response = authenticated_client.delete("/tasks/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_update_task(authenticated_client):
    create_response = authenticated_client.post(
        "/tasks/",
        json={"title": "Test Task", "description": "This is a test task."},
    )

    task_id = create_response.json()["id"]

    update_response = authenticated_client.put(
        f"/tasks/{task_id}",
        json={"title": "Updated Task", "description": "This task has been updated."},
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Task"
    assert update_response.json()["description"] == "This task has been updated."


def test_get_tasks_without_cookie(client):
    response = client.get("/tasks/")
    assert response.status_code == 401
