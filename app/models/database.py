from flask_login import UserMixin
from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
# 创建对象的基类:
Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer(), nullable=False, primary_key=True)
    username = Column(String(20), nullable=False)
    passwd = Column(String(20), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

class Articles(Base):
    __tablename__ = 'articles'
    id = Column(Integer(), nullable=False, primary_key=True)
    title = Column(String(20), nullable=False)
    content = Column(String(20), nullable=False)
    user = Column(String(20), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.title


