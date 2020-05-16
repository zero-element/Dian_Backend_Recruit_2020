from app import jwt
from flask import jsonify, g
from flask_jwt_extended import get_jwt_claims
from app.config.error import ILLEGAL_JWT, ERROR_COUNTRY, EXPIRED_JWT

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
    return jsonify(ILLEGAL_JWT)


@jwt.unauthorized_loader
def unauthorized_callback(reason):
    return jsonify(ILLEGAL_JWT)


@jwt.claims_verification_failed_loader
def invalid_claims_callback():
    return jsonify(ERROR_COUNTRY)

@jwt.expired_token_loader
def expired_callback():
    return jsonify(EXPIRED_JWT)