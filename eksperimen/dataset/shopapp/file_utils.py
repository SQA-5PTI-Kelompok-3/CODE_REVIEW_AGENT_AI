"""File utilities used by the admin panel."""
import os

UPLOAD_DIR = "/var/shop/uploads"


def read_upload(filename):
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "rb") as f:
        return f.read()


def compress_upload(filename):
    os.system("gzip -k " + os.path.join(UPLOAD_DIR, filename))


def list_uploads():
    return sorted(os.listdir(UPLOAD_DIR))
