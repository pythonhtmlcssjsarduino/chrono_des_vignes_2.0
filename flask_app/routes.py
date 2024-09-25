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
    ic(lang, next)
    next=next.removeprefix('http://')
    ic(lang, next)
    ic('.'.join(next.split('.')[1:]), next.find(app.config['SERVER_NAME']))
    next = '.'.join(next.split('.')[1:]) if next.find(app.config['SERVER_NAME'])!=0 else next
    ic(lang, next)
    return redirect('http://'+lang+'.'+next)
