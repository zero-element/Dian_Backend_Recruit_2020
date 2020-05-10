from flask_login import UserMixin
from sqlalchemy import (
    Column, String, Integer, DateTime, UnicodeText, ForeignKey, create_engine)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
# 初始化Model的基类:
Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, nullable=False, primary_key=True)
    username = Column(String(20), nullable=False)
    password = Column(String(64), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username


class Articles(Base):
    __tablename__ = 'articles'
    id = Column(Integer, nullable=False, primary_key=True)
    title = Column(String(100), nullable=False)
    content = Column(UnicodeText, nullable=False)
    summary = Column(UnicodeText)
    author_id = Column(Integer, ForeignKey('users.id'))
    create_time = Column(DateTime, default=datetime.now)
    # author = relationship('Users', backref='articles')

    def __repr__(self):
        return '<Article %r>' % self.title

