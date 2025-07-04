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
from icecream import install
from flask_babel import Babel, lazy_gettext, gettext, _
from flask_socketio import SocketIO
from flask_bcrypt import Bcrypt
import os, logging, json
from logging.handlers import SMTPHandler
from dotenv import load_dotenv
from datetime import datetime
install()
load_dotenv()
from urllib.parse import quote
from werkzeug import exceptions
#from sentry_sdk import init
#from sentry_sdk.integrations.flask import FlaskIntegration
# met la langue en francais pour le formatage des dates
import locale
locale.setlocale(locale.LC_TIME,'')

app = Flask(__name__)
app.subdomain_matching = True
app.config['SERVER_NAME'] = os.getenv('SERVER_NAME')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') #! change that for deployment

password= os.environ.get('db_password')
username= os.environ.get('db_user')
hostname= os.environ.get('db_host')
databasename= os.environ.get('db_name')

url = f"mysql+pymysql://{username}:{quote(password)}@{hostname}/{databasename}"
app.config["SQLALCHEMY_DATABASE_URI"] = url
app.config['BABEL_TRANSLATION_DIRECTORIES'] = f'{app.root_path}/translations'
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.url_map.default_subdomain = ''
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_POOL_RECYCLE"] = 280

DEFAULT_PROFIL_PIC = 'icone.png'
LANGAGES = ['de', 'fr', 'en']
if app.debug:
    LANGAGES += ['ids', 'pseudo']
PICTURE_SIZE = (200, 200)

db = SQLAlchemy(app)

migrate = Migrate(app, db)

socketio = SocketIO(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

# ? error report
mail_host= tuple(json.loads(os.getenv('mail_host')))
from_addr= os.getenv('from_addr')
mail_token= os.getenv('mail_token')
to_addrs= json.loads(os.getenv('to_addrs'))
#ic(mail_host, from_addr, mail_token, to_addrs)

class MailFormatter(logging.Formatter):
    def format(self, record):
        #region
        try:    post_data = "\n\t".join([f'"{k}": "{v}"' if v else f'"{k}"' for k, v in request.get_json().items()])
        except: post_data = request.get_data() if request.get_data()!=b'' else ''
        args = "\n\t".join([f'"{k}": "{v}"' if v else f'"{k}"' for k, v in request.args.to_dict().items()])
        user = f"""\
username:   {current_user.username}
id:         {current_user.id}
name:       {current_user.name}""" if current_user.is_authenticated else "anonymous"
        message = f'''\
an error occurred in the chrono des vignes:

{record.message} - {record.levelname}
it occured on the {self.formatTime(record, "%A, %d %B %Y %H:%M:%S")}
[user]
{user}

[request]
url:    {request.url}
endpoint:{request.endpoint}
route:  {request.url_rule}
method: {request.method}
args:   {args}
post:   {post_data}

[traceback]
{record.exc_text}

        '''
        return message
        #endregion

smtp_handeler = SMTPHandler(mailhost=mail_host, fromaddr=to_addrs, toaddrs=to_addrs, subject='server error', credentials=(from_addr, mail_token))
smtp_handeler.setFormatter(MailFormatter())
smtp_handeler.setLevel(logging.WARNING)

app.logger.addHandler(smtp_handeler)

#? instansiate flask babel
if app.debug:
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

babel = Babel(app)
@babel.localeselector
def get_locale():
    # if a user is logged in, use the locale from the user settings
    #ic(session.get('lang'), request.accept_languages.best_match(LANGAGES))
    if session.get('lang') :
        return session['lang']
    # otherwise try to guess the language from the user accept
    # header the browser transmits.  We support de/fr/en in this
    # example.  The best match wins.
    return request.accept_languages.best_match(LANGAGES)

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
    if args[0].startswith('doc'):
        if lang == 'fr':
            lang = None
        url = url_for(*args, lang=lang, **kwargs)
        if url[-1]!='/':url+='/'
        return url
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
            lang = kwargs.pop('lang', None)
            #ic('hey', lang, path, func.__name__)
            if lang == None:
                lang = request.accept_languages.best_match(LANGAGES)
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
app.register_blueprint(users)
from chrono_des_vignes.admin import admin
app.register_blueprint(admin)
from chrono_des_vignes.view import view
app.register_blueprint(view)
if app.debug:
    from chrono_des_vignes.dev import dev
    app.register_blueprint(dev)
from chrono_des_vignes.livetrack import livetrack
app.register_blueprint(livetrack)
from chrono_des_vignes import routes