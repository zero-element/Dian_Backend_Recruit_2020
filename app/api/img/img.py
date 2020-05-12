from .. import img_router
from flask import request, Response, jsonify, g
from app import get_session
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.database import Users
from app.libs import utils
from os import path, getcwd
from werkzeug.utils import secure_filename
from PIL import Image
from io import BytesIO

upload_path = path.join(getcwd(), 'static\\img')


@img_router.route('/', methods=['POST'])
@jwt_required
def upload_img():
    f = request.files['file']
    user_id = get_jwt_identity()
    with get_session() as session:
        user = session.query(Users).filter_by(id=user_id).one_or_none()
        if user is not None:
            filename = utils.get_file_name(
                secure_filename(f.filename), user.username)
            if filename is not None:
                try:
                    sImg = Image.open(f.stream)
                    weith, height = sImg.size
                    scale = max(weith, height) / 1000
                    if scale > 1:
                        sImg = sImg.resize((int(weith/scale), int(height/scale)))
                    sImg.save(path.join(upload_path, filename))
                    return jsonify({'msg': '上传成功', 'path': f'img/{filename}'}), 200
                except Exception:
                    return jsonify({'msg': '上传失败'}), 500

            else:
                return jsonify({'msg': '不支持此类型文件'}), 403
        else:
            return jsonify({'msg': '用户不存在'}), 404

# 查看图片 上线之后用nginx取代
@img_router.route('/<string:filename>', methods=['GET'])
def show_img(filename):
    file_path = path.join(upload_path, filename)
    if path.isfile(file_path):
        with open(file_path, "rb") as file:
            image = file.read()
            mimetype = utils.get_mimetype(file_path)
            if mimetype and mimetype.startswith('image'):
                response = Response(image, mimetype=mimetype)
                return response
            else:
                return jsonify({'msg': '非法的文件类型'}), 403
    else:
        return jsonify({'msg': '文件不存在'}), 404
