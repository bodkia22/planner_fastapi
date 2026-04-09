def test_create_task(client, auth_token):
    response = client.post(
        "/tasks/",
        json={"title": "Test Task", "description": "This is a test task."},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test Task"


def test_get_tasks(client, auth_token):
    client.post(
        "/tasks/",
        json={"title": "Test Task 1", "description": "This is the first test task."},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    client.post(
        "/tasks/",
        json={"title": "Test Task 2", "description": "This is the second test task."},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    response = client.get("/tasks/", headers={"Authorization": f"Bearer {auth_token}"})
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_task_by_id(client, auth_token):
    create_response = client.post(
        "/tasks/",
        json={"title": "Test Task", "description": "This is a test task."},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    task_id = create_response.json()["id"]

    response = client.get(
        f"/tasks/{task_id}", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == task_id


def test_delete_task(client, auth_token):
    create_response = client.post(
        "/tasks/",
        json={"title": "Test Task", "description": "This is a test task."},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    task_id = create_response.json()["id"]

    response = client.delete(
        f"/tasks/{task_id}", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "Task deleted"


def test_delete_nonexistent_task(client, auth_token):
    response = client.delete(
        "/tasks/9999", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_update_task(client, auth_token):
    create_response = client.post(
        "/tasks/",
        json={"title": "Test Task", "description": "This is a test task."},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    task_id = create_response.json()["id"]

    update_response = client.put(
        f"/tasks/{task_id}",
        json={"title": "Updated Task", "description": "This task has been updated."},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Task"
    assert update_response.json()["description"] == "This task has been updated."


def test_get_tasks_without_token(client):
    response = client.get("/tasks/")
    assert response.status_code == 401
