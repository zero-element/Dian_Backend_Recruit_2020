import hmac
from app.config import secret
from app.models.database import Users, Articles, Comments
from app import get_session
from os import path
import mimetypes

def hmac_sha1(key:str, s:str):
    return hmac.new(key.encode('utf-8'), s.encode('utf-8'), 'SHA1').hexdigest()

def get_hash(s:str):
    return hmac_sha1(s, secret.SALT)

def get_summary(s:str):
    if '<!--more-->' in s:
        return s.split(str='<!--more-->')[0]
    else:
        return s

def get_username(uid:int, session):
    user = session.query(Users).filter_by(id=uid).one_or_none()
    if user is not None:
        return user.username
    else:
        return ''


def get_reviewer_name(cid:int, session):
    with get_session() as session:
        comment = session.query(Comments).filter_by(id=cid).one_or_none()
        if comment is not None:
            return get_username(comment.user_id, session)
        else:
            return ''

def splite_filenam(filename:str):
    name, type = path.splitext(filename)
    type = type.lower()[1:]
    return name, type

def get_mimetype(filename:str):
    return mimetypes.guess_type(filename)[0]

def get_file_name(filename:str, username:str):
    name, type = splite_filenam(filename)
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif', 'bmp'])
    if type in ALLOWED_EXTENSIONS:
        return hmac_sha1(name, username) + '.' + type
    else:
        return None
