from .. import v1_router
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request, jsonify
from app import get_session
from app.models.database import Users, Articles, Tags, Categories, Article_tags
from app.libs import utils
from app.config.error import NO_USER, NO_TAG, NO_CATEGORY

# 获取用户标签列表
@v1_router.route('/user/<string:username>/tag/list/', methods=['GET'])
def get_user_tag(username):
    with get_session() as session:
        user = session.query(Users).filter_by(username=username).one_or_none()
        if user is not None:
            tags = session.query(Tags).filter_by(user_id=user.id)
            return jsonify({'status': 200, 'tags': [tag.tag for tag in tags]})
        else:
            return jsonify(NO_USER)


# 获取标签对应文章列表
@v1_router.route('/user/<string:username>/tag/<string:tag>', methods=['GET'])
def get_tag_article(username, tag):
    with get_session() as session:
        user = session.query(Users).filter_by(username=username).one_or_none()
        if user is not None:
            tag = session.query(Tags).filter_by(user_id=user.id, tag=tag).one_or_none()
            if tag is not None:
                articles = tag.articles
                count = len(articles)
                return jsonify({'total': count, 'list': [{'aid': article.id,
                                                        'title': article.title,
                                                        'creat_time': article.create_time
                                                        }
                                                        for article in articles]         
                                }), 200
            else:
                return jsonify(NO_TAG)
        else:
            return jsonify(NO_USER)


# 获取用户分类列表
@v1_router.route('/user/<string:username>/category/list/', methods=['GET'])
def get_user_category(username):
    with get_session() as session:
        user = session.query(Users).filter_by(username=username).one_or_none()
        if user is not None:
            categories = session.query(Categories).filter_by(user_id=user.id)
            return jsonify({'status': 200, 'tags': [category.category for category in categories if category.category]})
        else:
            return jsonify(NO_USER)


# 获取分类对应文章列表
@v1_router.route('/user/<string:username>/category/<string:category>', methods=['GET'])
def get_category_article(username, category):
    with get_session() as session:
        user = session.query(Users).filter_by(username=username).one_or_none()
        if user is not None:
            category = session.query(Categories).filter_by(user_id=user.id, category=category).one_or_none()
            if category is not None:
                articles = category.articles
                count = len(articles)
                return jsonify({'status': 200, 'total': count, 'list': [{'aid': article.id,
                                                        'title': article.title,
                                                        'creat_time': article.create_time
                                                        }
                                                        for article in articles]         
                                })
            else:
                return jsonify(NO_CATEGORY)
        else:
            return jsonify(NO_USER)
