from models import AdminResetCode, User


def test_user_register_duplicate(client):
    payload = {"email": "dup@skill2win.gg", "password": "Pass12345"}
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 201
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 400


def test_admin_login_wrong_password(client):
    client.post("/admin/auth/register", json={"email": "admin@skill2win.gg", "password": "Correct123!"})
    resp = client.post("/admin/auth/login", json={"email": "admin@skill2win.gg", "password": "Wrong123!"})
    assert resp.status_code == 401


def test_protected_requires_valid_token(client):
    # no token -> 401
    resp = client.get("/protected")
    assert resp.status_code == 401

    # invalid token -> 401
    resp = client.get("/protected", headers={"Authorization": "Bearer invalid"})
    assert resp.status_code == 401

    # valid user token -> 200
    client.post("/auth/register", json={"email": "player@skill2win.gg", "password": "Pass12345"})
    login = client.post("/auth/login", json={"email": "player@skill2win.gg", "password": "Pass12345"})
    token = login.json()["access_token"]
    resp = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["user_email"] == "player@skill2win.gg"


def test_reset_code_invalid_email(client, no_email):
    resp = client.post("/admin/auth/reset-code", json={"email": "none@skill2win.gg"})
    assert resp.status_code == 404


def test_reset_password_mismatch(client, db_session, no_email):
    client.post("/admin/auth/register", json={"email": "admin2@skill2win.gg", "password": "OldPass123!"})
    client.post("/admin/auth/reset-code", json={"email": "admin2@skill2win.gg"})
    admin = db_session.query(User).filter_by(email="admin2@skill2win.gg").first()
    code_entry = db_session.query(AdminResetCode).filter_by(user_id=admin.id).first()
    resp = client.post(
        "/admin/auth/new-password",
        json={
            "email": "admin2@skill2win.gg",
            "code": code_entry.code,
            "password": "NewPass123!",
            "confirmPassword": "Mismatch!",
        },
    )
    assert resp.status_code == 400
