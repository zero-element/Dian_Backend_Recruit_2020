from flask import Flask, request, jsonify, redirect, g
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from sqlalchemy.orm import sessionmaker

import os
from datetime import datetime
from contextlib import contextmanager
from app.config.error import NO_DB

login_manager = LoginManager()
db = SQLAlchemy()
jwt = JWTManager()
sessions = {}
os.chdir(os.path.join(os.getcwd(), 'app'))
img_path = os.path.join(os.getcwd(), 'static', 'img')

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
    app.register_blueprint(api.v1_router, url_prefix='/api/v1')
    app.register_blueprint(api.img_router, url_prefix='/img')
    register_before_request(app)
    register_error(app)
    register_index(app)

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

def register_index(app):
    @app.route('/')
    def index():
        return app.send_static_file('index.html') # history模式的vue前端

def register_before_request(app):
    @app.before_request
    def before_request():
        country = request.args.get('blog_type') or 'china'
        if not country in sessions:
            return jsonify(NO_DB)
        g.country = country

def register_error(app):
    # 前端使用vue的history路由
    @app.errorhandler(404)
    def not_found_error(error):	
        return redirect('/', code=302)
        
    @app.errorhandler(500)	
    def internal_error(error):
        return jsonify({'status': 500, 'msg': '操作失败'})