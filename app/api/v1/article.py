from .. import v1_router
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request, jsonify
from sqlalchemy import func
from app import get_session
from app.models.database import Users, Articles
from app.libs import utils


@v1_router.route('/article/list/<string:username>', methods=['GET'])
def get_article_list(username):
    limit = request.args.get('limit') or 10
    offset = request.args.get('offset') or 0
    with get_session() as session:
        user = session.query(Users).filter_by(username=username).one_or_none()
        if user is not None:
            count = session.query(func.count(Articles.id)).filter_by(
                author_id=user.id).scalar()
            article_list = session.query(Articles).filter_by(
                author_id=user.id).limit(limit).offset(offset).all()
            return jsonify({'total': count, 'list': [{'id': article.id,
                                                      'title': article.title,
                                                      'summary': article.summary or article.content,
                                                      }
                                                     for article in article_list]
                            }), 200
        else:
            return jsonify({'msg': '该用户不存在'}), 404


@v1_router.route('/article/<int:article_id>', methods=['GET'])
def get_article(article_id):
    with get_session() as session:
        article = session.query(Articles).filter_by(id=article_id).one_or_none()
        if article is not None:
            return jsonify({'id': article.id,
                            'title': article.title,
                            'content': article.content
                            }), 200
        else:
            return jsonify({'msg': '该文章不存在'}), 404


@v1_router.route('/article', methods=['POST'])
@jwt_required
def create_article():
    content = request.form.get('content')
    title = request.form.get('title')
    if content is None:
        return jsonify({'msg': '内容不能为空'}), 403
    if title is None:
        return jsonify({'msg': '标题不能为空'}), 403
    summary = utils.get_summary(content)
    user_id = get_jwt_identity()
    
    with get_session() as session:
        new_article = Articles(title=title, content=content, summary=summary, author_id=user_id)
        try:
            session.add(new_article)
            session.commit()
            return jsonify({'msg': '创建成功', 'id': new_article.id}), 200
        except:
            return jsonify({'msg': '系统错误'}), 500


@v1_router.route('/article/<int:article_id>', methods = ['PUT'])
@jwt_required
def modify_article(article_id):
    content = request.form.get('content')
    title = request.form.get('title')
    summary = utils.get_summary(content)
    user_id = get_jwt_identity()
    
    with get_session() as session:
        article=session.query(Articles).filter_by(id = article_id).one_or_none()
        if article is not None:
            if user_id == article.author_id:
                try:
                    article.title = title or article.title
                    article.content = content or article.content
                    article.summary = summary or article.summary
                    session.commit()
                    return jsonify({'msg': '修改成功'}), 200
                except:
                    return jsonify({'msg': '系统错误'}), 500
            else:
                return jsonify({'msg': '没有操作权限'}), 403
        else:
            return jsonify({'msg': '该文章不存在'}), 404


@v1_router.route('/article/<int:article_id>', methods = ['DELETE'])
@jwt_required
def delete_article(article_id):
    user_id = get_jwt_identity()

    with get_session() as session:
        article = session.query(Articles).filter_by(id = article_id).one_or_none()
        if article is not None:
            if user_id == article.author_id:
                try:
                    session.delete(article)
                    session.commit()
                    return jsonify({'msg': '删除成功'}), 200
                except:
                    return jsonify({'msg': '系统错误'}), 500
            else:
                return jsonify({'msg': '没有操作权限'}), 403
        else:
            return jsonify({'msg': '该文章不存在'}), 404
