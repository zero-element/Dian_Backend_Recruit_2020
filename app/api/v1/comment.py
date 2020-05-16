from .. import v1_router
from flask_jwt_extended import jwt_required, jwt_optional, get_jwt_identity
from sqlalchemy import desc, asc
from flask import request, jsonify
from app import get_session
from app.models.database import Users, Articles, Comments
from app.libs import utils
from app.config.error import NO_POST, NO_COMMENT, NO_AUTH, ILLEGAL_CONTENT, ILLEGAL_CONTENT_TOLONG

# 获取指定文章的一级评论列表
@v1_router.route('/article/<int:article_id>/comment/list/', methods=['GET'])
@jwt_optional
def get_comment_list(article_id):
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    sortby = request.args.get('sortby', 0, type=int)  # 0表点赞，1表时间
    order = request.args.get('order', sortby ^ 1, type=int)  # 默认时间升序或者点赞降序
    with get_session() as session:
        article = session.query(Articles).filter_by(
            id=article_id).one_or_none()
        if article is not None:
            count = session.query(Comments.id)\
                .filter_by(article_id=article_id, comment_level=1).count()
            sortby_ = Comments.create_time if sortby else Comments.praise_num
            order_ = desc if order else asc
            comment_list = session.query(Comments).filter_by(article_id=article_id, comment_level=1)\
                                                  .order_by(desc(Comments.top_status), order_(sortby_))\
                                                  .limit(limit).offset(limit*offset).all()
            user_id = get_jwt_identity()
            return jsonify({'status': 200, 'total': count, 'list': [{'cid': comment.id,
                                                                     'username': utils.get_username(comment.user_id, session),
                                                                     'content': comment.content_html,
                                                                     'reply_num': comment.reply_num,
                                                                     'praise_num': comment.praise_num,
                                                                     'top_status': comment.top_status,
                                                                     'create_time': comment.create_time,
                                                                     'auth_modify': comment.user_id == user_id,
                                                                     'auth_delete': comment.user_id == user_id or comment.article.user_id == user_id
                                                                     }
                                                                    for comment in comment_list]
                            })
        else:
            return jsonify(NO_POST)

# 获取指定评论的回复列表
@v1_router.route('/article/comment/<int:comment_id>/reply', methods=['GET'])
@jwt_optional
def get_comment_reply(comment_id):
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    with get_session() as session:
        comment = session.query(Comments)\
                         .filter_by(id=comment_id).one_or_none()
        if comment is not None:
            count = session.query(Comments.id)\
                           .filter_by(from_cid=comment_id).count()
            comment_list = session.query(Comments).filter_by(from_cid=comment_id)\
                                  .limit(limit).offset(limit*offset).all()
            user_id = get_jwt_identity()
            return jsonify({'status': 200,
                            'total': count, 'list': [{'cid': comment.id,
                                                      'username': utils.get_username(comment.user_id, session),
                                                      'from_name': utils.get_username(comment.from_uid, session),
                                                      'content': comment.content_html,
                                                      'praise_num': comment.praise_num,
                                                      'create_time': comment.create_time,
                                                      'auth_modify': comment.user_id == user_id,
                                                      'auth_delete': comment.user_id == user_id or comment.article.user_id == user_id
                                                      }
                                                     for comment in comment_list]
                            })
        else:
            return jsonify(NO_COMMENT)

# 获取评论内容（markdown）
@v1_router.route('/article/comment/<int:comment_id>/content', methods=['GET'])
@jwt_required
def get_comment_content(comment_id):
    user_id = get_jwt_identity()

    with get_session() as session:
        comment = session.query(Comments)\
                         .filter_by(id=comment_id).one_or_none()
        if comment is not None:
            if user_id == comment.user_id:
                return jsonify({'status': 200, 'content': comment.content})
            else:
                return jsonify(NO_AUTH)
        else:
            return jsonify(NO_COMMENT)

