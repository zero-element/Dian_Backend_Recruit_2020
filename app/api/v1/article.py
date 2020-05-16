from .. import v1_router
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request, jsonify
from sqlalchemy import and_
from app import get_session
from app.models.database import Users, Articles, Tags, Categories
from app.libs import utils
from datetime import datetime
from app.config.error import NO_AUTH, NO_POST, NO_USER, ILLEGAL_CONTENT, ILLEGAL_TITLE

# 获取文章列表
@v1_router.route('/user/<string:username>/article/list/', methods=['GET'])
def get_article_list(username):
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    search = request.args.get('search', '', type=str)
    with get_session() as session:
        user = session.query(Users).filter_by(username=username).one_or_none()
        if user is not None:
            word_list = [f'%{keyword}%' for keyword in search.split(' ')]
            rule = and_(*[Articles.content.like(w) for w in word_list])
            count = session.query(Articles.id).filter_by(
                user_id=user.id).filter(rule).count()
            article_list = session.query(Articles).filter_by(user_id=user.id).filter(rule)\
                                  .limit(limit).offset(limit*offset).all()
            return jsonify({'status': 200, 'total': count, 'list': [{'aid': article.id,
                                                                     'title': article.title,
                                                                     'summary': article.summary_html,
                                                                     'creat_time': article.create_time,
                                                                     'modify_time': article.modify_time,
                                                                     'PV': article.PV,
                                                                     'tags': [tag.tag for tag in article.tags],
                                                                     'category': article.category
                                                                     }
                                                                    for article in article_list]
                            })
        else:
            return jsonify(NO_USER)


# 获取文章内容（markdown）
@v1_router.route('/article/content/<int:article_id>', methods=['GET'])
@jwt_required
def get_article_content(article_id):
    user_id = get_jwt_identity()

    with get_session() as session:
        article = session.query(Articles)\
                         .filter_by(id=article_id).one_or_none()
        if article is not None:
            if user_id == article.user_id:
                return jsonify({'status': 200,
                                'title': article.title,
                                'content': article.content,
                                'tags': [tag.tag for tag in article.tags],
                                'category': article.category
                                })
            else:
                return jsonify(NO_AUTH)
        else:
            return jsonify(NO_POST)

# 获取文章详情
@v1_router.route('/article/detail/<int:article_id>', methods=['GET'])
def get_article_detail(article_id):
    with get_session() as session:
        article = session.query(Articles)\
                         .filter_by(id=article_id).one_or_none()
        if article is not None:
            article.PV += 1
            return jsonify({'status': 200,
                            'aid': article.id,
                            'author': utils.get_username(article.user_id, session),
                            'title': article.title,
                            'content': article.content_html,
                            'creat_time': article.create_time,
                            'modify_time': article.modify_time,
                            'PV': article.PV,
                            'tags': [tag.tag for tag in article.tags],
                            'category': article.category
                            })
        else:
            return jsonify(NO_POST)

# 创建文章
@v1_router.route('/article', methods=['POST'])
@jwt_required
def create_article():
    json = request.get_json()
    content = json.get('content')
    title = json.get('title')
    tags = json.get('tags')
    category = json.get('category')
    if content is None:
        return jsonify(ILLEGAL_CONTENT)
    if title is None:
        return jsonify(ILLEGAL_TITLE)
    summary = utils.get_summary(content)
    user_id = get_jwt_identity()

    with get_session() as session:
        new_article = Articles(title=title, content=content,
                               summary=summary, user_id=user_id)
        for tag in tags:
            session.merge(Tags(tag=tag, user_id=user_id))
        new_article.tags = session.query(Tags)\
                                  .filter_by(user_id=user_id)\
                                  .filter(Tags.tag.in_(tags)).all()
        session.merge(Categories(category=category, user_id=user_id))
        new_article.category_ = session.query(Categories)\
                                       .filter_by(user_id=user_id, category=category).one_or_none()
        session.add(new_article)
        session.commit()
        return jsonify({'status': 200, 'msg': '创建成功', 'aid': new_article.id})


# 修改文章
@v1_router.route('/article/<int:article_id>', methods=['PATCH'])
@jwt_required
def modify_article(article_id):
    json = request.get_json()
    content = json.get('content')
    title = json.get('title')
    tags = json.get('tags')
    category = json.get('category')
    summary = utils.get_summary(content) if content else ''
    user_id = get_jwt_identity()

    with get_session() as session:
        article = session.query(Articles)\
                         .filter_by(id=article_id).one_or_none()
        if article is not None:
            if user_id == article.user_id:
                article.modidy_time = datetime.now
                article.title = title or article.title
                article.content = content or article.content
                article.summary = summary if content else article.summary
                if tags is not None and type(tags) == list:
                    article.tags = []
                    for tag in tags:
                        session.merge(Tags(tag=tag, user_id=user_id))
                    article.tags = session.query(Tags)\
                        .filter_by(user_id=user_id)\
                        .filter(Tags.tag.in_(tags)).all()
                if category is not None and type(category) == str:
                    session.merge(Categories(
                        category=category, user_id=user_id))
                    article.category_ = session.query(Categories)\
                        .filter_by(user_id=user_id, category=category).one_or_none()
                return jsonify({'status': 200, 'msg': '修改成功'})
            else:
                return jsonify(NO_AUTH)
        else:
            return jsonify(NO_POST)


# 删除文章
@v1_router.route('/article/<int:article_id>', methods=['DELETE'])
@jwt_required
def delete_article(article_id):
    user_id = get_jwt_identity()

    with get_session() as session:
        article = session.query(Articles)\
                         .filter_by(id=article_id).one_or_none()
        if article is not None:
            if user_id == article.user_id:
                session.delete(article)
                return jsonify({'status': 200, 'msg': '删除成功'})
            else:
                return jsonify(NO_AUTH)
        else:
            return jsonify(NO_POST)
