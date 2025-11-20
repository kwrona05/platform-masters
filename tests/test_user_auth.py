def test_user_register_and_login(client):
    # register user
    resp = client.post("/auth/register", json={"email": "player@skill2win.gg", "password": "Pass12345"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "player@skill2win.gg"
    assert data["is_admin"] is False

    # login user
    resp = client.post("/auth/login", json={"email": "player@skill2win.gg", "password": "Pass12345"})
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    # get /auth/me
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    me = resp.json()
    assert me["email"] == "player@skill2win.gg"
    assert me["is_admin"] is False
