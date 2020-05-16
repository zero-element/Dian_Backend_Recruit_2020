NO_AUTH = {'status': 403, 'error': '没有操作权限'}
NO_USER = {'status': 404, 'error': '用户不存在'}
NO_POST = {'status': 404, 'error': '文章不存在'}
NO_COMMENT = {'status': 404, 'error': '评论不存在'}
NO_FILE = {'status': 404, 'error': '文件不存在'}
NO_TAG = {'status': 404, 'error': '标签不存在'}
NO_IMG = {'status': 404, 'error': '图片不存在'}
NO_CATEGORY = {'status': 404, 'error': '分类不存在'}
NO_DB = {'status': 404, 'msg': '数据库不存在'}

EXISTED_USERNAME = {'status': 403, 'error': '用户已存在'}

ILLEGAL_TYPE = {'status': 403, 'error': '文件类型非法'}
ILLEGAL_USERNAME = {'status': 403, 'error': '用户名无效'}
ILLEGAL_PASSWORD = {'status': 403, 'error': '密码无效'}
ILLEGAL_CONTENT = {'status': 403, 'error': '内容不能为空'}
ILLEGAL_CONTENT_TOLONG = {'status': 403, 'error': '内容过长'}
ILLEGAL_TITLE = {'status': 403, 'error': '标题不能为空'}
ILLEGAL_JWT = {'status': 401, 'error': 'token无效'}

EXPIRED_JWT = {'status': 401, 'error': 'token已过期'}

ERROR_AUTH = {'status': 403, 'error': '用户名或密码错误'}
ERROR_COUNTRY = {'status': 401, 'error': '国家或地区错误'}

FAIL_UPLOAD = {'status': 500, 'error': '上传失败'}
