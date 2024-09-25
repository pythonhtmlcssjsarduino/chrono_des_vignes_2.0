from flask import render_template, request, session, redirect
from flask_app import app, LANGAGES, set_route
from flask_login import current_user
from flask_app.models import Edition, Inscription, Event
from sqlalchemy import and_
from datetime import datetime
from flask_babel import gettext, force_locale, get_locale, lazy_gettext



@set_route(app, '/')
def home():
    # * home page of the web site
    if current_user.is_authenticated:
        user = current_user
        inscriptions = Inscription.query.filter(Inscription.inscrit==user, Inscription.edition.has(Edition.edition_date>datetime.now())).all()
    else:
        user = None
        inscriptions = None
    date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    next_events = Event.query.filter(Event.editions.any(and_(Edition.edition_date>=date,Edition.last_inscription>=date))).all()
    return render_template("0-home.html", user_data=user, inscriptions=inscriptions, events = next_events, time = date)

@app.route('/lang/<lang>/<path:next>')
def change_lang(lang, next:str):
    lang_index = next.find(app.config['SERVER_NAME']) + len(app.config['SERVER_NAME'])
    first = next[lang_index+1:].split('/')[0]
    if first in LANGAGES:
        if lang == request.accept_languages.best_match(LANGAGES):
            return redirect(f'{next[:lang_index]}{next[lang_index+len(lang)+1:]}')
        else:
            return redirect(f'{next[:lang_index]}/{lang}{next[lang_index+len(lang)+1::]}')
    else:
        if lang == request.accept_languages.best_match(LANGAGES):
            return redirect(next)
        else:
            return redirect(f'{next[:lang_index]}/{lang}{next[lang_index:]}')
