from flask import flash, redirect, url_for, render_template
from flask_app import app, fake_data, users
from flask_app.forms import Login_form, Signup_form
from flask_login import login_user, logout_user, login_required, current_user


@app.route('/')
def home():
    # * home page of the web site
    return render_template("0-home.html", user_data=None)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = Login_form()
    if form.validate_on_submit():
        user= users.get(form.username.data)
        if user and form.password.data == user.password:
            print(user)
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
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/event/<event_name>')
@login_required
def home_event(event_name):
    #* page to access and modify an event
    event_data = fake_data.get(event_name)
    user = current_user
    return render_template("1-home_event.html", user_data=user, event_data=event_data)


@app.route('/event/<event_name>/editions')
@login_required
def editions(event_name):
    # * page to access the differents editions of the event
    event_data = fake_data.get(event_name)
    user = current_user
    return render_template("1.1-editions.html", user_data=user, event_data=event_data)


@app.route('/event/<event_name>/editions/<edition>')
@login_required
def modify_edition(event_name, edition):
    event_data = fake_data.get(event_name)
    user = current_user
    return render_template('1.1.1-modify_edition.html', user_data=user, event_data=event_data)


@app.route('/event/<event_name>/parcours')
@login_required
def parcours(event_name):
    # * page to access the differents parcours of the event
    event_data = fake_data.get(event_name)
    user = current_user
    return render_template("1.2-parcours.html", user_data=user, event_data=event_data)


@app.route('/event/<event_name>/coureurs')
@login_required
def coureurs(event_name):
    # * page to access the different runner that will or had participate to the event
    event_data = fake_data.get(event_name)
    user = current_user
    return render_template("1.3-coureurs.html", user_data=user, event_data=event_data)
