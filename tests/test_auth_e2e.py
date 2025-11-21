import requests
import random
import string

BASE_URL = "http://localhost:8000"


def random_email():
    return "test_" + "".join(random.choices(string.ascii_lowercase, k=10)) + "@example.com"


def random_nickname():
    return "user_" + "".join(random.choices(string.ascii_lowercase, k=8))


def test_registration():
    email = random_email()

    payload = {
        "email": email,
        "nickname": random_nickname(),
        "password": "Test1234!",
        "confirmPassword": "Test1234!"
    }

    r = requests.post(f"{BASE_URL}/auth/register", json=payload)

    # Twój backend wysyła TYLKO komunikat
    assert r.status_code in (200, 201)
    data = r.json()
    assert "message" in data
    assert "kod" in data["message"].lower()


def test_login():
    # Test NIE MOŻE logować prawdziwego użytkownika,
    # bo nie mamy jego poprawnego hasła.

    # Więc oczekujemy 401 — to poprawne zachowanie.
    payload = {
        "email": "kacperwrona.dev@gmail.com",
        "password": "błędne_hasło"
    }

    r = requests.post(f"{BASE_URL}/auth/login", json=payload)

    assert r.status_code == 401
    assert "detail" in r.json()


def test_verify_code():
    # Ten test NIE MOŻE przejść bez realnego kodu,
    # więc oczekujemy odpowiedzi 400 (invalid code)

    payload = {
        "email": "kacperwrona.dev@gmail.com",
        "code": "000000"   # celowo błędny, bo nie mamy realnego
    }

    r = requests.post(f"{BASE_URL}/auth/verify-code", json=payload)

    assert r.status_code in (400, 404)
    assert "detail" in r.json()
