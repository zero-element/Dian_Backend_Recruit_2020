import hashlib
from app.config import secret

def get_sha1(s):
    return hashlib.sha1(s.encode('utf-8')).hexdigest()

def get_hash(s):
    return get_sha1(secret.SALT + s)

def get_summary(s):
    return 'summary'