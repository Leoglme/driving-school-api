from app import create_app
from flask_mail import Mail

app = create_app()
app.app_context().push()
mail = Mail(app)

if __name__ == '__main__':
    app.debug = True
    app.run(host='localhost', port=5000)
