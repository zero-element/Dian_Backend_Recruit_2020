from .. import auth_router
from flask import request, jsonify, g
from app import get_session
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_claims
from app.models.database import Users
from app.libs import utils
#todo 表单验证
@auth_router.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    with get_session() as session:
        user = session.query(Users).filter_by(username=username, password=utils.get_hash(password)).first()
        if user is not None:
            token = create_access_token(user)
            return jsonify({'msg': '登录成功', 'token': token}), 200
        else:
            return jsonify({'msg': '用户名或密码错误'}), 401

@auth_router.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    with get_session(g.country) as session:
        user = session.query(Users).filter_by(username=username).first()
        if user is None:
            new_user = Users(username=username, password=utils.get_hash(password))
            try:
                session.add(new_user)
                return jsonify({'msg': '注册成功'}), 200
            except:
                return jsonify({'msg': '系统错误'}), 500
        else:
            return jsonify({'msg': '用户已存在'}), 401