# 创建评论
@v1_router.route('/article/<int:article_id>/comment', methods=['POST'])
@jwt_required
def create_comment(article_id):
    json = request.get_json()
    content = json.get('content')
    from_id = json.get('from_cid')
    if content is None:
        return jsonify(ILLEGAL_CONTENT)
    if len(content) > 10000:
        return jsonify(ILLEGAL_CONTENT_TOLONG)
    user_id = get_jwt_identity()

    with get_session() as session:
        article = session.query(Articles)\
                         .filter_by(id=article_id).one_or_none()
        if article is None:
            return jsonify(NO_POST)
        if from_id is not None:
            # 对评论回复
            from_comment = session.query(Comments)\
                                  .filter_by(id=from_id).one_or_none()
            if from_comment is not None and from_comment.article_id == article_id:
                new_comment = Comments(article_id=article_id,
                                       user_id=user_id,
                                       parent_uid=from_comment.parent_uid or from_comment.user_id,
                                       parent_cid=from_comment.parent_cid or from_comment.id,
                                       from_uid=from_comment.user_id,
                                       from_cid=from_comment.id,
                                       comment_level=2,
                                       content=content
                                       )
                from_comment.reply_num += 1
                session.add(new_comment)
            else:
                return jsonify(NO_COMMENT)
        else:
            # 对文章回复
            new_comment = Comments(article_id=article_id,
                                   user_id=user_id,
                                   comment_level=1,
                                   content=content
                                   )
            session.add(new_comment)
        session.commit()
        return jsonify({'status': 200, 'msg': '创建成功', 'cid': new_comment.id})

# 修改评论
@v1_router.route('/article/comment/<int:comment_id>', methods=['PUT'])
@jwt_required
def modify_comment(comment_id):
    json = request.get_json()
    content = json.get('content')
    if content is None:
        return jsonify(ILLEGAL_CONTENT)
    user_id = get_jwt_identity()

    with get_session() as session:
        comment = session.query(Comments)\
                         .filter_by(id=comment_id).one_or_none()
        if comment is not None:
            if user_id == comment.user_id:
                comment.content = content
                return jsonify({'status': 200, 'msg': '修改成功'})
            else:
                return jsonify(NO_AUTH)
        else:
            return jsonify(NO_COMMENT)

# 删除评论
@v1_router.route('/article/comment/<int:comment_id>', methods=['DELETE'])
@jwt_required
def delete_comment(comment_id):
    user_id = get_jwt_identity()

    with get_session() as session:
        comment = session.query(Comments)\
                         .filter_by(id=comment_id).one_or_none()
        if comment is not None:
            # 是否具有删除权限
            if user_id == comment.user_id or user_id == comment.article.user_id:
                # 是否是一级评论
                if comment.comment_level == 1:
                    # 一级评论则删除所有子评论
                    session.query(Comments)\
                           .filter_by(parent_cid=comment_id).delete()
                else:
                    # 否则父评论数量-1
                    parent_comment = session.query(Comments).filter_by(id=comment.parent_cid)
                    parent_comment.reply_num -= 1
                session.delete(comment)
                return jsonify({'status': 200, 'msg': '删除成功'})
            else:
                return jsonify(NO_AUTH)
        else:
            return jsonify(NO_COMMENT)

# 点赞评论
@v1_router.route('/article/comment/<int:comment_id>/praise', methods=['POST'])
@jwt_required
def praise_comment(comment_id):
    with get_session() as session:
        comment = session.query(Comments)\
                         .filter_by(id=comment_id).one_or_none()
        if comment is not None:
            comment.praise_num = comment.praise_num + 1
            return jsonify({'status': 200, 'msg': '操作成功'})
        else:
            return jsonify(NO_COMMENT)

# 置顶/取消置顶评论
@v1_router.route('/article/comment/<int:comment_id>/top', methods=['POST'])
@jwt_required
def top_comment(comment_id):
    user_id = get_jwt_identity()

    with get_session() as session:
        comment = session.query(Comments)\
                         .filter_by(id=comment_id).one_or_none()
        if comment is not None:
            if user_id == comment.article.user_id:
                # 状态取反
                comment.top_status = not comment.top_status
                return jsonify({'status': 200, 'msg': '操作成功'})
            else:
                return jsonify(NO_AUTH)
        else:
            return jsonify(NO_COMMENT)
