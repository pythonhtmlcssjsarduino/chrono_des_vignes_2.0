from datetime import datetime
from flask import Blueprint, redirect, render_template, flash, request, jsonify, session
from flask_app import admin_required, db, set_route, lang_url_for as url_for, socketio
from flask_app.admin.parcours import calc_points_dist
from flask_login import login_required, current_user
from flask_app.models import  Event, Edition, PassageKey, Stand, Parcours, Passage, User, Inscription, Trace
from flask_socketio import join_room, leave_room, emit
from ..passages import get_passage_data

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
    inscriptions:list[Inscription] = Inscription.query.filter_by(edition=edition, parcours=parcours).all()
    data = []
    for coureur in inscriptions:
        passage = coureur.get_last_passage()
        first_passage:Passage = coureur.passages.order_by(Passage.time_stamp.asc()).first()
        if coureur.has_started():
            pass_data = get_passage_data(passage, json=True)
            pass_data.update({'started':True, 'start_time':first_passage.time_stamp.timestamp(), 'id':coureur.id, 'finish':coureur.has_finish(), 'all_right':coureur.has_all_right(), 'end':coureur.end})
            data.append(pass_data)
        else:
            pass_data = {'parcours':[], 'started':False, 'id':coureur.id, 'dossard':coureur.dossard, 'name':coureur.inscrit.name}
            for stand, dist in zip(coureur.parcours.iter_chrono_list(), coureur.parcours.get_chrono_dists()):
                pass_data['parcours'].append({'stand':{'name':stand.name}, 'dist':round(dist, 3), 'delta':'', 'succes':None})
            data.append(pass_data)
    return data

@socketio.on('launch_parcours', namespace='/edition/parcours')
def launch_parcours(data):
    parcours = Parcours.query.get(data.get('parcours_id'))
    edition = Edition.query.get(session['room'].split('-')[3])
    if parcours is not None and data.get('start_time'):
        start_time =datetime.fromtimestamp(data['start_time']/1000)
        inscription:Inscription
        for inscription in edition.inscriptions.filter(Inscription.parcours==parcours).all():
            if inscription.has_started() and inscription.present:
                passage = Passage(time_stamp=start_time, inscription_id = inscription.id)
                db.session.add(passage)
                db.session.commit()
                db.session.refresh(passage)
                emit('new_passage', {'time':str(start_time), 'user':inscription.inscrit.username, 'dossard':inscription.dossard,'key':'', 'stand':passage.get_stand().name}, namespace='/dashboard', to=f'{passage.key.event.id}-{passage.key.edition.id}')
                
                first_passage:Passage = inscription.passages.order_by(Passage.time_stamp.asc()).first()
                pass_data = get_passage_data(passage, json=True)
                pass_data.update({'started':True, 'parcours_id':inscription.parcours.id, 'start_time':first_passage.time_stamp.timestamp() , 'id':inscription.id, 'finish':inscription.has_finish(), 'all_right':inscription.has_all_right(), 'end':inscription.end})
                emit('new_passage', pass_data, namespace='/edition/parcours', to=f'edition-parcours-{inscription.event.id}-{inscription.edition.id}')

@socketio.on('launch_parcours', namespace='/edition/parcours')
def stop_parcours(data):
    parcours = Parcours.query.get(data.get('parcours_id'))
    edition = Edition.query.get(session['room'].split('-')[3])

    if parcours is not None:
        inscription:Inscription
        for inscription in edition.inscriptions.filter(Inscription.parcours==parcours).all():
            if inscription.end is None:
                if inscription.has_started():
                    if inscription.has_finish():
                        if inscription.has_all_right():
                            end = 'finish'
                        else:
                            end = 'disqual'
                    else:
                        end='abandon'
                else:
                    end = 'absent'

                inscription.end = end
                db.session.commit()
                emit('stop', {'type':end, 'inscription_id':inscription.id}, namespace='/edition/parcours', to=f'edition-parcours-{inscription.event.id}-{inscription.edition.id}')

@socketio.on('disqualify', namespace='/edition/parcours')
def disqualify(data):
    inscription = Inscription.query.get(data.get('inscription_id'))
    if inscription:
        inscription.end = 'disqual'
        db.session.commit()
        emit('stop', {'type':'disqual', 'inscription_id':inscription.id}, namespace='/edition/parcours', to=f'edition-parcours-{inscription.event.id}-{inscription.edition.id}')

@socketio.on('abandon', namespace='/edition/parcours')
def abandon(data):
    if data.get('inscription_id'):
        inscription = Inscription.query.get(data['inscription_id'])
        inscription.end = 'abandon'
        db.session.commit()
        emit('stop', {'type':'abandon', 'inscription_id':inscription.id}, namespace='/edition/parcours', to=f'edition-parcours-{inscription.event.id}-{inscription.edition.id}')

@socketio.on('finish', namespace='/edition/parcours')
def finish(data):
    if data.get('inscription_id'):
        inscription:Inscription = Inscription.query.get(data['inscription_id'])
        if not inscription.has_finish():
            return False
        inscription.end = 'finish'
        db.session.commit()
        emit('stop', {'type':'finish', 'inscription_id':inscription.id}, namespace='/edition/parcours', to=f'edition-parcours-{inscription.event.id}-{inscription.edition.id}')

@set_route(parcours, '/event/<event_name>/editions/<edition_name>/parcours')
@login_required
@admin_required
def view(event_name, edition_name):
    user = current_user
    event = Event.query.filter_by(name=event_name).first_or_404()
    edition:Edition = event.editions.filter_by(name=edition_name).first_or_404()
    parcours = edition.parcours

    if 0 and edition.edition_date>datetime.now():
        flash('l\'edition n\'as pas encore commencé', 'warning')
        return redirect(url_for('admin.editions.modify_edition_page', edition_name=edition.name, event_name=event.name))

    return render_template('edition_parcours.html', parcours_data=parcours, edition_data = edition, event_data=event, user_data=user, event_modif=True, edition_sidebar=True, now=datetime.now())

