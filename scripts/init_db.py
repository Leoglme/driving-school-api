import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app import create_app, db
from app.models.User import User
from app.models.Role import Role
from app.models.Meet import Meet
from app.seeders.role import add_roles
from app.seeders.user import add_users
from app.seeders.meet import add_meets

app = create_app()

with app.app_context():
    print("🚀 Initialisation de la base...")
    db.create_all()

    # Seed si vide
    if not Role.query.first():
        print("➡️ Insertion des rôles")
        add_roles(standalone_mode=False)

    if not User.query.first():
        print("➡️ Insertion des utilisateurs")
        add_users.callback(count=50)

    if not Meet.query.first():
        print("➡️ Insertion des rendez-vous")
        add_meets.callback(count=500)

    print("✅ Base de données initialisée avec succès")
