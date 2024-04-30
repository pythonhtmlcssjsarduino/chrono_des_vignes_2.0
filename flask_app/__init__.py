from flask import Flask, redirect, url_for, flash
from datetime import datetime
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from flask_colorpicker import colorpicker

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key' #! change that for deployment
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"

db = SQLAlchemy()
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

colorpicker(app)

from flask_app.models import User
@login_manager.user_loader
def load_user(user_id:str ):
    return User.query.filter_by(id=user_id).first()


def admin_required(func):
    """
    Modified login_required decorator to restrict access to admin group.
    """

    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.admin:
            flash('tu doit être admin pour acceder a cette page.', 'danger')
            return redirect(url_for('home'))
        if not current_user.creations.filter_by(name=kwargs.get('event_name')).first():
            flash('tu doit être admin de cet evenement pour acceder a cette page.', 'danger')
            return redirect(url_for('home'))
        return func(*args, **kwargs)
    return decorated_view

#* erreur 403 acces non autorisé
def error403():
    flash('tu doit etre connecté pour acceder a cette page.', 'danger')
    return redirect(url_for('home'))
login_manager.unauthorized_handler(error403)

# defini les pages du site web
from flask_app.users import users
from flask_app.admin import admin
from flask_app.view import view
app.register_blueprint(users)
app.register_blueprint(admin)
app.register_blueprint(view)
from flask_app import routes

