from .. import v1_router
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request, jsonify
from app import get_session
from app.models.database import Users, Articles, Tags, Categories
from app.libs import utils
from datetime import datetime

# 获取文章列表
@v1_router.route('/article/list/<string:username>', methods=['GET'])
def get_article_list(username):
    limit = request.args.get('limit', type=int) or 10
    offset = request.args.get('offset', type=int) or 0
    with get_session() as session:
        user = session.query(Users).filter_by(username=username).one_or_none()
        if user is not None:
            count = session.query(Articles.id).filter_by(
                user_id=user.id).count()
            article_list = session.query(Articles).filter_by(
                user_id=user.id).limit(limit).offset(limit*offset).all()
            return jsonify({'total': count, 'list': [{'aid': article.id,
                                                      'title': article.title,
                                                      'summary': article.summary or article.content,
                                                      'creat_time': article.create_time,
                                                      'modify_time': article.modify_time,
                                                      'tags': [tag.tag for tag in article.tags],
                                                      'category': article.category
                                                      }
                                                     for article in article_list]
                            }), 200
        else:
            return jsonify({'msg': '用户不存在'}), 404


# 获取文章详情
@v1_router.route('/article/<int:article_id>', methods=['GET'])
def get_article(article_id):
    with get_session() as session:
        article = session.query(Articles).filter_by(
            id=article_id).one_or_none()
        if article is not None:
            return jsonify({'aid': article.id,
                            'author': utils.get_username(article.user_id, session),
                            'title': article.title,
                            'content': article.content,
                            'creat_time': article.create_time,
                            'modify_time': article.modify_time,
                            'tags': [tag.tag for tag in article.tags],
                            'category': article.category
                            }), 200
        else:
            return jsonify({'msg': '文章不存在'}), 404

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
        return jsonify({'msg': '内容不能为空'}), 403
    if title is None:
        return jsonify({'msg': '标题不能为空'}), 403
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
        return jsonify({'msg': '创建成功', 'aid': new_article.id}), 200


# 修改文章
@v1_router.route('/article/<int:article_id>', methods=['PUT'])
@jwt_required
def modify_article(article_id):
    json = request.get_json()
    content = json.get('content', '')
    title = json.get('title', '')
    tags = json.get('tags', [])
    category = json.get('category', '')
    summary = utils.get_summary(content) if content else ''
    user_id = get_jwt_identity()

    with get_session() as session:
        article = session.query(Articles).filter_by(id=article_id).one_or_none()
        if article is not None:
            if user_id == article.user_id:
                article.modidy_time = datetime.now
                article.title = title or article.title
                article.content = content or article.content
                article.summary = summary or article.summary
                article.tags = []
                for tag in tags:
                    session.merge(Tags(tag=tag, user_id=user_id))
                article.tags = session.query(Tags)\
                                      .filter_by(user_id=user_id)\
                                      .filter(Tags.tag.in_(tags)).all()
                session.merge(Categories(category=category, user_id=user_id))
                article.category_ = session.query(Categories)\
                                           .filter_by(user_id=user_id, category=category).one_or_none()
                return jsonify({'msg': '修改成功'}), 200
            else:
                return jsonify({'msg': '没有操作权限'}), 403
        else:
            return jsonify({'msg': '文章不存在'}), 404


# 删除文章
@v1_router.route('/article/<int:article_id>', methods=['DELETE'])
@jwt_required
def delete_article(article_id):
    user_id = get_jwt_identity()

    with get_session() as session:
        article = session.query(Articles).filter_by(
            id=article_id).one_or_none()
        if article is not None:
            if user_id == article.user_id:
                session.delete(article)
                return jsonify({'msg': '删除成功'}), 200
            else:
                return jsonify({'msg': '没有操作权限'}), 403
        else:
            return jsonify({'msg': '文章不存在'}), 404
