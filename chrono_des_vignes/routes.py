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

from flask import render_template, request, redirect, send_from_directory, abort
from chrono_des_vignes import app, LANGAGES, set_route
from flask_login import current_user
from chrono_des_vignes.models import Edition, Inscription, Event
from sqlalchemy import and_
from datetime import datetime
from chrono_des_vignes.admin.form import NewEventForm
from werkzeug.wrappers.response import Response
from typing import cast, Any
import os

@set_route(app, '/')
def home()->str:
    # * home page of the web site
    if current_user.is_authenticated:
        user = current_user
        inscriptions = user.inscriptions.filter(Inscription.edition.has(Edition.edition_date>datetime.now())).all()
        participations = user.inscriptions.filter(Inscription.edition.has(Edition.edition_date<=datetime.now())).all()
        form = NewEventForm()
    else:
        user = None
        inscriptions = None
        participations = None
        form = None
    date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    next_events = Event.query.filter(Event.editions.any(and_(Edition.edition_date>=date,Edition.last_inscription>=date))).filter(Event.id!=1).all()
    return render_template("0-home.html", user_data=user, inscriptions=inscriptions, events = next_events, participations=participations, form=form)

@app.route('/lang/<lang>')
def change_lang(lang:str)->Response:
    next = request.args.get('next')
    next = next.split('/')#type: ignore
    if next[1] in LANGAGES:#type: ignore
        if lang==request.accept_languages.best_match(LANGAGES):
            next.pop(1)#type: ignore
        else:
            next[1]=lang#type: ignore
    else:
        if lang!=request.accept_languages.best_match(LANGAGES):
            next.insert(1, lang)#type: ignore
    next = '/'.join(next)#type: ignore
    return redirect(next)

@app.route('/doc/<path:path>')
@app.route('/doc/<lang>/<path:path>')
@app.route('/doc/')
def doc(path: str='', lang: str='')-> str:
    if not os.path.exists(os.path.join(app.root_path,cast(str, app.template_folder), 'doc/site/index.html' if path == '' else f'doc/site/{path}index.html')):
        return render_template('doc/site/404.html')
    lang=lang+"/" if lang else ""
    return render_template(f'doc/site/{lang}index.html' if path == '' else f'doc/site/{lang}{path}index.html')

@app.route('/doc/assets/<path:path>')
def assets_doc_files(path:str)->Any:
    return doc_file('assets', path)

@app.route('/doc/search/<path:path>')
def search_doc_files(path: str)->Any:
    return doc_file('search', path)

def doc_file(dir:str, path:str)->Any:
    if not os.path.exists(os.path.join(app.root_path,str(app.template_folder), f'doc/site/{dir}/{path}')): 
        return abort(404)
    return send_from_directory(str(app.template_folder), f'doc/site/{dir}/{path}', download_name=path.split('/')[-1])
