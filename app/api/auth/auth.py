from .. import auth_router
from flask import request, jsonify, g
from app import get_session
from flask_jwt_extended import create_access_token, jwt_required
from app.models.database import Users
from app.libs import utils
# todo 表单验证
@auth_router.route('/login', methods=['POST'])


def login():
    json = request.get_json()
    username = json.get('username')
    password = json.get('password')
    if username is None or len(username) > 16:
        return jsonify({'msg': '用户名无效'}), 403
    if password is None or not(8 <= len(password) <= 16):
        return jsonify({'msg': '密码无效'}), 403
    with get_session() as session:
        user = session.query(Users).filter_by(
            username=username, password=utils.get_hash(password)).first()
        if user is not None:
            token = create_access_token(user)
            return jsonify({'msg': '登录成功', 'token': token}), 200
        else:
            return jsonify({'msg': '用户名或密码错误'}), 401


@auth_router.route('/register', methods=['POST'])
def register():
    json = request.get_json()
    username = json.get('username')
    password = json.get('password')
    if username is None or len(username) > 16:
        return jsonify({'msg': '用户名无效'}), 403
    if password is None or not(8 <= len(password) <= 16):
        return jsonify({'msg': '密码无效'}), 403
    with get_session(g.country) as session:
        user = session.query(Users).filter_by(username=username).first()
        if user is None:
            new_user = Users(username=username,
                             password=utils.get_hash(password))
            session.add(new_user)
            return jsonify({'msg': '注册成功'}), 200
        else:
            return jsonify({'msg': '用户已存在'}), 401
