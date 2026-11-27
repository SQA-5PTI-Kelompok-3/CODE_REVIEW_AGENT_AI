"""Store user sessions inside a signed-less cookie."""
import base64
import pickle


def dump_session(session):
    return base64.b64encode(pickle.dumps(session)).decode()


def load_session(cookie_value):
    return pickle.loads(base64.b64decode(cookie_value))


def is_admin(cookie_value):
    session = load_session(cookie_value)
    return session.get("role") == "admin"
