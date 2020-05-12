from flask import Flask, request, jsonify, g
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from sqlalchemy.orm import sessionmaker

import os
from datetime import datetime
from contextlib import contextmanager


login_manager = LoginManager()
db = SQLAlchemy()
jwt = JWTManager()
sessions = {}
os.chdir(os.path.join(os.getcwd(), 'app'))

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.secret')
    app.config.from_object('app.config.setting.database')
    #初始化db
    from .models import database
    db.init_app(app)
    with app.app_context():
        for country in app.config['SQLALCHEMY_BINDS']:
            db.create_all(bind=country)
            engine = db.get_engine(bind=country)
            # database.Base.metadata.drop_all(engine)
            database.Base.metadata.create_all(engine)
            DBSession = sessionmaker(bind=engine)
            sessions[country] = DBSession()
    #初始化login
    from .models import auth
    login_manager.session_protection = 'strong'
    login_manager.init_app(app)
    #初始化jwt
    jwt.init_app(app)
    #初始化router
    from . import api
    app.register_blueprint(api.auth_router, url_prefix='/auth')
    app.register_blueprint(api.v1_router, url_prefix='/v1')
    app.register_blueprint(api.img_router, url_prefix='/img')
    app.before_request(before)

    return app

@contextmanager
def get_session(schema=''):
    try:
        schema = schema or g.country
        g.session = sessions[schema]
        yield g.session
        g.session.commit()
    except:
        g.session.rollback()
        raise
    finally:
        g.session.close()

def before():
    country = request.args.get('blog_type') or 'china'
    if not country in sessions:
        return jsonify({'msg': '数据库不存在'}), 404
    g.country = country
