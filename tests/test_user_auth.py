from models import UserVerificationCode


def test_user_register_confirm_and_login(client, db_session, no_email):
    # register user
    resp = client.post(
        "/auth/register",
        json={
            "email": "player@skill2win.gg",
            "nickname": "player1",
            "password": "Pass12345",
            "confirmPassword": "Pass12345",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["message"]

    # cannot login before confirming email
    resp = client.post("/auth/login", json={"email": "player@skill2win.gg", "password": "Pass12345"})
    assert resp.status_code == 403

    # confirm code and login
    code_entry = db_session.query(UserVerificationCode).order_by(UserVerificationCode.id.desc()).first()
    assert code_entry
    resp = client.post(
        "/auth/verify-code",
        json={"email": "player@skill2win.gg", "code": code_entry.code},
    )
    assert resp.status_code == 200

    resp = client.post("/auth/login", json={"email": "player@skill2win.gg", "password": "Pass12345"})
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    # get /auth/me
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    me = resp.json()
    assert me["email"] == "player@skill2win.gg"
    assert me["is_admin"] is False
    assert me["is_verified_account"] is False


def test_kyc_submission_and_admin_verification(client, db_session, no_email):
    # admin setup
    client.post("/admin/auth/register", json={"email": "admin@skill2win.gg", "password": "AdminPass123!"})
    admin_login = client.post("/admin/auth/login", json={"email": "admin@skill2win.gg", "password": "AdminPass123!"})
    admin_token = admin_login.json()["access_token"]

    # user registers and confirms
    client.post(
        "/auth/register",
        json={
            "email": "kyc@skill2win.gg",
            "nickname": "kyc-user",
            "password": "Pass12345",
            "confirmPassword": "Pass12345",
        },
    )
    code_entry = db_session.query(UserVerificationCode).order_by(UserVerificationCode.id.desc()).first()
    client.post("/auth/verify-code", json={"email": "kyc@skill2win.gg", "code": code_entry.code})

    # login user
    login = client.post("/auth/login", json={"email": "kyc@skill2win.gg", "password": "Pass12345"})
    user_token = login.json()["access_token"]

    # submit KYC
    resp = client.post(
        "/auth/kyc",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "first_name": "Jan",
            "last_name": "Kowalski",
            "bank_account": "12345678901234567890123456",
            "billing_address": "Ul. Testowa 1, 00-000 Warszawa",
            "pesel": "90010112345",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["first_name"] == "Jan"
    assert resp.json()["is_verified_account"] is False

    # admin verifies account
    resp = client.post(
        "/admin/auth/users/verify",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"user_id": resp.json()["id"]},
    )
    assert resp.status_code == 200
    assert resp.json()["is_verified_account"] is True
    assert resp.json()["kyc_verified_at"] is not None
