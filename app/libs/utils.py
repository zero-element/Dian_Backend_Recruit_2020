import hmac
import hashlib
import mimetypes
from app.config import secret
from app.models.database import Users, Articles, Comments
from app import get_session
from os import path
from werkzeug.utils import secure_filename

def hmac_sha1(key:str, s:str):
    return hmac.new(key.encode('utf-8'), s.encode('utf-8'), 'SHA1').hexdigest()

def get_hash(s:str):
    return hmac_sha1(s, secret.SALT)

def get_file_sha1(file:bytes):
    return hashlib.sha1(file).hexdigest()

def get_summary(s:str):
    if '<!--more-->' in s:
        return s.split('<!--more-->')[0]
    else:
        return s

def get_username(uid:int, session):
    user = session.query(Users).filter_by(id=uid).one_or_none()
    if user is not None:
        return user.username
    else:
        return ''

def get_mimetype(filename:str):
    return mimetypes.guess_type(filename)[0]

def get_file_type(filename:str):
    _, type = path.splitext(secure_filename(filename))
    type = type.lower()[1:]
    ALLOWED_EXTENSIONS = set(['png', 'jpeg', 'jpg', 'gif', 'bmp'])
    if type in ALLOWED_EXTENSIONS:
        type = 'jpeg' if type=='jpg' else type
        return type
    else:
        return None
