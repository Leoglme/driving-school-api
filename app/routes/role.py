from .index import router
from ..enums.role import Role
from flask import jsonify


# Get all roles
@router.route('/roles', methods=['GET'])
def index_roles():
    roles = []
    for i in Role:
        roles.append({
            'id': i.value,
            'name': i.name
        })
    return jsonify(roles)
