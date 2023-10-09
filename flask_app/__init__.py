from flask import Flask, redirect, url_for, flash
from datetime import datetime
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"

db = SQLAlchemy()
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

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
            flash('tu doit être admin pour cet evenement pour acceder a cette page.', 'danger')
            return redirect(url_for('home'))
        return func(*args, **kwargs)
    return decorated_view

# defini les pages du site web
from flask_app import routes

#* erreur 403 acces non autorisé
def error403():
    flash('tu doit etre connecté pour acceder a cette page.', 'danger')
    return redirect(url_for('home'))
login_manager.unauthorized_handler(error403)

