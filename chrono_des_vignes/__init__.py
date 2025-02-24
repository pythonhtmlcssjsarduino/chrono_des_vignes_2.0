'''
# Chrono Des Vignes
# a timing system for sports events
# 
# Copyright © 2024-2025 Romain Maurer
# This file is part of Chrono Des Vignes
# 
# Chrono Des Vignes is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# 
# Chrono Des Vignes is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with Foobar.
# If not, see <https://www.gnu.org/licenses/>.
# 
# You may contact me at chrono-des-vignes@ikmail.com
'''

from flask import Flask, redirect, flash, request, session, url_for, render_template, Blueprint, abort
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from functools import wraps
from flask_colorpicker import colorpicker
from icecream import install
from flask_babel import Babel, lazy_gettext, gettext, _
from flask_socketio import SocketIO
from sqlalchemy import URL
from flask_bcrypt import Bcrypt
import os
from dotenv import load_dotenv
from datetime import datetime
install()
load_dotenv()
from sqlalchemy import make_url
from werkzeug import exceptions
from sentry_sdk import init
from sentry_sdk.integrations.flask import FlaskIntegration
# met la langue en francais pour le formatage des dates
import locale
locale.setlocale(locale.LC_TIME,'')

app = Flask(__name__)
app.config['SERVER_NAME'] = 'localhost:5000'
password= os.environ.get('db_password')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') #! change that for deployment
url_object = URL.create(
    "mysql+pymysql",
    username="root",
    password=password,  # plain (unescaped) text
    host="localhost",
    database="site",
)
app.config["SQLALCHEMY_DATABASE_URI"] = url_object
app.config['BABEL_TRANSLATION_DIRECTORIES'] = f'{app.root_path}/translations'
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.url_map.default_subdomain = ''

DEFAULT_PROFIL_PIC = 'icone.png'
LANGAGES = ['de', 'fr', 'en']
if app.debug:
    LANGAGES += ['ids', 'pseudo']
PICTURE_SIZE = (200, 200)

if not app.debug:
    ic('init sentry')
    init(
        dsn=os.environ.get('SANTRY_DSN'),
        send_default_pii=True,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
        integrations=[FlaskIntegration(
            transaction_style='endpoint'
        )],
    )

db = SQLAlchemy(app)

migrate = Migrate(app, db)

socketio = SocketIO(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

colorpicker(app)

#? instansiate flask babel
old = '.venv/Lib/site-packages/babel/locale-data/fr_CH.dat'
new = ('.venv/Lib/site-packages/babel/locale-data/pseudo.dat', '.venv/Lib/site-packages/babel/locale-data/ids.dat')
for file in new:
    if not os.path.exists(file):
        with open(old, 'rb') as file1:
            with open(file, '+wb') as file2:
                file2.write(file1.read())

from babel.core import LOCALE_ALIASES
LOCALE_ALIASES['pseudo'] ='pseudo'
LOCALE_ALIASES['ids'] ='ids'


def get_locale():
    # if a user is logged in, use the locale from the user settings
    if session.get('lang') :
        return session['lang']
    # otherwise try to guess the language from the user accept
    # header the browser transmits.  We support de/fr/en in this
    # example.  The best match wins.
    return request.accept_languages.best_match(LANGAGES)

def get_timezone():
    pass

babel = Babel(app, locale_selector=get_locale, timezone_selector=get_timezone)

from chrono_des_vignes.models import User
@login_manager.user_loader
def load_user(user_id:str ):
    return User.query.filter_by(id=user_id).first()


def admin_required(func):
    """
    Modified login_required decorator to restrict access to admin group.
    """

    @wraps(func)
    def decorated_view(*args, **kwargs):
        #ic(current_user, current_user.admin, args, kwargs)
        if not current_user.admin:
            flash(_('flash.error.mustadmin'), 'danger')
            return redirect(url_for('home'))
        if kwargs.get('event_name') and not current_user.creations.filter_by(name=kwargs.get('event_name')).first():
            flash(_('flash.error.wrongadminevent'), 'danger')
            return redirect(url_for('home'))
        return func(*args, **kwargs)
    return decorated_view

def lang_url_for(*args, **kwargs):
    if 'static' in args or kwargs.get('lang'):
        return url_for(*args, **kwargs)
    lang = _('app.lang')
    if lang == request.accept_languages.best_match(LANGAGES):
        return url_for(*args, **kwargs)
    return url_for(*args, lang=lang, **kwargs)

@app.context_processor
def jinja_context():
    return dict(_=gettext, url_for=lang_url_for, now=datetime.now(), date=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))

def set_route(blueprint:Flask|Blueprint, path, **options):
    def decorator(func):
        @blueprint.route(f'/<lang>{path}', **options)
        @blueprint.route(path, **options)
        @wraps(func)
        def wrap(*args, **kwargs):
            lang = kwargs.pop('lang', 'fr')
            #ic('hey', lang, path, func.__name__)
            if lang not in LANGAGES:
                return abort(404)
            session['lang'] = lang
            return func(*args, **kwargs)
        return wrap
    
    return decorator

# ? error Handling

@app.errorhandler(exceptions.Forbidden)
@app.errorhandler(exceptions.InternalServerError)
@app.errorhandler(exceptions.MethodNotAllowed)
@app.errorhandler(exceptions.NotFound)
@app.errorhandler(exceptions.TooManyRequests)
@app.errorhandler(exceptions.ImATeapot)
def http_error(error:exceptions.HTTPException):
    return render_template('error/simple_error.html', error=error), error.code

# ? end error Handling

# defini les pages du site web
from chrono_des_vignes.users import users
from chrono_des_vignes.admin import admin
from chrono_des_vignes.view import view
from chrono_des_vignes.dev import dev
from chrono_des_vignes.livetrack import livetrack
app.register_blueprint(users)
app.register_blueprint(admin)
app.register_blueprint(view)
app.register_blueprint(dev)
app.register_blueprint(livetrack)
from chrono_des_vignes import routes