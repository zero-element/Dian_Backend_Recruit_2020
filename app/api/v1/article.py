from .. import v1_router

@v1_router.route('/article', methods=['GET'])
def get_article():
    return "get"