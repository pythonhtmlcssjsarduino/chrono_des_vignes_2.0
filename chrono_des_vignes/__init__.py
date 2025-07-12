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

import json
import locale
import logging
import os
from datetime import datetime
from functools import wraps
from logging.handlers import SMTPHandler
from typing import Any, Callable, ParamSpec, TypeVar, cast, Final, override
from urllib.parse import quote
from flask.typing import ResponseReturnValue
from flask_babel import Babel, _, gettext
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from icecream import install
from werkzeug import exceptions
from werkzeug.wrappers.response import Response
from flask import (
    Blueprint,
    Flask,
    abort,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from dotenv import load_dotenv
install()
load_dotenv()
# met la langue en francais pour le formatage des dates

locale.setlocale(locale.LC_TIME, "")

app = Flask(__name__)
app.subdomain_matching = True
app.config["SERVER_NAME"] = os.getenv("SERVER_NAME")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")  #! change that for deployment

password = quote(cast(str, os.environ.get("db_password")))
username = os.environ.get("db_user")
hostname = os.environ.get("db_host")
databasename = os.environ.get("db_name")

url = f"mysql+pymysql://{username}:{password}@{hostname}/{databasename}"
app.config["SQLALCHEMY_DATABASE_URI"] = url
app.config["BABEL_TRANSLATION_DIRECTORIES"] = f"{app.root_path}/translations"
app.jinja_env.add_extension("jinja2.ext.loopcontrols")
app.url_map.default_subdomain = ""
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_POOL_RECYCLE"] = 280

DEFAULT_PROFIL_PIC:Final[str] = "icone.png"
LANGAGES:Final[tuple[str,...]] = ("de", "fr", "en")
if app.debug:
    LANGAGES += ("ids", "pseudo")  # pyright: ignore[reportConstantRedefinition, reportGeneralTypeIssues]
PICTURE_SIZE:Final[tuple[int, int]] = (200, 200)

class Base(DeclarativeBase, MappedAsDataclass):  # pyright: ignore[reportUnsafeMultipleInheritance]
  pass

db = SQLAlchemy(app, model_class=Base)

migrate = Migrate(app, db)

socketio = SocketIO(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "users.login"
login_manager.login_message_category = "info"

# ? error report
mail_host = cast(str, json.loads(cast(str, os.getenv("mail_host"))))
from_addr = cast(str, os.getenv("from_addr"))
mail_token = cast(str, os.getenv("mail_token"))
to_addrs = cast(str, json.loads(cast(str, os.getenv("to_addrs"))))
# ic(mail_host, from_addr, mail_token, to_addrs)


class MailFormatter(logging.Formatter):
    @override
    def format(self, record: logging.LogRecord) -> str:
        # region
        try:
            post_data = "\n\t".join(
                [
                    f'"{k}": "{v}"' if v else f'"{k}"'
                    for k, v in request.get_json().items()  # pyright: ignore[reportAny]
                ]
            )
        except:  # noqa: E722
            post_data = str(request.get_data() if request.get_data() != b"" else "")
        args = "\n\t".join(
            [
                f'"{k}": "{v}"' if v else f'"{k}"'
                for k, v in request.args.to_dict().items()
            ]
        )
        user = (
            f"""\
username:   {current_user.username}
id:         {current_user.id}
name:       {current_user.name}"""
            if current_user.is_authenticated
            else "anonymous"
        )
        message = f"""\
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

        """
        return message
        # endregion


smtp_handeler = SMTPHandler(
    mailhost=mail_host,
    fromaddr=to_addrs,
    toaddrs=to_addrs,
    subject="server error",
    credentials=(from_addr, mail_token),
)
smtp_handeler.setFormatter(MailFormatter())
smtp_handeler.setLevel(logging.WARNING)

app.logger.addHandler(smtp_handeler)

# ? instansiate flask babel
if app.debug:
    old = ".venv/Lib/site-packages/babel/locale-data/fr_CH.dat"
    new = (
        ".venv/Lib/site-packages/babel/locale-data/pseudo.dat",
        ".venv/Lib/site-packages/babel/locale-data/ids.dat",
    )
    for file in new:
        if not os.path.exists(file):
            with open(old, "rb") as file1:
                with open(file, "+wb") as file2:
                    file2.write(file1.read())

    from babel.core import LOCALE_ALIASES

    LOCALE_ALIASES["pseudo"] = "pseudo"
    LOCALE_ALIASES["ids"] = "ids"

def get_locale() -> str:
    # if a user is logged in, use the locale from the user settings
    # ic(session.get('lang'), request.accept_languages.best_match(LANGAGES))
    if session.get("lang"):  # pyright: ignore[reportUnknownMemberType]
        return cast(str, session["lang"])
    # otherwise try to guess the language from the user accept
    # header the browser transmits.  We support de/fr/en in this
    # example.  The best match wins.
    return request.accept_languages.best_match(LANGAGES, default="en")

babel = Babel(app, locale_selector=get_locale)

from chrono_des_vignes.models import User  # noqa: E402

@login_manager.user_loader
def load_user(user_id: str):
    return db.session.query(User).filter_by(id=user_id).first()

param = ParamSpec("param")
ret = TypeVar("ret")

def admin_required(func: Callable[param, ret]) -> Callable[param, ret | Response]:
    """
    Modified login_required decorator to restrict access to admin group.
    """

    @wraps(func)
    def decorated_view(*args: param.args, **kwargs: param.kwargs) -> ret | Response:
        # ic(current_user, current_user.admin, args, kwargs)
        if not current_user.admin:
            flash(_("flash.error.mustadmin"), "danger")
            return redirect(url_for("home"))
        if (
            kwargs.get("event_name")
            and not current_user.creations.filter_by(
                name=kwargs.get("event_name")
            ).first()
        ):
            flash(_("flash.error.wrongadminevent"), "danger")
            return redirect(url_for("home"))
        return func(*args, **kwargs)

    return decorated_view


def lang_url_for(*args: Any, **kwargs: Any) -> str:
    if "static" in args or kwargs.get("lang"):
        return url_for(*args, **kwargs)
    lang:str|None = _("app.lang")
    if args[0].startswith("doc"):
        if lang == "fr":
            lang = None
        url = url_for(*args, lang=lang, **kwargs)
        if url[-1] != "/":
            url += "/"
        return url
    if lang == request.accept_languages.best_match(LANGAGES):
        return url_for(*args, **kwargs)
    return url_for(*args, lang=lang, **kwargs)


@app.context_processor
def jinja_context():
    return dict(
        _=gettext,
        url_for=lang_url_for,
        now=datetime.now(),
        date=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
    )


routeP = ParamSpec("routeP")
routeR = TypeVar("routeR", bound=ResponseReturnValue)
def set_route(
    blueprint: Flask | Blueprint, path: str, **options: Any
) -> Callable[..., Callable[routeP, routeR]]:
    def decorator(func: Callable[routeP, routeR])->Callable[routeP, routeR]:
        @blueprint.route(f"/<lang>{path}", **options)
        @blueprint.route(path, **options)
        @wraps(func)
        def wrap(*args: routeP.args, **kwargs: routeP.kwargs):
            lang = kwargs.pop("lang", None)
            # ic('hey', lang, path, func.__name__)
            if lang is None:
                lang = request.accept_languages.best_match(LANGAGES)
            if lang not in LANGAGES:
                return abort(404)
            session["lang"] = lang
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
def http_error(error: exceptions.HTTPException) -> Response:
    html = render_template("error/simple_error.html", error=error)
    return make_response(html, error.code)

# ? end error Handling

# defini les pages du site web
from chrono_des_vignes.users import users  # noqa: E402

app.register_blueprint(users)
from chrono_des_vignes.admin import admin  # noqa: E402

app.register_blueprint(admin)
from chrono_des_vignes.view import view  # noqa: E402

app.register_blueprint(view)
if app.debug:
    from chrono_des_vignes.dev import dev

    app.register_blueprint(dev)
from chrono_des_vignes.livetrack import livetrack  # noqa: E402

app.register_blueprint(livetrack)
from chrono_des_vignes import routes  # noqa: E402, F401  # pyright: ignore[reportUnusedImport]
