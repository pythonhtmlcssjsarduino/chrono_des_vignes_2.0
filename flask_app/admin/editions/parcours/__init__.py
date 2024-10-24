import time
from flask import Blueprint, redirect, render_template, flash, request, jsonify, session
from flask_app import admin_required, db, set_route, lang_url_for as url_for, socketio
from flask_app.admin.parcours import calc_points_dist
from flask_login import login_required, current_user
from flask_app.models import  Event, Edition, PassageKey, Stand, Parcours, Passage, User, Inscription, Trace
from datetime import datetime
from flask_app.admin.editions.passages.form import NewKeyForm, ChronoLoginForm, ChronoLoginForm, SetPassageForm
import secrets
from flask_socketio import join_room, leave_room, emit
from flask_app.admin.editions.passages import get_passage_data

parcours = Blueprint('parcours', __name__, template_folder='templates')

@socketio.on('connect', namespace='/edition/parcours')
def parcours_connect(auth):
    if current_user.is_authenticated and auth.get('event_id') and auth.get('edition_id'):
        event:Event = Event.query.get(auth['event_id'])
        if not event or event.createur != current_user:
            return False # connection not allowed
        edition = event.editions.filter_by(id=auth['edition_id']).first()
        if not edition:
            return False # connection not allowed
        
        session['room'] = f'edition-parcours-{event.id}-{edition.id}'
        join_room(session['room'], request.sid)
    else:
        return False # connection not allowed
@socketio.on('disconnect', namespace='/edition/parcours')
def parcours_disconnect():
    leave_room(session['room'], request.sid)
    del session['room']

@socketio.on('get_parcours_passage', namespace='/edition/parcours')
def get_parcours_passages(parcours):
    parcours = Parcours.query.get(parcours)
    edition = Edition.query.get(session['room'].split('-')[3])
    inscription:list[Inscription] = Inscription.query.filter_by(edition=edition, parcours=parcours).all()
    data = []
    for coureur in inscription:
        passage = coureur.passages.order_by(Passage.time_stamp.desc()).first()
        if coureur.has_started():
            ic(coureur.has_started(), coureur.has_finish(), coureur.has_all_right())
            pass_data = get_passage_data(passage, json=True)
            pass_data.update({'started':True, 'finish':coureur.has_finish(), 'all_right':coureur.has_all_right()})
            data.append(pass_data)
        else:
            data.append({'started':False, 'dossard':coureur.dossard, 'name':coureur.inscrit.name})
    return data

@set_route(parcours, '/event/<event_name>/editions/<edition_name>/parcours')
@login_required
@admin_required
def view(event_name, edition_name):
    user = current_user
    event = Event.query.filter_by(name=event_name).first_or_404()
    edition:Edition = event.editions.filter_by(name=edition_name).first_or_404()
    parcours = edition.parcours

    return render_template('edition_parcours.html', parcours_data=parcours, edition_data = edition, event_data=event, user_data=user, event_modif=True, edition_sidebar=True)

