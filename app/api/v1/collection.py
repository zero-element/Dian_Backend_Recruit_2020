from .. import v1_router
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request, jsonify
from app import get_session
from app.models.database import Users, Articles, Tags, Categories, Article_tags
from app.libs import utils

# 获取用户标签列表
@v1_router.route('/tag/list/<string:username>', methods=['GET'])
def get_user_tag(username):
    with get_session() as session:
        user = session.query(Users).filter_by(username=username).one_or_none()
        if user is not None:
            tags = session.query(Tags).filter_by(user_id=user.id)
            return jsonify({'tags': [tag.tag for tag in tags]}), 200
        else:
            return jsonify({'msg': '用户不存在'}), 404
            


# 获取标签对应文章列表
@v1_router.route('/tag/<string:tag>', methods=['GET'])
def get_tag_article(tag):
    username = request.args.get('username', type=str)

    with get_session() as session:
        user = session.query(Users).filter_by(username=username).one_or_none()
        if user is not None:
            tag = session.query(Tags).filter_by(user_id=user.id).filter_by(tag=tag).one_or_none()
            if tag is not None:
                articles = tag.articles
                print(articles)
            else:
                return jsonify({'msg': '标签不存在'})
        else:
            return jsonify({'msg': '用户不存在'}), 404





@v1_router.route('/category/list<int:article_id>', methods=['GET'])
def get_article_category(article_id):
    with get_session() as session:
        article = session.query(Articles).filter_by(
            id=article_id).one_or_none()
        if article is not None:
            return jsonify({'category': article.category}), 200
        else:
            return jsonify({'msg': '文章不存在'}), 404


@v1_router.route('/category/<string:article_id>', methods=['PUT'])
@jwt_required
def modify_article_category(article_id):
    json = request.get_json()
    if not 'category' in json:
        return jsonify({'msg': '分类不能为空'}), 403
    category = json['category']
    if type(category) is not str:
        return jsonify({'msg': '分类不能为空'}), 403
    user_id = get_jwt_identity()

    with get_session() as session:
        article = session.query(Articles).filter_by(
            id=article_id).one_or_none()
        if article is not None:
            if user_id == article.user_id:
                session.merge(Categories(category=category))
                article.category_ = session.query(Categories).filter_by(
                    category=category).one_or_none()
                session.commit()
                return jsonify({'category': article.category}), 200
            else:
                return jsonify({'msg': '没有操作权限'}), 403
        else:
            return jsonify({'msg': '文章不存在'}), 404
