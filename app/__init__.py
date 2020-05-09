from flask import Flask, request, g
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker

from os import path
from datetime import datetime
from contextlib import contextmanager


login_manager = LoginManager()
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.secret')
    app.config.from_object('app.config.setting.database')
    #初始化db
    from .models import database
    db.init_app(app)
    with app.app_context():
        db.create_all(bind='china')
        db.create_all(bind='usa')
        database.Base.metadata.create_all(db.get_engine(bind='china'))
        database.Base.metadata.create_all(db.get_engine(bind='usa'))
    #初始化login
    from .models import auth
    login_manager.session_protection = 'strong'
    login_manager.init_app(app)
    #初始化router
    from . import api
    app.register_blueprint(api.auth_router, url_prefix='/auth')
    app.register_blueprint(api.v1_router, url_prefix='/v1')
    app.before_request(before)

    return app

@contextmanager
def session_maker(schema):
    try:
        engine = db.get_engine(bind=schema)
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

def before():
    country = request.args.get('blog_type') or 'china'
    g.country = country
    print(g.country)
