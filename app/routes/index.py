from flask import Blueprint

router = Blueprint('index', __name__)


@router.route("/", methods=['GET'])
def home():
    return {'success': True}
