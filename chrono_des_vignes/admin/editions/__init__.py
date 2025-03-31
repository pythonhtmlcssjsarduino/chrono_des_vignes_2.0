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

from flask import Blueprint, flash, render_template, redirect, request
from chrono_des_vignes import admin_required, db, set_route, lang_url_for as url_for
from chrono_des_vignes.admin.editions.form import Edition_form
from flask_login import login_required, current_user
from chrono_des_vignes.models import  Event, Parcours, Edition
from datetime import datetime
from .dossard import dossard
from .passages import passages
from .parcours import parcours
from .result import result
from sqlalchemy import or_

editions = Blueprint('editions', __name__, template_folder='templates')
editions.register_blueprint(dossard)
editions.register_blueprint(passages)
editions.register_blueprint(parcours)
editions.register_blueprint(result)

@set_route(editions, '/event/<event_name>/editions', methods=['POST', 'GET'])
@login_required
@admin_required
def editions_page(event_name):
    # * page to access the differents editions of the event
    event = Event.query.filter_by(name=event_name).first_or_404()
    user = current_user
    form = Edition_form()
    form.parcours.choices=[str((e.name, e.description)) for e in event.parcours.filter_by(archived=False).all()]
    if form.validate_on_submit():
        if not event.editions.filter_by(name=form.name.data).first():
            #ok nom pas utilisé
            parcours = [eval(p)[0] for p in form.parcours.data]
            parcours = event.parcours.filter(Parcours.name.in_(parcours)).all()
            edition = Edition(name = form.name.data,
                              event_id=event.id,
                              parcours=parcours,
                              edition_date=form.edition_date.data,
                              description = form.description.data,
                              first_inscription=form.first_inscription.data,
                              last_inscription=form.last_inscription.data,
                              rdv_lat=form.rdv_lat.data,
                              rdv_lng=form.rdv_lng.data)
            db.session.add(edition)
            db.session.commit()
            flash('edition bien crée', 'success')
            return redirect(url_for('admin.editions.editions_page', event_name=event.name))
        else:
            form.name.errors = list(form.name.errors)+['vous utiliser deja ce nom.']

    return render_template("editions.html", user_data=user, event_data=event, form=form, event_modif=True)

@set_route(editions, '/event/<event_name>/editions/<edition_name>/delete', methods=['POST', 'GET'])
@login_required
@admin_required
def delete_edition_page(event_name, edition_name):
    event = Event.query.filter_by(name=event_name).first_or_404()
    edition : Edition= event.editions.filter_by(name=edition_name).first_or_404()
    if edition.first_inscription <= datetime.now():
        flash('l\'edition ne peut pas être supprimée car les inscriptions sont déjà ouvertes', 'danger')
        return redirect(url_for('admin.editions.modify_edition_page',event_name=event.name, edition_name=edition.name))

    db.session.delete(edition)
    db.session.commit()
    flash('l\'edition a bien été supprimée', 'success')
    return redirect(url_for('admin.editions.editions_page',event_name=event.name))

@set_route(editions, '/event/<event_name>/editions/<edition_name>', methods=['POST', 'GET'])
@login_required
@admin_required
def modify_edition_page(event_name, edition_name):
    event : Event = Event.query.filter_by(name=event_name).first_or_404()
    edition : Edition= event.editions.filter_by(name=edition_name).first_or_404()
    user = current_user
    form = Edition_form(data={'name':edition.name,
                              'edition_date':edition.edition_date,
                              'description':edition.description,
                              'first_inscription':edition.first_inscription,
                              'last_inscription':edition.last_inscription,
                              'rdv_lat':edition.rdv_lat,
                              'rdv_lng':edition.rdv_lng,
                              'parcours':[str((p.name, p.description)) for p in edition.parcours]})
    form.parcours.choices=[str((p.name, p.description)) for p in event.parcours.filter(or_(Parcours.archived==False, Parcours.editions.any(Edition.id==edition.id))).all()]

    #? desactiver le champs si dates deja passé
    form.edition_date.render_kw.pop("disabled", None)
    form.first_inscription.render_kw.pop("disabled", None)
    form.last_inscription.render_kw.pop("disabled", None)
    form.name.render_kw = {}
    form.rdv_lat.render_kw = {}
    form.rdv_lng.render_kw = {}
    form.parcours.render_kw = {}
    if edition.first_inscription <= datetime.now():
        # si ils peuvent s'iscrire ne plus modifier la date de l'edition
        form.edition_date.render_kw["disabled"]= "disabled"
        form.parcours.render_kw["disabled"]= "disabled"
        form.parcours.data = [str((p.name, p.description)) for p in edition.parcours]
        form.first_inscription.render_kw["disabled"]= "disabled"
        form.name.render_kw["disabled"]= "disabled"
        form.rdv_lat.render_kw["disabled"]= "disabled"
        form.rdv_lng.render_kw["disabled"]= "disabled"
    if edition.last_inscription <= datetime.now():
        form.last_inscription.render_kw["disabled"]= "disabled"
    #? fin desactivation des champs

    if form.validate_on_submit():
        #ic(edition.rdv_lat, form.rdv_lat.data, edition.rdv_lng, form.rdv_lng.data)
        if form.name.data == edition.name or not event.editions.filter_by(name=form.name.data).first():
            edition.name = form.name.data
            edition.edition_date = form.edition_date.data
            edition.description = form.description.data
            edition.parcours = event.parcours.filter(Parcours.name.in_([eval(p)[0] for p in form.parcours.data])).all()
            edition.first_inscription = form.first_inscription.data
            edition.last_inscription = form.last_inscription.data
            edition.rdv_lat = form.rdv_lat.data
            edition.rdv_lng = form.rdv_lng.data
            db.session.commit()
            flash('l\'edition a bien été mise a jour.', 'success')
            return redirect(url_for('admin.editions.editions_page', event_name=event.name))
        else:
            form.name.errors = list(form.name.errors)+['vous utiliser deja ce nom.']
    return render_template('modify_edition.html', user_data=user, event_data=event, edition_data=edition, form = form, now=datetime.now(), event_modif=True, edition_sidebar=True)
