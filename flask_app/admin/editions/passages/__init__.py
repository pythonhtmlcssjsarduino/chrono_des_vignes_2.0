import time
from flask import Blueprint, redirect, render_template, flash, url_for, jsonify
from flask_app import admin_required, db
from flask_login import login_required, current_user
from flask_app.models import  Event, Edition, PassageKey, Stand, Parcours, Passage, User, Inscription
from datetime import datetime
from flask_app.admin.editions.passages.form import NewKeyForm, ChronoLoginForm, ChronoLoginForm, SetPassageForm
import secrets

passages = Blueprint('passages', __name__, template_folder='templates')
@login_required
@admin_required
@passages.route("/event/<event_name>/editions/<edition_name>/dashboard", methods=['get', 'post'])
def dashboard(event_name, edition_name):
    user = current_user
    event = Event.query.filter_by(name= event_name).first_or_404()
    edition:Edition = event.editions.filter_by(name=edition_name).first_or_404()
    keys = PassageKey.query.filter_by(event=event, edition=edition).all()
    if edition.edition_date > datetime.now():
        # formulaire d'ajout
        form:NewKeyForm = NewKeyForm()
        form.stands.choices = [(f'{s.id}', f'{s.parcours.name} - {s.name}') for s in Stand.query.filter(Stand.parcours.has(Parcours.editions.any(Edition.id==edition.id)), Stand.chrono==True).all()]
        if form.validate_on_submit():
            if not edition.passage_keys.filter_by(name=form.name.data).first():
                stand = Stand.query.get(int(form.stands.data))
                key_code=secrets.token_urlsafe(5)
                while PassageKey.query.filter_by(key=key_code).first():
                    key_code=secrets.token_urlsafe(5)
                key = PassageKey(event_id=event.id,
                                edition_id=edition.id,
                                parcours_id=stand.parcours.id,
                                stand_id=stand.id,
                                key=key_code,
                                name=form.name.data)
                db.session.add(key)
                db.session.commit()

                return redirect(url_for("admin.editions.passages.dashboard", event_name=event.name, edition_name=edition.name))
            else:
                form.name.errors = list(form.name.errors)+['vous utiliser déjà ce nom.']
    else:
        form = None


    passages = Passage.query.filter(Passage.key.has(PassageKey.edition == edition)).all()

    return render_template('dashboard.html', event_data=event, edition_data = edition, user_data=user, now = datetime.now(), keys=keys, passages=passages, form=form, event_modif=True, edition_sidebar=True)

@passages.route('/chrono', methods=["GET", 'post'])
def chrono_home():
    user = current_user if current_user.is_authenticated else None


    form:ChronoLoginForm = ChronoLoginForm()
    if form.validate_on_submit():
        if PassageKey.query.filter_by(key=form.key.data).first():
            return redirect(url_for('admin.editions.passages.chrono_page', key_code=form.key.data))
        else:
            form.key.errors = list(form.key.errors)+['cette clé n\'est pas valable.']

    return render_template('chrono_home.html', user_data=user, form=form)

@passages.route('/chrono/<key_code>')
def chrono_page(key_code):
    user = current_user if current_user.is_authenticated else None
    key = PassageKey.query.filter_by(key=key_code).first_or_404()
    # TODO uncomment this part
    """ if key.edition.edition_date > datetime.now():
        flash('l\'edition n\'est pas aujourd\'hui', 'warning')
        return redirect(url_for("admin.editions.passages.chrono_home")) """
    return render_template('chrono.html', user_data=user, key=key)

@passages.route('/chrono/set', methods=['post'])
def set_passage():
    form = SetPassageForm()
    user = User.query.filter(User.inscriptions.any(Inscription.dossard == form.dossard.data)).first()
    if not user:
        return jsonify({"success": False, 'error':'not valide dossard', 'request':{'dossard':form.dossard.data, 'time':form.time.data, 'key':form.key.data}})
    key = PassageKey.query.filter_by(key=form.key.data).first()
    if not key:
        return jsonify({"success": False, 'error':'not valide key', 'request':{'dossard':form.dossard.data, 'time':form.time.data, 'key':form.key.data}})
    pass_time = datetime.fromtimestamp(form.time.data/1000)
    ic(key)#type:ignore
    ic(pass_time) #type:ignore
    ic(user) #type:ignore

    passage = Passage(key_id = key.id, time_stamp=pass_time, inscrit_id= user.id)


    return jsonify({"success": True})
