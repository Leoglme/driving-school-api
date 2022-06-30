from pathlib import Path
import sys

path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))
from app import db, create_app
import random
import click
from faker import Faker

app = create_app()
from werkzeug.security import generate_password_hash
from app.models.User import User
from app.services.rand import random_email, random_char

fake = Faker()


# RUN CLI COMMAND: python app/seeders/user.py --count=50

@click.command()
@click.option('--count', default=20, help='number of users to be generated')
def add_users(count):
    print('ADD USER')
    for i in range(0, count):
        email = random_email()
        password = generate_password_hash("password")
        first_name = random_char()
        last_name = random_char()
        role = random.randint(1, 3)

        with app.app_context():
            user = User(email=email, password=password, first_name=first_name, last_name=last_name, role=role)
            print(email)
            db.session.add(user)
            db.session.commit()

    return click.echo('{} users were added successfully to the database.'.format(count))


if __name__ == '__main__':
    add_users()
