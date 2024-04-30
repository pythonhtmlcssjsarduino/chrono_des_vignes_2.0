from flask import flash, redirect, url_for, render_template
from flask_app import app, db
from flask_login import login_user, logout_user, login_required, current_user
from flask_app.models import Edition, User, Parcours, Inscription, Event
from sqlalchemy import and_
from datetime import datetime

@app.route('/')
def home():
    # * home page of the web site
    if current_user.is_authenticated:
        user = current_user
        inscriptions = Inscription.query.filter(Inscription.inscrit==user, Inscription.edition.has(Edition.edition_date>datetime.now())).all()
    else:
        user = None
        inscriptions = None
    next_events = Event.query.filter(Event.editions.any(and_(Edition.edition_date>datetime.now(),Edition.last_inscription<datetime.now()))).all()
    return render_template("0-home.html", user_data=user, inscriptions=inscriptions, events = next_events, time = datetime.now())


