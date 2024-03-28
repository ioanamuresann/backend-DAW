from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app.controllers import auth_bp
app.register_blueprint(auth_bp)

from app.controllers import destinatie_bp
app.register_blueprint(destinatie_bp)

if __name__ == '__main__':
    app.run(debug=True)