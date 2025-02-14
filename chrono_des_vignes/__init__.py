from flask import Flask, redirect, flash, request, session, url_for, render_template
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
# met la langue en francais pour le formatage des dates
import locale
locale.setlocale(locale.LC_TIME,'')

DEFAULT_PROFIL_PIC = 'icone.png'
DEV_ENABLE = True
LANGAGES = ['de', 'fr', 'en']
if DEV_ENABLE:
    LANGAGES += ['ids', 'pseudo']
PICTURE_SIZE = (200, 200)

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
        if not current_user.admin:
            flash(_('flash.error.mustadmin'), 'danger')
            return redirect(url_for('home'))
        if not current_user.creations.filter_by(name=kwargs.get('event_name')).first():
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
    return dict(_=gettext, url_for=lang_url_for, now=datetime.now())

def set_route(blueprint, path, **options):
    def decorator(func):
        @blueprint.route(path, **options)
        @blueprint.route(f'/<lang>{path}', **options)
        @wraps(func)
        def wrap(*args, **kwargs):
            lang = kwargs.pop('lang', 'fr')
            if lang in LANGAGES:
                session['lang'] = lang
            return func(*args, **kwargs)
        return wrap
    
    return decorator

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