from .. import img_router
from flask import request, Response, jsonify, g
from app import get_session, img_path
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.database import Users
from app.libs import utils
from os import path
from PIL import Image
from io import BytesIO
from app.config.error import NO_USER, FAIL_UPLOAD, ILLEGAL_TYPE, NO_FILE

@img_router.route('/upload', methods=['POST'])
@jwt_required
def upload_img():
    f = request.files['file']
    user_id = get_jwt_identity()
    with get_session() as session:
        user = session.query(Users).filter_by(id=user_id).one_or_none()
        if user is not None:
            try:
                sImg = Image.open(f.stream)
                weith, height = sImg.size
                scale = max(weith, height) / 1000
                if scale > 1:
                    sImg = sImg.resize(
                        (int(weith/scale), int(height/scale)))
                type = utils.get_file_type(f.filename)
                if type is not None:
                    with BytesIO() as img_bytes:
                        sImg.save(img_bytes, format=type)
                        filename = "{}.{}".format(utils.get_file_sha1(img_bytes.getvalue()), type)
                        sImg.save(path.join(img_path, filename))
                        return jsonify({'status': 200, 'msg': '上传成功', 'path': f'img/{filename}'})
                else:
                    return jsonify(ILLEGAL_TYPE)
            except Exception:
                return jsonify(FAIL_UPLOAD)
        else:
            return jsonify(NO_USER)

# 查看图片 上线之后用nginx取代
@img_router.route('/<string:filename>', methods=['GET'])
def show_img(filename):
    file_path = path.join(img_path, filename)
    if path.isfile(file_path):
        with open(file_path, "rb") as file:
            image = file.read()
            mimetype = utils.get_mimetype(file_path)
            if mimetype and mimetype.startswith('image'):
                response = Response(image, mimetype=mimetype)
                return response
            else:
                return jsonify(ILLEGAL_TYPE)
    else:
        return jsonify(NO_FILE)
