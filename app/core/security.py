import re
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def validate_password_complexity(password: str) -> None:
    rules = [
        (len(password) <= 128, "Password is too long."),
        (len(password) >= 8, "Password must be at least 8 characters long."),
        (
            bool(re.search(r"[A-Z]", password)),
            "Password must contain at least one uppercase letter.",
        ),
        (
            bool(re.search(r"[a-z]", password)),
            "Password must contain at least one lowercase letter.",
        ),
        (bool(re.search(r"\d", password)), "Password must contain at least one digit."),
        (
            bool(re.search(r"[^\w\s]", password)),
            "Password must contain at least one special character.",
        ),
    ]

    for condition, message in rules:
        if not condition:
            raise ValueError(message)
