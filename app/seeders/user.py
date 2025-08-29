from pathlib import Path
import sys

from flask import jsonify

path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))
from app import db, create_app
import random
import click
from faker import Faker
from flask_avatars import Avatars

app = create_app()
avatars = Avatars(app)

from werkzeug.security import generate_password_hash
from app.models.User import User
from app.models.DrivingTime import DrivingTime
from app.enums.role import Role

fake = Faker()


# RUN CLI COMMAND: python app/seeders/user.py --count=50

@click.command()
@click.option('--count', default=20, help='number of users to be generated')
def add_users(count):
    with app.app_context():
        # Add admin user with passwordNeedSet to False
        with app.app_context():
            user_admin_email = 'admin@driving-school.dibodev.fr'
            user = User(email=user_admin_email, password=generate_password_hash("password"), first_name='Léo', last_name='Guillaume', role=Role.Admin,
                        avatar=avatars.robohash(user_admin_email, size='80'), passwordNeedSet=False)
            db.session.add(user)
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                raise
            print(user_admin_email)

        emails = [fake.unique.safe_email() for _ in range(count)]
        for i in range(0, count):
            email = emails[i]
            email = email
            password = generate_password_hash("password")
            first_name = fake.first_name()
            last_name = fake.last_name()
            user_role = random.randint(1, 4)
            hours_done = random.randint(0, 10)
            hours_total = random.randint(10, 40)
            avatar = avatars.robohash(email, size='80')

            with app.app_context():
                user = User(email=email, password=password, first_name=first_name, last_name=last_name, role=user_role,
                            avatar=avatar)
                db.session.add(user)
                try:
                    db.session.commit()
                except Exception:
                    db.session.rollback()
                    raise
                if user.role == Role.Student:
                    driving_time = DrivingTime(hours_done=hours_done, hours_total=hours_total, user_id=user.id)
                    db.session.add(driving_time)

                try:
                    db.session.commit()
                except Exception:
                    db.session.rollback()
                    raise
                print(email)

        return click.echo('{} users were added successfully to the database.'.format(count))


if __name__ == '__main__':
    add_users()
