import hashlib
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

PASSWORD_MIN_LENGTH = 12
PASSWORD_MAX_LENGTH = 1024
TOKEN_BYTES = 32

password_hasher = PasswordHasher(
    time_cost=8,
    memory_cost=65536,
    parallelism=2,
    hash_len=32,
    salt_len=16,
)
DUMMY_PASSWORD_VERIFIER = password_hasher.hash("applypilot-dummy-verifier-not-an-owner-password")


class PasswordPolicyError(ValueError):
    pass


def validate_password(password: str) -> None:
    if len(password) < PASSWORD_MIN_LENGTH:
        raise PasswordPolicyError("Password must contain at least 12 characters.")
    if len(password) > PASSWORD_MAX_LENGTH:
        raise PasswordPolicyError("Password is longer than the supported maximum.")


def hash_password(password: str) -> str:
    validate_password(password)
    return password_hasher.hash(password)


def verify_password(verifier: str, password: str) -> bool:
    if len(password) > PASSWORD_MAX_LENGTH:
        return False
    try:
        return password_hasher.verify(verifier, password)
    except (VerificationError, VerifyMismatchError, InvalidHashError):
        return False


def generate_token() -> str:
    return secrets.token_urlsafe(TOKEN_BYTES)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def token_is_well_formed(token: str) -> bool:
    if not 40 <= len(token) <= 64:
        return False
    try:
        token.encode("ascii")
    except UnicodeEncodeError:
        return False
    return True
