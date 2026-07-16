import os  ##
from flask import Flask, request, current_app, render_template
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_babel import Babel


def get_locale():
    return request.accept_languages.best_match(current_app.config["LANGUAGES"])


# def create_app():
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = "home.login"
babel = Babel(app, locale_selector=get_locale)


@app.context_processor
def inject_locale():
    return dict(get_locale=get_locale)

#    from app import routes ### statt routes.py haben wir __init__.py
##   from flask_hello import models

from .blueprints.home import home_bp

app.register_blueprint(home_bp)

from . import models  ##


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors.html", error="Page not found"), 404


# return app
