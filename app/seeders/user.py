from pathlib import Path
import sys

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

fake = Faker()


# RUN CLI COMMAND: python app/seeders/user.py --count=50

@click.command()
@click.option('--count', default=20, help='number of users to be generated')
def add_users(count):
    with app.app_context():
        emails = [fake.unique.safe_email() for _ in range(count)]
        for i in range(0, count):
            email = emails[i]
            email = email
            password = generate_password_hash("password")
            first_name = fake.first_name()
            last_name = fake.last_name()
            role = random.randint(1, 3)
            avatar = avatars.robohash(email, size='80')

            with app.app_context():
                user = User(email=email, password=password, first_name=first_name, last_name=last_name, role=role,
                            avatar=avatar)
                print(email)
                db.session.add(user)
                db.session.commit()

        return click.echo('{} users were added successfully to the database.'.format(count))


if __name__ == '__main__':
    add_users()
