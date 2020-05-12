from .. import v1_router
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc, asc
from flask import request, jsonify
from app import get_session
from app.models.database import Users, Articles, Comments
from app.libs import utils


@v1_router.route('/comment/list/<int:article_id>', methods=['GET'])
def get_comment_list(article_id):
    limit = request.args.get('limit', type=int) or 10
    offset = request.args.get('offset', type=int) or 0
    order = request.args.get('order', type=int) or 0
    with get_session() as session:
        article = session.query(Articles).filter_by(
            id=article_id).one_or_none()
        if article is not None:
            count = session.query(Comments.id)\
                .filter_by(article_id=article_id, comment_level=1).count()
            comment_list = session.query(Comments).filter_by(article_id=article_id, comment_level=1)\
                                                  .order_by(desc(Comments.top_status),
                                                            desc(Comments.praise_num) if order else asc(Comments.create_time))\
                                                  .limit(limit).offset(limit*offset).all()
            return jsonify({'total': count, 'list': [{'cid': comment.id,
                                                      'username': utils.get_username(comment.user_id, session),
                                                      'content': comment.content,
                                                      'praise_num': comment.praise_num,
                                                      'top_status': comment.top_status,
                                                      'create_time': comment.create_time
                                                      }
                                                     for comment in comment_list]
                            }), 200
        else:
            return jsonify({'msg': '文章不存在'}), 404


@v1_router.route('/comment/reply/<int:comment_id>', methods=['GET'])
def get_comment_reply(comment_id):
    limit = request.args.get('limit', type=int) or 10
    offset = request.args.get('offset', type=int) or 0
    with get_session() as session:
        comment = session.query(Comments)\
                         .filter_by(id=comment_id).one_or_none()
        if comment is not None:
            count = session.query(Comments.id)\
                           .filter_by(parent_cid=comment_id, comment_level=2).count()
            comment_list = session.query(Comments).filter_by(parent_cid=comment_id, comment_level=2)\
                                  .limit(limit).offset(limit*offset).all()
            return jsonify({'total': count, 'list': [{'cid': comment.id,
                                                      'username': utils.get_username(comment.user_id, session),
                                                      'from_name': utils.get_username(comment.from_uid, session),
                                                      'content': comment.content,
                                                      'praise_num': comment.praise_num,
                                                      'create_time': comment.create_time
                                                      }
                                                     for comment in comment_list]
                            }), 200
        else:
            return jsonify({'msg': '评论不存在'}), 404

# 获取单个评论内容
# @v1_router.route('/comment/<int:comment_id>', methods=['GET'])
# def get_comment(comment_id):
#     with get_session() as session:
#         comment = session.query(Comments)\
#                          .filter_by(id=comment_id).one_or_none()
#         if comment is not None:
#             return jsonify({'cid': comment.id,
#                             'aid': comment.article_id,
#                             'username': utils.get_username(comment.user_id, session),
#                             'from_name': utils.get_username(comment.from_uid, session),
#                             'content': comment.content,
#                             'praise_num': comment.praise_num,
#                             'create_time': comment.create_time
#                             }), 200
#         else:
#             return jsonify({'msg': '评论不存在'}), 404


@v1_router.route('/comment/<int:article_id>', methods=['POST'])
@jwt_required
def create_comment(article_id):
    json = request.get_json()
    content = json.get('content')
    from_id = json.get('from_cid')
    if content is None:
        return jsonify({'msg': '内容不能为空'}), 403
    user_id = get_jwt_identity()

    with get_session() as session:
        article = session.query(Articles).filter_by(
            id=article_id).one_or_none()
        if article is None:
            return jsonify({'msg': '文章不存在'}), 404
        if from_id is not None:
            from_comment = session.query(Comments)\
                                  .filter_by(id=from_id).one_or_none()
            if from_comment is not None:
                new_comment = Comments(article_id=article_id,
                                       user_id=user_id,
                                       parent_uid=from_comment.parent_uid or from_comment.user_id,
                                       parent_cid=from_comment.parent_cid or from_comment.id,
                                       from_uid=from_comment.user_id,
                                       from_cid=from_comment.id,
                                       comment_level=2,
                                       content=content
                                       )
                session.add(new_comment)
            else:
                return jsonify({'msg': '评论不存在'}), 404
        else:
            new_comment = Comments(article_id=article_id,
                                   user_id=user_id,
                                   comment_level=1,
                                   content=content
                                   )
            session.add(new_comment)
        session.commit()
        return jsonify({'msg': '创建成功', 'cid': new_comment.id}), 200


@v1_router.route('/comment/<int:comment_id>', methods=['PUT'])
@jwt_required
def modify_comment(comment_id):
    json = request.get_json()
    content = json.get('content')
    if content is None:
        return jsonify({'msg': '内容不能为空'}), 403
    user_id = get_jwt_identity()

    with get_session() as session:
        comment = session.query(Comments)\
                         .filter_by(id=comment_id).one_or_none()
        if comment is not None:
            if user_id == comment.user_id:
                comment.content = content
                return jsonify({'msg': '修改成功'}), 200
            else:
                return jsonify({'msg': '没有操作权限'}), 403
        else:
            return jsonify({'msg': '评论不存在'}), 404


@v1_router.route('/comment/<int:comment_id>', methods=['DELETE'])
@jwt_required
def delete_comment(comment_id):
    user_id = get_jwt_identity()

    with get_session() as session:
        comment = session.query(Comments)\
                         .filter_by(id=comment_id).one_or_none()
        if comment is not None:
            if user_id == comment.user_id or user_id == comment.article.user_id:
                session.delete(comment)
                return jsonify({'msg': '删除成功'}), 200
            else:
                return jsonify({'msg': '没有操作权限'}), 403
        else:
            return jsonify({'msg': '评论不存在'}), 404


@v1_router.route('/comment/praise/<int:comment_id>', methods=['PUT'])
@jwt_required
def praise_comment(comment_id):
    with get_session() as session:
        comment = session.query(Comments)\
                         .filter_by(id=comment_id).one_or_none()
        if comment is not None:
            comment.praise_num = comment.praise_num + 1
            return jsonify({'msg': '点赞成功'}), 200
        else:
            return jsonify({'msg': '评论不存在'}), 404


@v1_router.route('/comment/top/<int:comment_id>', methods=['PUT'])
@jwt_required
def top_comment(comment_id):
    user_id = get_jwt_identity()

    with get_session() as session:
        comment = session.query(Comments)\
                         .filter_by(id=comment_id).one_or_none()
        if comment is not None:
            if user_id == comment.article.user_id:
                comment.top_status = not comment.top_status
                return jsonify({'msg': '操作成功'}), 200
            else:
                return jsonify({'msg': '没有操作权限'}), 403
        else:
            return jsonify({'msg': '评论不存在'}), 404
