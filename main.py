from app import create_app
from flask_marshmallow import Marshmallow

app = create_app()
marsh = Marshmallow(app)
app.app_context().push()

if __name__ == '__main__':
    app.debug = True
    app.run(host='localhost', port=5000)
