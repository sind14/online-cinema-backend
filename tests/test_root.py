from app.main import root


def test_root_returns_health_message():
    assert root() == {"message": "Online Cinema API is running"}
