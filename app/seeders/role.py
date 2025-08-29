from pathlib import Path
import sys

path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))
from app import db, create_app
import click
from faker import Faker

app = create_app()
from app.models.Role import Role

fake = Faker()


# RUN CLI COMMAND: python app/seeders/role.py
@click.command()
def add_roles():
    roles = ['student', 'instructor', 'secretary', 'admin']

    for role in roles:
        with app.app_context():
            role = Role(name=role)
            db.session.add(role)
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                raise

    return click.echo('roles were added successfully to the database.')


if __name__ == '__main__':
    add_roles()
