from flask import flash, redirect, url_for, render_template
from flask_app import app, db
from flask_app.forms import Login_form, Signup_form
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
    return render_template("0-home.html", user_data=user, inscriptions=inscriptions, events = next_events)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = Login_form()
    if form.validate_on_submit():
        user= User.query.filter_by(username=form.username.data).first()
        if user and form.password.data == user.password:
            login_user(user)
            flash(f'welcome {user.name} you are connected', 'success')
            if user.admin:
                return redirect(url_for('home_event', event_name='course des vignes'))
            return redirect(url_for('home'))
        else:
            flash('please retry')
    return render_template('2-login.html', form=form)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    form = Signup_form()
    if form.validate_on_submit():
        flash('valide')
    return render_template('3-signup.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('tu es bien déconnecté !', 'success')
    return redirect(url_for('home'))

@app.route('/view/<event>')
def view_event_page(event):
    return f'{event}'

@app.route('/view/<event>/<parcours>')
def view_parcours_page(event, parcours):
    return f'{event}, {parcours}'

#* import de admin routes
from flask_app import admin_routes
