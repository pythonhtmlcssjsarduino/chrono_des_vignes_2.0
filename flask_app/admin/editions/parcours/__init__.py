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

parcours = Blueprint('parcours', __name__, template_folder='templates')

@set_route(parcours, '/event/<event_name>/editions/<edition_name>/parcours')
@login_required
@admin_required
def view(event_name, edition_name):
    user = current_user
    event = Event.query.filter_by(name=event_name).first_or_404()
    edition:Edition = event.editions.filter_by(name=edition_name).first_or_404()
    parcours = edition.parcours
    return render_template('edition_parcours.html', parcours_data=parcours, edition_data = edition, event_data=event, user_data=user, event_modif=True, edition_sidebar=True)

