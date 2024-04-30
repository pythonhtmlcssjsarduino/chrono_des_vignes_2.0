from flask import Blueprint, redirect, url_for, flash, render_template
from flask_login import login_required, current_user, login_user, logout_user
from flask_app.models import User
from flask_app.users.forms import Login_form, Signup_form
from flask_app import db

users = Blueprint('users', __name__, template_folder='templates')

@users.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = Login_form()
    if form.validate_on_submit():
        user= User.query.filter_by(username=form.username.data).first()
        if user and form.password.data == user.password:
            login_user(user)
            flash(f'welcome {user.name} you are connected', 'success')
            if user.admin:
                return redirect(url_for('admin.home_event', event_name='course des vignes'))
            return redirect(url_for('home'))
        else:
            flash('le mot de passe ou nom d\'utilisateur n\'est pas valide', 'warning')
    return render_template('login.html', form=form)


@users.route('/signup', methods=['POST', 'GET'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = Signup_form()
    if form.validate_on_submit():
        hash_pwd=form.password.data
        user = User(name=form.name.data,
                    lastname=form.lastname.data,
                    username=form.username.data,
                    email=form.email.data,
                    phone=form.phone.data,
                    datenaiss= form.datenaiss.data,
                    password=hash_pwd,)
        db.session.add(user)
        db.session.commit()
        flash('votre compte a bien été crée', 'success')
        login_user(user)
        return redirect(url_for('home'))
    return render_template('signup.html', form=form)


@users.route('/logout')
@login_required
def logout():
    logout_user()
    flash('tu es bien déconnecté !', 'success')
    return redirect(url_for('home'))