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

from flask import Blueprint, render_template, flash, redirect
from flask_login import login_required, current_user
from chrono_des_vignes import admin_required, set_route, db, lang_url_for as url_for, app
from chrono_des_vignes.models import Event
from .form import EventForm, NewEventForm
from .editions import editions
from .parcours import parcours_bp
from .coureurs import coureurs

admin = Blueprint('admin', __name__, template_folder='templates')
admin.register_blueprint(parcours_bp)
admin.register_blueprint(editions)
admin.register_blueprint(coureurs)


@set_route(admin, '/event/<event_name>/delete', methods=['POST'])
@login_required
@admin_required
def delete_event(event_name):
    event:Event = Event.query.filter_by(name=event_name).first_or_404()
    if event.parcours.count() or event.editions.count():
        flash(_('flash.event_not_deleted'), 'danger')
        return redirect(url_for('admin.home_event', event_name=event.name))
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for('home'))

@admin.route('/event/new', methods=['POST'])
@login_required
@admin_required
def new_event():

    user = current_user
    form = NewEventForm()
    ic('coucou')

    if form.validate_on_submit():
        name=form.name.data
        ic(name)

        event = Event(name=name, createur_id=user.id)
        db.session.add(event)
        db.session.commit()

        return redirect(url_for('admin.home_event', event_name=event.name))
    else:
        ic(form.errors)
        for error in form.name.errors:
            flash(error, 'danger')
        return redirect(url_for('home'))


@set_route(admin, '/event/<event_name>', methods=['POST', 'GET'])
@login_required
@admin_required
def home_event(event_name):
    #* page to access and modify an event
    event_data:Event = Event.query.filter_by(name=event_name).first()
    user = current_user

    event_form = EventForm(data={
        'description':event_data.description
    })

    if event_form.validate_on_submit():
        event_data.description = event_form.description.data
        db.session.commit()
        flash('l\'évenement a bien été mise a jour.', 'success')

    return render_template("home_event.html", user_data=user, event_data=event_data, form=event_form, event_modif=True)
