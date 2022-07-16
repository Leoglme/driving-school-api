from flask import Blueprint

router = Blueprint('router', __name__)


@router.route("/", methods=['GET'])
def home():
    return {'success': True}
