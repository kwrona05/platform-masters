from models import AdminResetCode, User, UserVerificationCode


def test_user_register_duplicate(client, no_email):
    payload = {
        "email": "dup@skill2win.gg",
        "nickname": "dup1",
        "password": "Pass12345",
        "confirmPassword": "Pass12345",
    }
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 201
    assert "message" in resp.json()
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 400


def test_user_register_duplicate_nickname(client, no_email):
    base = {
        "nickname": "dup-nick",
        "password": "Pass12345",
        "confirmPassword": "Pass12345",
    }
    resp = client.post("/auth/register", json={"email": "nick1@skill2win.gg", **base})
    assert resp.status_code == 201
    resp = client.post("/auth/register", json={"email": "nick2@skill2win.gg", **base})
    assert resp.status_code == 400


def test_user_register_password_mismatch(client, no_email):
    payload = {
        "email": "mismatch@skill2win.gg",
        "nickname": "mismatch",
        "password": "Pass12345",
        "confirmPassword": "OtherPass123",
    }
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 400


def test_admin_login_wrong_password(client):
    client.post("/admin/auth/register", json={"email": "admin@skill2win.gg", "password": "Correct123!"})
    resp = client.post("/admin/auth/login", json={"email": "admin@skill2win.gg", "password": "Wrong123!"})
    assert resp.status_code == 401


def test_protected_requires_valid_token(client, db_session, no_email):
    # no token -> 401
    resp = client.get("/protected")
    assert resp.status_code == 401

    # invalid token -> 401
    resp = client.get("/protected", headers={"Authorization": "Bearer invalid"})
    assert resp.status_code == 401

    # valid user token -> 200
    client.post(
        "/auth/register",
        json={
            "email": "player@skill2win.gg",
            "nickname": "player2",
            "password": "Pass12345",
            "confirmPassword": "Pass12345",
        },
    )
    code_entry = db_session.query(UserVerificationCode).order_by(UserVerificationCode.id.desc()).first()
    client.post("/auth/verify-code", json={"email": "player@skill2win.gg", "code": code_entry.code})
    login = client.post("/auth/login", json={"email": "player@skill2win.gg", "password": "Pass12345"})
    token = login.json()["access_token"]
    resp = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["user_email"] == "player@skill2win.gg"


def test_reset_code_invalid_email(client, no_email):
    resp = client.post("/admin/auth/reset-code", json={"email": "none@skill2win.gg"})
    assert resp.status_code == 404


def test_resend_verification_unknown_and_confirmed(client, db_session, no_email):
    # unknown email
    resp = client.post("/auth/resend-code", json={"email": "ghost@skill2win.gg"})
    assert resp.status_code == 404

    # register + confirm
    client.post(
        "/auth/register",
        json={
            "email": "resend@skill2win.gg",
            "nickname": "resenduser",
            "password": "Pass12345",
            "confirmPassword": "Pass12345",
        },
    )
    code_entry = db_session.query(UserVerificationCode).order_by(UserVerificationCode.id.desc()).first()
    client.post("/auth/verify-code", json={"email": "resend@skill2win.gg", "code": code_entry.code})
    resp = client.post("/auth/resend-code", json={"email": "resend@skill2win.gg"})
    assert resp.status_code == 400


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


def test_confirm_code_invalid(client, db_session, no_email):
    client.post(
        "/auth/register",
        json={
            "email": "wrong@skill2win.gg",
            "nickname": "wrongcode",
            "password": "Pass12345",
            "confirmPassword": "Pass12345",
        },
    )
    resp = client.post("/auth/verify-code", json={"email": "wrong@skill2win.gg", "code": "000000"})
    assert resp.status_code == 400


def test_banned_user_cannot_login(client, db_session, no_email):
    # admin setup
    client.post("/admin/auth/register", json={"email": "admin3@skill2win.gg", "password": "AdminPass123!"})
    admin_login = client.post("/admin/auth/login", json={"email": "admin3@skill2win.gg", "password": "AdminPass123!"})
    admin_token = admin_login.json()["access_token"]

    # user register + confirm
    client.post(
        "/auth/register",
        json={
            "email": "banned@skill2win.gg",
            "nickname": "banme",
            "password": "Pass12345",
            "confirmPassword": "Pass12345",
        },
    )
    code_entry = db_session.query(UserVerificationCode).order_by(UserVerificationCode.id.desc()).first()
    client.post("/auth/verify-code", json={"email": "banned@skill2win.gg", "code": code_entry.code})

    # ban user
    resp = client.post(
        "/admin/auth/users/ban",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"user_id": db_session.query(User).filter_by(email="banned@skill2win.gg").first().id},
    )
    assert resp.status_code == 200

    # login should fail
    resp = client.post("/auth/login", json={"email": "banned@skill2win.gg", "password": "Pass12345"})
    assert resp.status_code == 403

    # unban should allow login again
    resp = client.post(
        "/admin/auth/users/unban",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"user_id": db_session.query(User).filter_by(email="banned@skill2win.gg").first().id},
    )
    assert resp.status_code == 200
    resp = client.post("/auth/login", json={"email": "banned@skill2win.gg", "password": "Pass12345"})
    assert resp.status_code == 200
