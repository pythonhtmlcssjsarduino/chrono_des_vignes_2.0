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

from flask import Blueprint, redirect, flash, render_template, request, session
from flask_login import login_required, current_user, login_user, logout_user
from chrono_des_vignes.models import User, Event, Parcours, Inscription, Edition
from chrono_des_vignes import app, DEFAULT_PROFIL_PIC, PICTURE_SIZE, username
from .form import Login_form, Signup_form, Inscription_connected_form, Inscription_form, ModifyForm, ModifyPwdForm
from chrono_des_vignes import db, set_route, lang_url_for as url_for, bcrypt
from sqlalchemy import and_, not_
from datetime import datetime
import string
import secrets
import os
from flask_babel import _
from PIL import Image
from werkzeug.datastructures import FileStorage
from werkzeug.wrappers import Response
alphabet = string.ascii_letters + string.digits

users = Blueprint('users', __name__, template_folder='templates')

@set_route(users, '/login', methods=['POST', 'GET'])
def login()->str|Response:
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = Login_form()
    if form.validate_on_submit():
        user:User|None = db.session.query(User).filter_by(username=form.username.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash(_('flash.connected:name').format(name = user.name), 'success')
            if request.args.get('next'):
                return redirect(request.args['next'])
            else:
                return redirect(url_for('home'))
        else:
            flash(_('flash.error.pwdnotvalid'), 'warning')
    return render_template('login.html', form=form)

@set_route(users, '/signup', methods=['POST', 'GET'])
def signup()-> str|Response:
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = Signup_form()
    if form.validate_on_submit():
        hash_pwd= bcrypt.generate_password_hash(form.password.data).decode('utf-8')# type: ignore[arg-type]
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
def logout()-> str|Response:
    logout_user()
    flash(_('flash.deconected'), 'success')
    return redirect(url_for('home'))

@set_route(users, '/<event_name>/edition/<edition_name>/inscription', methods=['POST', 'GET'])
def inscription_page(event_name: str, edition_name: str)-> str|Response:
    user = current_user if current_user.is_authenticated else None
    event = Event.query.filter_by(name=event_name).first_or_404()
    edition:Edition = event.editions.filter_by(name=edition_name).first_or_404()
    if edition.first_inscription > datetime.now():
        date = edition.first_inscription.strftime('%A %d %B %Y')
        # pas encore ouvert
        flash(_('flash.warn.inscriptionsnotopen:date').format(date=date), 'warning')
        return redirect(url_for("view.view_edition_page", event_name = event.name, edition_name=edition.name))
    if edition.last_inscription < datetime.now():
        # deja fermé
        flash(_('flash.warn.inscriptionclosed'), 'warning')
        return redirect(url_for("view.view_edition_page", event_name = event.name, edition_name=edition.name))

    form:Inscription_connected_form|Inscription_form
    if user:
        form = Inscription_connected_form()
        choices = edition.parcours.filter( not_(Parcours.inscriptions.any(and_(Inscription.inscrit==user, Inscription.edition==edition))), Parcours.event==event).all()#type: ignore[no-untyped-call]
        form.parcours.choices = [str((p.name, p.description)) for p in choices]#type: ignore[misc]

        if form.validate_on_submit():
            choices = event.parcours.filter(Parcours.name.in_([eval(data)[0] for data in form.parcours.data])).all()#type: ignore[union-attr]

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
        form.parcours.choices = [str((p.name, p.description)) for p in choices]#type: ignore[misc]

        if form.validate_on_submit():
            pwd= form.password.data
            hash_pwd = bcrypt.generate_password_hash(pwd).decode('utf-8')# type: ignore[arg-type]
            username=f'{form.name.data[:10]}.{form.lastname.data[:10]}'#type: ignore[index]
            nb = User.query.filter(User.username==username).count()
            username += f'({nb})' if nb>0 else ''
            user = User(name=form.name.data,
                        lastname=form.lastname.data,
                        username=username,
                        email=form.email.data if form.email.data else None,
                        phone=form.phone.data if form.phone.data else None,
                        datenaiss= form.datenaiss.data,
                        password=hash_pwd,)
            db.session.add(user)
            db.session.commit()
            db.session.refresh(user)
            login_user(user)
            #print(user, form.parcours.data)
            choices = event.parcours.filter(Parcours.name.in_([eval(data)[0] for data in form.parcours.data])).all()#type: ignore[union-attr]

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
def profil()-> str|Response:
    user = current_user
    return render_template('profil.html', user_data=user)

def save_avatar(form_picture:FileStorage, old_picture_name: str|None=None)-> str:
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)#type:ignore[type-var]
    picture_name = f'{random_hex}{f_ext}'
    picture_path = os.path.join(app.root_path, 'static/profil_pics', picture_name)

    i = Image.open(form_picture)
    i.thumbnail(PICTURE_SIZE)
    i.save(picture_path)

    if old_picture_name!=DEFAULT_PROFIL_PIC and old_picture_name is not None:
        os.remove(os.path.join(app.root_path, 'static/profil_pics', old_picture_name))

    return picture_name

@set_route(users, '/profil/update', methods=['get', 'post'])
@login_required
def modify_profil()-> str|Response:
    user:User = current_user
    form:ModifyForm = ModifyForm(data={'name':user.name,
                            'lastname':user.lastname,
                            'username':user.username,
                            'email':user.email,
                            'phone':user.phone,
                            'datenaiss':user.datenaiss,
                            'profil_pic':user.avatar})
    if form.validate_on_submit():
        if form.username.data == user.name or not User.query.filter_by(name=form.username.data).first():
            # le nom peut etre utilisé
            user.name=form.name.data
            user.lastname=form.lastname.data
            user.username=form.username.data
            user.email=form.email.data if form.email.data else None
            user.phone=form.phone.data if form.phone.data else None
            user.datenaiss= form.datenaiss.data
            if form.profil_pic.data and isinstance(form.profil_pic.data, FileStorage):
                user.avatar = save_avatar(form.profil_pic.data, user.avatar)
            db.session.commit()
            flash(_('flash.profilupdated'), 'success')
            return redirect(url_for('users.profil'))
        else:
            form.username.errors = list(form.username.errors)+['ce nom d\'utilisateur est déjà utilisé.']

    return render_template('modify_profil.html', user_data=user, form=form)


@set_route(users, '/profil/updatepwd', methods=['get', 'post'])
@login_required
def modify_password()-> str|Response:
    user:User = current_user
    form:ModifyPwdForm = ModifyPwdForm()

    if form.validate_on_submit():
        if bcrypt.check_password_hash(user.password, form.old_pwd.data):# type: ignore[arg-type]
            hash_pwd= bcrypt.generate_password_hash(form.password.data).decode('utf-8')# type: ignore[arg-type]
            user.password = hash_pwd
            db.session.commit()
            return redirect(url_for('users.profil'))
        else:
            form.old_pwd.errors = list(form.old_pwd.errors)+['wrong password']

    return render_template('modify_password.html', user_data=user, form=form)