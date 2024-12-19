from flask import Blueprint, flash, render_template, redirect, url_for, request, session
from flask_app import admin_required, db, set_route, socketio
from flask_app.admin.editions.form import Edition_form
from flask_login import login_required, current_user
from flask_app.models import  Event, Parcours, Edition, Inscription
from datetime import datetime
from flask_socketio import join_room, leave_room

dossard = Blueprint('dossard', __name__, template_folder='templates')

@set_route(dossard, '/event/<event_name>/editions/<edition_name>/modify_dossard', methods=['POST', 'GET'])
@login_required
@admin_required
def dossard_page(event_name, edition_name):
    user = current_user
    return render_template('dossard.html', user_data=user, pyscript=True)


@set_route(dossard, '/event/<event_name>/editions/<edition_name>/dossard', methods=['POST', 'GET'])
@login_required
@admin_required
def generate_dossard(event_name, edition_name):
    event : Event = Event.query.filter_by(name=event_name).first_or_404()
    edition : Edition= event.editions.filter_by(name=edition_name).first_or_404()
    user = current_user


    return render_template('generate_dossard.html', user_data=user, event_data=event, edition_data=edition, now=datetime.now(), inscriptions=edition.inscriptions, event_modif=True, edition_sidebar=True)

@socketio.on('connect', namespace='/dossard')
def dossard_connect(auth):
    if current_user.is_authenticated and auth.get('event_id') and auth.get('edition_id'):
        event:Event = Event.query.get(auth['event_id'])
        if not event or event.createur != current_user:
            return False # connection not allowed
        edition = event.editions.filter_by(id=auth['edition_id']).first()
        if not edition:
            return False # connection not allowed
    else:
        False # connection not allowed

@socketio.on('disconnect', namespace='/dossard')
def dossard_disconnect():
    pass

@socketio.on('change_dossard', namespace='/dossard')
def change_dossard(data):
    inscription = Inscription.query.get(data['inscription_id'])
    if (not inscription and isinstance(data['new_dossard'], int) and not current_user.is_authenticated and inscription.event.createur == current_user):
        return False
    if Inscription.query.filter(Inscription.dossard == data['new_dossard'], Inscription.edition==inscription.edition, Inscription.id!=inscription.id).first():
        return {'erreur':'dossard déjà utilisé'}
    inscription.dossard = data['new_dossard']
    db.session.commit()
    return True

@socketio.on('change_presence', namespace='/dossard')
def set_presence(data):
    if not data.get('presence') is not None or not data.get('inscription_id'):
        return False
    
    inscription:Inscription = Inscription.query.get(data['inscription_id'])
    if not inscription:
        return False
    if inscription.edition.edition_date>datetime.now():
        return False

    inscription.present = bool(data['presence'])
    db.session.commit()
    return True

@set_route(dossard, '/event/<event_name>/editions/<edition_name>/dossard/generate', methods=['POST', 'GET'])
@login_required
@admin_required
def generate_all_dossard(event_name, edition_name):
    event : Event = Event.query.filter_by(name=event_name).first_or_404()
    edition : Edition= event.editions.filter_by(name=edition_name).first_or_404()
    user = current_user

    dossard_nb = [inscription.dossard for inscription in edition.inscriptions.filter(Inscription.dossard!=None).all()]
    last_dossard = 1
    for inscription in edition.inscriptions.filter(Inscription.dossard==None).all():
        while last_dossard in dossard_nb:
            last_dossard+=1
        inscription.dossard = last_dossard
        last_dossard+=1
    db.session.commit()

    return redirect(url_for("admin.editions.dossard.generate_dossard", event_name=event.name, edition_name=edition.name))
