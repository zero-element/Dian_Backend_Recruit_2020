from app import login_manager
from flask import jsonify
from app.models.database import Users

def nolog():
    return jsonify({'code': 403, 'msg': "没有操作权限"})


def load_user(user_id):
    return Users.query.get(int(user_id))