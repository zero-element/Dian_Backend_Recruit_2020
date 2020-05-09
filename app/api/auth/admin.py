from .. import auth_router
from flask import request, jsonify, g
from app.models.database import Users
from app import session_maker

@auth_router.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    passwd = request.form.get('passwd')
    with session_maker(g.country) as session:
        user = session.query(Users).filter_by(username=username, passwd=passwd).first()
        if user is not None:
            return jsonify({'code': 200, 'msg': '登录成功'})
        else:
            return jsonify({'code': 400, 'msg': '用户名或密码错误'})
    
@auth_router.route('/logout')
def logout():
    return jsonify({'code': 200, 'msg': '登出成功'})