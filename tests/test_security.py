import pytest

from utils.rate_limiter import rate_limiter


def test_sql_injection_in_login_rejected(client, no_email):
    # prepare user
    client.post(
        "/auth/register",
        json={
            "email": "safe@skill2win.gg",
            "nickname": "safeuser",
            "password": "Pass12345",
            "confirmPassword": "Pass12345",
        },
    )
    # try injection-like payload
    resp = client.post(
        "/auth/login",
        json={"email": "safe@skill2win.gg' OR '1'='1", "password": "anything"},
    )
    assert resp.status_code in (400, 401, 403)


@pytest.mark.parametrize("limit", [2])
def test_rate_limit_hits_429(client, limit):
    # tighten limiter for test
    rate_limiter.max_requests = limit
    rate_limiter.window_seconds = 60
    for _ in range(limit):
        resp = client.get("/protected", headers={"Authorization": "Bearer invalid"})
        assert resp.status_code == 401
    # next request should be blocked by rate limiter before auth
    resp = client.get("/protected", headers={"Authorization": "Bearer invalid"})
    assert resp.status_code == 429
    assert "Too many requests" in resp.json()["detail"]
