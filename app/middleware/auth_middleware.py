from flask import request, jsonify, current_app
from functools import wraps
from ..models.User import User
import jwt


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        current_app.logger.info("Vérification du token dans token_required")
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].replace("Bearer ", "")
            current_app.logger.info(f"Token reçu : {token}")

        if not token:
            current_app.logger.error("Token manquant")
            return {
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized"
            }, 401

        try:
            secret_key = current_app.config.get('SECRET_KEY')
            if not secret_key:
                current_app.logger.error("SECRET_KEY non défini dans la configuration")
                return {
                    "message": "Configuration serveur incorrecte : clé secrète manquante",
                    "data": None,
                    "error": "Internal Server Error"
                }, 500
            current_app.logger.info(f"Clé secrète utilisée : {secret_key}")
            data = jwt.decode(token, secret_key, algorithms=["HS256"])
            current_app.logger.info(f"Token décodé : id={data['id']}")
            current_user = User.query.filter_by(id=data["id"]).first()
            if current_user is None:
                current_app.logger.error("Utilisateur non trouvé pour ce token")
                return {
                    "message": "Invalid Authentication token!",
                    "data": None,
                    "error": "Unauthorized"
                }, 401
        except Exception as e:
            current_app.logger.error(f"Erreur dans token_required : {str(e)}", exc_info=True)
            return {
                "message": "Something went wrong",
                "data": None,
                "error": str(e)
            }, 500

        current_app.logger.info(f"Utilisateur authentifié : {current_user.email}")
        return f(current_user, *args, **kwargs)

    return decorated