from flask import g
from sqlalchemy import (
    Table, Column, String, Integer, Boolean, DateTime, and_,
    UnicodeText, ForeignKey, ForeignKeyConstraint, UniqueConstraint, create_engine)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import event
from datetime import datetime
from app import get_session
from markdown import markdown
import bleach
# 初始化Model的基类:
Base = declarative_base()

# tag和article属于多对多，使用中间表连接两者
Article_tags = Table('article_tags', Base.metadata,
                     Column('article_id',
                            ForeignKey('articles.id', ondelete='CASCADE'),
                            primary_key=True),
                     Column('user_id', primary_key=True),
                     Column('tag', primary_key=True),
                     ForeignKeyConstraint(['tag', 'user_id'], [
                                          'tags.tag', 'tags.user_id'])
                     )


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
    content_html = Column(UnicodeText, nullable=False)
    summary = Column(UnicodeText)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    create_time = Column(DateTime, default=datetime.now)
    modify_time = Column(DateTime)
    author = relationship('Users', backref='articles')
    tags = relationship('Tags',
                        secondary=Article_tags,
                        backref='articles')
    category = Column(String(30), ForeignKey('categories.category'))
    category_ = relationship('Categories', backref='articles',
                             primaryjoin="Articles.category==Categories.category and Articles.user_id==Categories.user_id")

    __table_args__ = (
        ForeignKeyConstraint(
            ['category', 'user_id'],
            ['categories.category', 'categories.user_id']
        ),
    )

    def __repr__(self):
        return '<Article %r>' % self.title


class Comments(Base):
    __tablename__ = 'comments'
    id = Column(Integer, nullable=False, primary_key=True)
    article_id = Column(Integer, ForeignKey(
        'articles.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, nullable=False)
    parent_uid = Column(Integer)
    parent_cid = Column(Integer)
    from_uid = Column(Integer)
    from_cid = Column(Integer)
    comment_level = Column(Integer, nullable=False, default=1)
    praise_num = Column(Integer, nullable=False, default=0)
    top_status = Column(Boolean, nullable=False, default=False)
    content = Column(UnicodeText, nullable=False)
    content_html = Column(UnicodeText, nullable=False)
    create_time = Column(DateTime, default=datetime.now)
    article = relationship('Articles')

    def __repr__(self):
        return '<Comment %r>' % self.id


class Tags(Base):
    __tablename__ = 'tags'

    tag = Column(String(30), nullable=False, primary_key=True)
    user_id = Column(Integer, nullable=False, primary_key=True)

    def __repr__(self):
        return '<Tag %r>' % self.tag


class Categories(Base):
    __tablename__ = 'categories'

    category = Column(String(30), primary_key=True)
    user_id = Column(Integer, nullable=False, primary_key=True)

    def __repr__(self):
        return '<category %r>' % self.category

# 自动删除article未使用的tag，tag为column，监听remove
@event.listens_for(Articles.tags, 'remove')
def delete_tag(mapper, connection, target):
    if len(connection.articles) == 0:
        g.session.delete(connection)

# 自动删除article未使用的category，category为obj，监听set
@event.listens_for(Articles.category_, 'set')
def delete_category(target, value, oldvalue, initiator):
    # category修改时只对应一篇article，修改后需要删除
    if oldvalue and value != oldvalue and len(oldvalue.articles) == 1:
        g.session.delete(oldvalue)

# 删除文章时自动删除article未使用的tag和category
@event.listens_for(Articles, 'after_delete')
def delete_orphan_delete(mapper, connection, target):
    article = target
    if article.category_ and len(article.category_.articles) == 0:
        g.session.delete(target.category_)
    for tag in article.tags:
        if len(tag.articles) == 0:
            g.session.delete(tag)

@event.listens_for(Articles.content, 'set')
@event.listens_for(Comments.content, 'set')
def generate_html(target, value, oldvalue, initiator):
    allow_tags = [
        'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li',
        'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p', 'img'
    ]
    target.content_html = bleach.linkify(
        bleach.clean(
            markdown(value, output_form='html'),
            tags=allow_tags,
            strip=True,
            attributes={
                '*': ['class'],
                'a': ['href', 'rel'],
                'img': ['src', 'alt'],  #支持<img src …>标签和属性
            }))
