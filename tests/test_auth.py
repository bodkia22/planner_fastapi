def test_register(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@test.com",
            "password": "testpassword",
        },
    )
    assert response.status_code == 201


def test_duplicate_email_registration(client):
    client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@test.com",
            "password": "testpassword",
        },
    )

    response = client.post(
        "/auth/register",
        json={
            "username": "testuser2",
            "email": "test@test.com",
            "password": "testpassword",
        },
    )
    assert response.status_code == 400


def test_duplicate_username_registration(client):
    client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@test.com",
            "password": "testpassword",
        },
    )

    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test2@test.com",
            "password": "testpassword",
        },
    )
    assert response.status_code == 400


def test_login(client):
    client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@test.com",
            "password": "testpassword",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "test@test.com",
            "password": "testpassword",
        },
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@test.com",
            "password": "testpassword",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "test@test.com",
            "password": "fakepassword",
        },
    )
    assert response.status_code == 400
