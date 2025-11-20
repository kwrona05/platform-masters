def test_cors_preflight(client):
    resp = client.options(
        "/auth/login",
        headers={
            "Origin": "http://example.com",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert resp.status_code in (200, 204)
    # CORSMiddleware powinno zwrócić nagłówki pozwalające na cross-origin
    assert resp.headers.get("access-control-allow-origin") in ("*", "http://example.com")


def test_missing_payload_returns_generic_error(client):
    # Brak password => powinien być lakoniczny komunikat (bez listy pól)
    resp = client.post("/auth/register", json={"email": "missing@skill2win.gg"})
    assert resp.status_code == 400
    data = resp.json()
    assert data.get("detail") == "Invalid request payload."
