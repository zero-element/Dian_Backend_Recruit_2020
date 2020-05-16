from .. import v1_router
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request, jsonify
from app import get_session, img_path
from app.models.database import Users
from app.libs import utils
from werkzeug.utils import secure_filename
from os import path
from app.config.error import NO_IMG, NO_USER

# 获取用户列表
@v1_router.route('/user/list/', methods=['GET'])
def get_user_list():
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    with get_session() as session:
        count = session.query(Users.id).count()
        user_list = session.query(Users).limit(
            limit).offset(limit*offset).all()
        return jsonify({'status': 200, 'total': count, 'list': [{'username': user.username,
                                                                 'introduction': user.introduction_html,
                                                                 'avatar': 'img/{}'.format(user.avatar)
                                                                 }
                                                                for user in user_list]})

""" # 获取自身信息
@v1_router.route('/user/self', methods=['GET'])
@jwt_required
def get_self_info():
    user_id = get_jwt_identity()

    with get_session() as session:
        user = session.query(Users).filter_by(id=user_id).one_or_none()
        if user is not None:
            return jsonify({'status': 200,
                            'username': user.username,
                            'introduction': user.introduction_html,
                            'avatar': 'img/{}'.format(user.avatar)
                            })
        else:
            return jsonify(NO_USER) """

# 获取指定用户信息
@v1_router.route('/user/<string:username>/info', methods=['GET'])
def get_user_info(username):
    with get_session() as session:
        user = session.query(Users).filter_by(username=username).one_or_none()
        if user is not None:
            return jsonify({'status': 200, 'username': user.username,
                            'introduction': user.introduction_html,
                            'avatar': 'img/{}'.format(user.avatar)
                            })
        else:
            return jsonify(NO_USER)

# 修改用户头像
@v1_router.route('/user/avatar', methods=['PUT'])
@jwt_required
def modify_user_avatar():
    json = request.get_json()
    avatar_name = json.get('avatar_name', 'avatar.jpg')
    user_id = get_jwt_identity()

    with get_session() as session:
        user = session.query(Users).filter_by(id=user_id).one_or_none()
        if user is not None:
            avatar_name = secure_filename(avatar_name)
            avatar_path = path.join(img_path, avatar_name)
            if path.isfile(avatar_path):
                user.avatar = avatar_name
                return jsonify({'status': 200, 'msg': '修改成功'})
            else:
                return jsonify(NO_IMG)
        else:
            return jsonify(NO_USER)

# 获取个人介绍（markdown）
@v1_router.route('/user/introduction', methods=['GET'])
@jwt_required
def get_introduction_content():
    user_id = get_jwt_identity()

    with get_session() as session:
        user = session.query(Users).filter_by(id=user_id).one_or_none()
        if user is not None:
            return jsonify({'status': 200, 'content': user.introduction})
        else:
            return jsonify(NO_USER)


# 修改用户个人介绍
@v1_router.route('/user/introduction', methods=['PUT'])
@jwt_required
def modify_user_introduction():
    json = request.get_json()
    introduction = json.get('introduction', '')
    user_id = get_jwt_identity()

    with get_session() as session:
        user = session.query(Users).filter_by(id=user_id).one_or_none()
        if user is not None:
            user.introduction = introduction
            return jsonify({'status': 200, 'msg': '修改成功'})
        else:
            return jsonify(NO_USER)
