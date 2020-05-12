from flask import Blueprint
auth_router = Blueprint('auth', __name__)
v1_router = Blueprint('v1', __name__)
img_router = Blueprint('img', __name__)

from . import auth
from . import v1
from . import img