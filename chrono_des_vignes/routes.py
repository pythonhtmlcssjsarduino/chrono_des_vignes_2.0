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

from flask import render_template, request, session, redirect, send_file, send_from_directory, url_for
from chrono_des_vignes import app, LANGAGES, set_route
from flask_login import current_user
from chrono_des_vignes.models import Edition, Inscription, Event, User
from sqlalchemy import and_
from datetime import datetime
from flask_babel import gettext, force_locale, get_locale, lazy_gettext
from chrono_des_vignes.admin import NewEventForm

@set_route(app, '/')
def home():
    # * home page of the web site
    if current_user.is_authenticated:
        user:User = current_user
        inscriptions = user.inscriptions.filter(Inscription.edition.has(Edition.edition_date>datetime.now())).all()
        participations = user.inscriptions.filter(Inscription.edition.has(Edition.edition_date<=datetime.now())).all()
        form = NewEventForm()
    else:
        user = None
        inscriptions = None
        participations = None
        form = None
    date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    next_events = Event.query.filter(Event.editions.any(and_(Edition.edition_date>=date,Edition.last_inscription>=date))).all()
    return render_template("0-home.html", user_data=user, inscriptions=inscriptions, events = next_events, participations=participations, form=form)

@app.route('/lang/<lang>')
def change_lang(lang):
    next = request.args.get('next')
    ic(next)
    ic(next.split('/')[1])
    next = next.split('/')
    if next[1] in LANGAGES:
        if lang==request.accept_languages.best_match(LANGAGES):
            next.pop(1)
        else:
            next[1]=lang
    else:
        if lang!=request.accept_languages.best_match(LANGAGES):
            next.insert(1, lang)
    next = '/'.join(next)
    ic(next)
    return redirect(next)

@app.route('/doc/<path:path>')
@app.route('/doc/')
def doc(path=''):
    return render_template('doc/site/index.html' if path == '' else f'doc/site/{path}index.html')

@app.route('/doc/assets/<path:path>')
def assets_doc_files(path):
    return doc_file('assets', path)

@app.route('/doc/search/<path:path>')
def search_doc_files(path):
    return doc_file('search', path)

def doc_file(dir, path:str):
    return send_from_directory(app.template_folder, f'doc/site/{dir}/{path}', download_name=path.split('/')[-1])

@app.route('/error')
def error():
    return 1/0