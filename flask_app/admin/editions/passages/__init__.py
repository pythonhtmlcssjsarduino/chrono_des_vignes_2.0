import time
from flask import Blueprint, redirect, render_template, flash, request, jsonify
from flask_app import admin_required, db, set_route, lang_url_for as url_for
from flask_app.admin.parcours import calc_points_dist
from flask_login import login_required, current_user
from flask_app.models import  Event, Edition, PassageKey, Stand, Parcours, Passage, User, Inscription, Trace
from datetime import datetime
from flask_app.admin.editions.passages.form import NewKeyForm, ChronoLoginForm, ChronoLoginForm, SetPassageForm
import secrets
from wtforms import SelectField

passages = Blueprint('passages', __name__, template_folder='templates')
@login_required
@admin_required
@set_route(passages, "/event/<event_name>/editions/<edition_name>/dashboard", methods=['get', 'post'])
def dashboard(event_name, edition_name):
    user = current_user
    event = Event.query.filter_by(name= event_name).first_or_404()
    edition:Edition = event.editions.filter_by(name=edition_name).first_or_404()
    keys = PassageKey.query.filter_by(event=event, edition=edition).all()
    if edition.edition_date > datetime.now():
        # formulaire d'ajout
        form:NewKeyForm = NewKeyForm()
        for i, parcours in enumerate(edition.parcours):
            choices =  [('', '')] + [(f'{s.id}', f'{s.parcours.name} - {s.name}') for s in Stand.query.filter(Stand.parcours.has(Parcours.id==parcours.id), Stand.chrono==True).all()]
            if len(form.stands.entries)<=i:form.stands.append_entry()
            field = form.stands.entries[i]
            field.choices = choices
            field.label.text = f'parcours {parcours.name}'

        if form.validate_on_submit():
            if not edition.passage_keys.filter_by(name=form.name.data).first():
                stands = [Stand.query.get(int(stand.data)) for stand in form.stands if stand.data]
                key_code=secrets.token_urlsafe(5)
                while PassageKey.query.filter_by(key=key_code).first():
                    key_code=secrets.token_urlsafe(5)
                key = PassageKey(event_id=event.id,
                                edition_id=edition.id,
                                stands=stands,
                                key=key_code,
                                name=form.name.data)
                db.session.add(key)
                db.session.commit()
                ic(key, edition, edition.id)

                return redirect(url_for("admin.editions.passages.dashboard", event_name=event.name, edition_name=edition.name))
            else:
                form.name.errors = list(form.name.errors)+['vous utiliser déjà ce nom.']
    else:
        form = None


    passages = Passage.query.filter(Passage.key.has(PassageKey.edition == edition)).all()

    return render_template('dashboard.html', event_data=event, edition_data = edition, user_data=user, now = datetime.now(), keys=keys, passages=passages, form=form, event_modif=True, edition_sidebar=True)

@set_route(passages, '/chrono', methods=["GET", 'post'])
def chrono_home():
    user = current_user if current_user.is_authenticated else None


    form:ChronoLoginForm = ChronoLoginForm()
    if form.validate_on_submit():
        if PassageKey.query.filter_by(key=form.key.data).first():
            return redirect(url_for('admin.editions.passages.chrono_page', key_code=form.key.data))
        else:
            form.key.errors = list(form.key.errors)+['cette clé n\'est pas valable.']

    return render_template('chrono_home.html', user_data=user, form=form)


def parcours_chrono_list_dist(parcours:Parcours, dist_stand:list[int]):
    part_list = []
    dist_list = []
    start = parcours.start_stand
    new_stand=start
    last_point=None
    dist=0
    # si aucun depart alors ne mettre aucun stand
    if start:
        part_list.append(start)
        turn_nb = 0
        while True:
            if new_stand == start:
                turn_nb +=1
            old_stand = new_stand
            # si l'ancien stand a une trace qui part d lui
            trace:Trace = old_stand.start_trace.filter_by(turn_nb=turn_nb).first()
            if trace :
                new_stand = trace.end
                dist += (calc_points_dist(new_stand.lat, new_stand.lng, last_point[0], last_point[1]) if last_point else 0)
                last_point = new_stand.lat, new_stand.lng

                if new_stand.id==dist_stand[0]:
                    dist_stand = dist_stand[1:]
                    dist_list.append(dist)
                    if len(dist_stand)==0:
                        break

                dist += trace.get
            else:
                break

