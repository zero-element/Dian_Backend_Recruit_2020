from .. import auth_router
from flask import request, jsonify, g
from app import get_session
from flask_jwt_extended import create_access_token, jwt_required
from app.models.database import Users
from app.libs import utils
from app.config.error import ILLEGAL_USERNAME, ILLEGAL_PASSWORD, ERROR_AUTH, EXISTED_USERNAME
import datetime


@auth_router.route('/login', methods=['POST'])
def login():
    json = request.get_json()
    username = json.get('username')
    password = json.get('password')
    if username is None or len(username) > 16:
        return jsonify(ILLEGAL_USERNAME)
    if password is None or not(6 <= len(password) <= 16):
        return jsonify(ILLEGAL_PASSWORD)
    with get_session() as session:
        user = session.query(Users)\
                      .filter_by(username=username, password=utils.get_hash(password)).first()
        if user is not None:
            # 有效期7天
            expires = datetime.timedelta(days=7)
            token = create_access_token(user, expires_delta=expires)
            return jsonify({'status': 200, 'msg': '登录成功',
                            'token': token,
                            'username': user.username,
                            'avatar': 'img/{}'.format(user.avatar)})
        else:
            return jsonify(ERROR_AUTH)


@auth_router.route('/register', methods=['POST'])
def register():
    json = request.get_json()
    username = json.get('username')
    password = json.get('password')
    # 用户名长度不得长于16位
    if username is None or len(username) > 16:
        return jsonify(ILLEGAL_USERNAME)
    # 密码长度在8-16位之间
    if password is None or not(8 <= len(password) <= 16):
        return jsonify(ILLEGAL_PASSWORD)
    with get_session(g.country) as session:
        user = session.query(Users).filter_by(username=username).first()
        if user is None:
            new_user = Users(username=username,
                             password=utils.get_hash(password))
            session.add(new_user)
            return jsonify({'status': 200, 'msg': '注册成功'})
        else:
            return jsonify(EXISTED_USERNAME)
