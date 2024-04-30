from flask import Blueprint, flash, render_template, redirect, request
from flask_app import admin_required, db
from flask_app.admin.editions.forms import Edition_form
from flask_login import login_required, current_user
from flask_app.models import  Event
from datetime import datetime

editions = Blueprint('editions', __name__, template_folder='templates')

@editions.route('/event/<event_name>/editions')
@login_required
@admin_required
def editions_page(event_name):
    # * page to access the differents editions of the event
    event_data = Event.query.filter_by(name=event_name).first()
    user = current_user
    return render_template("editions.html", user_data=user, event_data=event_data)

@editions.route('/event/<event_name>/editions/<edition_name>', methods=['POST', 'GET'])
@login_required
@admin_required
def modify_edition_page(event_name, edition_name):
    event = Event.query.filter_by(name=event_name).first_or_404()
    edition= event.editions.filter_by(name=edition_name).first_or_404()
    user = current_user
    form = Edition_form(data={'name':edition.name,
                              'edition_date':edition.edition_date,
                              'first_inscription':edition.first_inscription,
                              'last_inscription':edition.last_inscription,
                              'rdv_lat':edition.rdv_lat,
                              'rdv_lng':edition.rdv_lng})


    #? desactiver le champs si dates deja passé
    form.edition_date.render_kw.pop("disabled", None)
    form.first_inscription.render_kw.pop("disabled", None)
    form.last_inscription.render_kw.pop("disabled", None)
    if edition.edition_date < datetime.now():
        form.edition_date.render_kw["disabled"]= "disabled"
    if edition.first_inscription < datetime.now():
        form.first_inscription.render_kw["disabled"]= "disabled"
    if edition.last_inscription < datetime.now():
        form.last_inscription.render_kw["disabled"]= "disabled"
    #? fin desactivation des champs


    if form.validate_on_submit():
        if form.name.data == edition.name or not event.editions.filter_by(name=form.name.data).first():
            edition.name = form.name.data
            edition.edition_date = form.edition_date.data
            edition.first_inscription = form.first_inscription.data
            edition.last_inscription = form.last_inscription.data
            edition.rdv_lat = form.rdv_lat.data
            edition.rdv_lng = form.rdv_lng.data
            db.session.commit()
            flash('l\'edition a bien été mise a jour.', 'success')
        else:
            form.name.errors = list(form.name.errors)+['vous utiliser deja ce nom.']
    return render_template('modify_edition.html', user_data=user, event_data=event, edition_data=edition, form = form)
