from datetime import datetime, timedelta, timezone

from models import AdminResetCode, User


def _assert_token(response):
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_admin_register_and_login(client):
    # register
    resp = client.post(
        "/admin/auth/register",
        json={"email": "admin@example.com", "password": "Secret123!"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "admin@example.com"
    assert data["is_admin"] is True

    # login
    resp = client.post(
        "/admin/auth/login",
        json={"email": "admin@example.com", "password": "Secret123!"},
    )
    _assert_token(resp)


def test_reset_password_flow(client, db_session, no_email):
    client.post("/admin/auth/register", json={"email": "admin@skill2win.gg", "password": "OldPass123!"})

    # request reset code
    resp = client.post("/admin/auth/reset-code", json={"email": "admin@skill2win.gg"})
    assert resp.status_code == 200
    assert "code" not in resp.json()

    # pick latest code from DB
    code_entry = db_session.query(AdminResetCode).order_by(AdminResetCode.id.desc()).first()
    assert code_entry and code_entry.code

    # confirm code
    resp = client.post("/admin/auth/confirm-code", json={"email": "admin@skill2win.gg", "code": code_entry.code})
    assert resp.status_code == 200

    # set new password
    resp = client.post(
        "/admin/auth/new-password",
        json={
            "email": "admin@skill2win.gg",
            "code": code_entry.code,
            "password": "NewPass456!",
            "confirmPassword": "NewPass456!",
        },
    )
    assert resp.status_code == 200

    # login with new password
    resp = client.post(
        "/admin/auth/login",
        json={"email": "admin@skill2win.gg", "password": "NewPass456!"},
    )
    _assert_token(resp)


def test_reset_code_expires(client, db_session, no_email):
    client.post("/admin/auth/register", json={"email": "exp@skill2win.gg", "password": "OldPass123!"})
    client.post("/admin/auth/reset-code", json={"email": "exp@skill2win.gg"})
    code_entry = db_session.query(AdminResetCode).order_by(AdminResetCode.id.desc()).first()
    assert code_entry

    # Expire the code manually
    code_entry.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    db_session.add(code_entry)
    db_session.commit()

    resp = client.post(
        "/admin/auth/confirm-code",
        json={"email": "exp@skill2win.gg", "code": code_entry.code},
    )
    assert resp.status_code == 400


def test_reset_code_single_entry(client, db_session, no_email):
    client.post("/admin/auth/register", json={"email": "once@skill2win.gg", "password": "OldPass123!"})
    client.post("/admin/auth/reset-code", json={"email": "once@skill2win.gg"})
    client.post("/admin/auth/reset-code", json={"email": "once@skill2win.gg"})
    admin = db_session.query(User).filter_by(email="once@skill2win.gg").first()
    codes = db_session.query(AdminResetCode).filter_by(user_id=admin.id).all()
    assert len(codes) == 1
