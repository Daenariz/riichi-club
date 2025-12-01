import os ##
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


#def create_app():
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = "home.login"

#    from app import routes ### statt routes.py haben wir __init__.py
 ##   from flask_hello import models

from .blueprints.home import home_bp

app.register_blueprint(home_bp)

from . import models ##
from flask import render_template

@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors.html", error="Page not found"), 404

# return app
