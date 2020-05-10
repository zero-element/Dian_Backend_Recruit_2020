from app import jwt
from flask import jsonify, g
from flask_jwt_extended import get_jwt_claims


@jwt.user_claims_loader
def add_claims(user):
    return {'country': g.country}


@jwt.user_identity_loader
def add_identity(user):
    return user.id


@jwt.claims_verification_loader
def verify_country(claims):
    if claims['country'] == g.country:
        return True
    else:
        return False


@jwt.invalid_token_loader
def invalid_token_callback(reason):
    print('invalid')
    return jsonify({'msg': '没有操作权限', 'reason': reason}), 401


@jwt.unauthorized_loader
def unauthorized_callback(reason):
    return jsonify({'msg': '没有操作权限', 'reason': reason}), 401


@jwt.claims_verification_failed_loader
def invalid_claims_callback():
    return jsonify({'msg': '没有操作权限', 'reason': 'Wrong country'}), 401
