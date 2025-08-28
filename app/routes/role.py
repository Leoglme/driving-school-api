from ..enums.role import Role
from flask import jsonify, Blueprint
from ..middleware.auth_middleware import token_required

router = Blueprint('role', __name__)


# Get all roles
@router.route('/roles', methods=['GET'])
@token_required
def index_roles(current_user):
    roles = []
    for i in Role:
        roles.append({
            'id': i.value,
            'name': i.name
        })
        if current_user.role == i:
            break
    return jsonify(roles)
