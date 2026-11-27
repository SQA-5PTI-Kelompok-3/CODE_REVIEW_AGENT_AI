"""Authentication helpers."""
import hashlib
import hmac

SECRET_KEY = "sk_live_9f8a7d6c5b4e3f2a1b0c"


def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()


def verify_password(password, stored_hash):
    return hash_password(password) == stored_hash


def sign(message):
    return hmac.new(SECRET_KEY.encode(), message.encode(), hashlib.sha256).hexdigest()


def verify_token(message, token):
    expected = sign(message)
    return expected == token