def get_passage_data(passage:Passage)->dict:
    data={'dossard':passage.inscription.dossard,
          'name':passage.inscription.inscrit.name,
          'time_stamp':passage.time_stamp,
          'parcours':[]}
    
    user_passages:list[Passage] = Passage.query.filter(Passage.inscription==passage.inscription, Passage.time_stamp<=passage.time_stamp).all()
    if len(user_passages)>0:
        first_passage = user_passages[0]
        for stand, dist in zip(passage.inscription.parcours.iter_chrono_list(), passage.inscription.parcours.get_chrono_dists()):
            if len(user_passages)>0 and stand == user_passages[0].get_stand():
                delta=user_passages[0].time_stamp-first_passage.time_stamp
                days = delta.days
                hours, remainder = divmod(delta.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                delta= f"{f'{days} days, 'if days>0 else ''}{hours:02}:{minutes:02}:{seconds:02}"
                user_passages.pop(0)
                succes=True
            elif len(user_passages)>0:
                delta=None
                succes=False
            else:
                succes=None
                delta=None
            
            data['parcours'].append({'stand':stand, 'dist':round(dist, 3), 'delta':delta, 'succes':succes})
        for p in user_passages:
            succes=None
            delta = p.time_stamp-first_passage.time_stamp
            days = delta.days
            hours, remainder = divmod(delta.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            delta= f"{f'{days} days, 'if days>0 else ''}{hours:02}:{minutes:02}:{seconds:02}"
            data['parcours'].append({'stand':p.get_stand(), 'dist':None, 'delta':delta, 'succes':succes})

    return data

def get_key_passage_data(key:PassageKey):
    passage:Passage
    data = []
    for passage in Passage.query.filter_by(key=key).order_by(Passage.time_stamp.asc()).all():
        data.append(get_passage_data(passage))
        
        '''passage_user = passage.inscription.inscrit
        passage_stand = passage.key.stands.filter_by(parcours=passage.inscription.parcours).first()
        passage_chronos_list = list(passage.inscription.parcours.iter_chrono_list())

        user_passages = Passage.query.filter(Passage.inscription==passage.inscrit, Passage.time_stamp<=passage.time_stamp).all()
        passage_data = [{'stand':stand, 'dist':dist} for stand, dist in zip(passage.inscription.parcours.iter_chrono_list(), passage.inscription.parcours.get_chrono_dists())]
        offset = 0
        for index, passed_passage in enumerate(user_passages):
            index+=offset
            if index +1 >= len(passage_chronos_list):
                passage_data.append({'user':False})
            for stand in passage_chronos_list[index:]:
                if passed_stand_id == stand:
                    ic(user_passages_passage[passage_user.id], Passage.query.get(user_passages_passage[passage_user.id][0]), Passage.query.get(user_passages_passage[passage_user.id][index]))
                    return_list.append(True)
                    delta = Passage.query.get(user_passages_passage[passage_user.id][index]).time_stamp-Passage.query.get(user_passages_passage[passage_user.id][0]).time_stamp
                    days = delta.days
                    hours, remainder = divmod(delta.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    delta_list.append(f"{f'{days} days, 'if days>0 else ''}{hours:02}:{minutes:02}:{seconds:02}")
                    break
                else:
                    return_list.append(None)
                    delta_list.append(None)
                    offset+=1'''
        
    return data

@set_route(passages, '/chrono/<key_code>')
def chrono_page(key_code):
    user = current_user if current_user.is_authenticated else None
    key = PassageKey.query.filter_by(key=key_code).first_or_404()
    # TODO uncomment this part
    """ if key.edition.edition_date > datetime.now():
        flash('l\'edition n\'est pas aujourd\'hui', 'warning')
        return redirect(url_for("admin.editions.passages.chrono_home")) """
    
    key_passages = get_key_passage_data(key)
    '''key_passages = []
    user_passages_stand = {}
    user_passages_passage = {}
    passage:Passage
    for passage in Passage.query.filter_by(key=key).order_by(Passage.time_stamp.asc()).all():
        ic(passage)
        passage_user = passage.inscription.inscrit
        passage_stand = passage.key.stands.filter_by(parcours=passage.inscription.parcours).first()
        passage_chronos_list = list(passage.inscription.parcours.iter_chrono_list())
        if passage_user.id not in user_passages_stand.keys():
            user_passages_stand[passage_user.id] = []
        user_passages_stand[passage_user.id].append(passage_stand.id)
        if passage_user.id not in user_passages_passage.keys():
            user_passages_passage[passage_user.id] = []
        user_passages_passage[passage_user.id].append(passage.id)

        return_list = []
        delta_list = []
        offset = 0
        for index, passed_stand_id in enumerate(user_passages_stand[passage_user.id]):
            index += offset
            if index +1 >= len(passage_chronos_list):
                return_list.append(False)
                delta_list.append(None)

            for stand in passage_chronos_list[index:]:
                if passed_stand_id == stand.id:
                    ic(user_passages_passage[passage_user.id], Passage.query.get(user_passages_passage[passage_user.id][0]), Passage.query.get(user_passages_passage[passage_user.id][index]))
                    return_list.append(True)
                    delta = Passage.query.get(user_passages_passage[passage_user.id][index]).time_stamp-Passage.query.get(user_passages_passage[passage_user.id][0]).time_stamp
                    days = delta.days
                    hours, remainder = divmod(delta.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    delta_list.append(f"{f'{days} days, 'if days>0 else ''}{hours:02}:{minutes:02}:{seconds:02}")
                    break
                else:
                    return_list.append(None)
                    delta_list.append(None)
                    offset+=1

        dist_list = []
        dist =  0
        for element in passage.inscription.parcours:
            if isinstance(element, Stand):
                if element.chrono:
                    dist_list.append(round(dist, 3))
            else:
                dist += element.get_dist()
            
        key_passages.append((passage, passage_chronos_list, return_list, delta_list, dist_list))
'''
    ic(key_passages)
    return render_template('chrono.html', user_data=user, key=key, passages=reversed(key_passages))

@set_route(passages, '/chrono/set', methods=['post'])
def set_passage():
    form = SetPassageForm()
    inscription = Inscription.query.filter(Inscription.dossard == form.dossard.data).first()
    if not inscription:
        return jsonify({"success": False, 'saved':False, 'error':'not valide dossard', 'request':{'dossard':form.dossard.data, 'time':form.time.data, 'key':form.key.data}})
    key = PassageKey.query.filter_by(key=form.key.data).first()
    if not key:
        return jsonify({"success": False, 'saved':False, 'error':'not valide key', 'request':{'dossard':form.dossard.data, 'time':form.time.data, 'key':form.key.data}})
    
    pass_time = datetime.fromtimestamp(form.time.data/1000)
    ic(key)#type:ignore
    ic(pass_time) #type:ignore
    ic(inscription) #type:ignore
    user_passages = Passage.query.filter_by(inscription=inscription).order_by(Passage.time_stamp).all()
    ic(user_passages) #type:ignore

    stand = key.stands.filter_by(parcours=inscription.parcours).first()

    parcours = inscription.parcours

    passage = Passage(key_id = key.id, time_stamp=pass_time, inscription_id= inscription.id)


    return jsonify({"success": True, 'saved':True, 'request':{'dossard':form.dossard.data, 'time':form.time.data, 'key':form.key.data}})
