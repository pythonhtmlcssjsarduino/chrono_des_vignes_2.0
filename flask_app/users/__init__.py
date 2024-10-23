from flask import Blueprint, redirect, flash, render_template, request
from flask_login import login_required, current_user, login_user, logout_user
from flask_app.models import User, Event, Parcours, Inscription, Edition
from flask_app.users.forms import Login_form, Signup_form, Inscription_connected_form, Inscription_form, ModifyForm
from flask_app import db, set_route, lang_url_for as url_for
from sqlalchemy import and_, not_
from datetime import datetime
import string, secrets
from flask_babel import _
alphabet = string.ascii_letters + string.digits

users = Blueprint('users', __name__, template_folder='templates')

@set_route(users, '/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = Login_form()
    ic(form.password.data)
    if form.validate_on_submit():
        user= User.query.filter_by(username=form.username.data).first()
        if user and form.password.data == user.password:
            login_user(user)
            flash(_('flash.connected:name').format(name = user.name), 'success')
            if request.args.get('next'):
                return redirect(request.args.get('next'))
            else:
                #if user.admin:
                #    return redirect(url_for('admin.home_event', event_name='course des vignes'))
                return redirect(url_for('home'))
        else:
            flash(_('flash.error.pwdnotvalid'), 'warning')
    return render_template('login.html', form=form)

@set_route(users, '/signup', methods=['POST', 'GET'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = Signup_form()
    if form.validate_on_submit():
        hash_pwd=form.password.data
        user = User(name=form.name.data,
                    lastname=form.lastname.data,
                    username=form.username.data,
                    email=form.email.data if form.email.data else None,
                    phone=form.phone.data if form.phone.data else None,
                    datenaiss= form.datenaiss.data,
                    password=hash_pwd)
        db.session.add(user)
        db.session.commit()
        flash(_('flash.accountcreated'), 'success')
        login_user(user)
        return redirect(url_for('home'))
    return render_template('signup.html', form=form)

@set_route(users, '/logout')
@login_required
def logout():
    logout_user()
    flash(_('flash.deconected'), 'success')
    return redirect(url_for('home'))

@set_route(users, '/<event>/edition/<edition>/inscription', methods=['POST', 'GET'])
def inscription_page(event, edition):
    user = current_user if current_user.is_authenticated else None
    event = Event.query.filter_by(name=event).first_or_404()
    edition:Edition = event.editions.filter_by(name=edition).first_or_404()
    if edition.first_inscription > datetime.now():
        date = edition.first_inscription.strftime('%A %d %B %Y')
        # pas encore ouvert
        flash(_('flash.warn.inscriptionsnotopen:date').format(date=date), 'warning')
        return redirect(url_for("view.view_edition_page", event = event.name, edition=edition.name))
    if edition.last_inscription < datetime.now():
        # deja fermé
        flash(_('flash.warn.inscriptionclosed'), 'warning')
        return redirect(url_for("view.view_edition_page", event = event.name, edition=edition.name))

    if user:
        form = Inscription_connected_form()
        choices = edition.parcours.filter( not_(Parcours.inscriptions.any(and_(Inscription.inscrit==user, Inscription.edition==edition))), Parcours.event==event).all()
        form.parcours.choices = [str((p.name, p.description)) for p in choices]

        if form.validate_on_submit():
            choices = event.parcours.filter(Parcours.name.in_([eval(data)[0] for data in form.parcours.data])).all()

            inscriptions = []
            for parcours in choices:
                inscriptions.append(Inscription(user_id = user.id,
                                                event_id=event.id,
                                                edition_id=edition.id,
                                                parcours_id=parcours.id))
            db.session.add_all(inscriptions)
            db.session.commit()

            return redirect(url_for('home'))

    else:
        form = Inscription_form()
        choices = edition.parcours
        form.parcours.choices = [str((p.name, p.description)) for p in choices]

        if form.validate_on_submit():
            hash_pwd= 'dev' #! ''.join(secrets.choice(alphabet) for _ in range(10))
            username=f'{form.name.data}.{form.lastname.data}'
            nb = User.query.filter(User.username.contains(username)).count()
            username += str(nb) if nb>0 else ''
            user = User(name=form.name.data,
                        lastname=form.lastname.data,
                        username=username,
                        email=form.email.data if form.email.data else None,
                        phone=form.phone.data if form.phone.data else None,
                        datenaiss= form.datenaiss.data,
                        password=hash_pwd,)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            print(user, form.parcours.data)
            choices = event.parcours.filter(Parcours.name.in_([eval(data)[0] for data in form.parcours.data])).all()

            inscriptions = []
            for parcours in choices:
                inscriptions.append(Inscription(user_id = user.id,
                                                event_id=event.id,
                                                edition_id=edition.id,
                                                parcours_id=parcours.id))
            print(inscriptions)
            db.session.add_all(inscriptions)
            db.session.commit()

            return redirect(url_for('home'))

    return render_template('inscription.html', user_data=user, event_data=event, edition_data=edition, form=form)

@set_route(users, '/profil')
@login_required
def profil():
    user = current_user
    return render_template('profil.html', user_data=user)

@set_route(users, '/profil/update', methods=['get', 'post'])
@login_required
def modify_profil():
    user = current_user
    form:ModifyForm = ModifyForm(data={'name':user.name,
                            'lastname':user.lastname,
                            'username':user.username,
                            'email':user.email,
                            'phone':user.phone,
                            'datenaiss':user.datenaiss})
    if form.validate_on_submit():
        if form.username.data == user.name or not User.query.filter_by(name=form.username.data).first():
            # le nom peut etre utilisé
            user.name=form.name.data
            user.lastname=form.lastname.data
            user.username=form.username.data
            user.email=form.email.data if form.email.data else None
            user.phone=form.phone.data if form.phone.data else None
            user.datenaiss= form.datenaiss.data
            db.session.commit()
            flash('name saved', 'success')
            return redirect(url_for('users.profil'))
        else:
            form.username.errors = list(form.username.errors)+['ce nom d\'utilisateur est déjà utilisé.']

    return render_template('modify_profil.html', user_data=user, form=form)
