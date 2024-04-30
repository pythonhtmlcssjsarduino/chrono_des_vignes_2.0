from flask import Blueprint, render_template
from flask_login import current_user, login_required
from flask_app import admin_required
from flask_app.models import Event, User

coureurs = Blueprint("coureurs", __name__, template_folder='templates')

@coureurs.route('/event/<event_name>/coureurs')
@login_required
@admin_required
def coureurs_page(event_name):
    # * page to access the different runner that will or had participate to the event
    event_data = Event.query.filter_by(name=event_name).first()
    user = current_user
    return render_template("coureurs.html", user_data=user, event_data=event_data)

@coureurs.route('/event/<event_name>/coureurs/<coureur>')
def view_coureur_page(event_name, coureur):
    event_data = Event.query.filter_by(name=event_name).first()
    coureur_data:User = User.query.get_or_404(coureur, f'le coureur ayans l\'id {coureur} n\'existe pas.')
    inscriptions = coureur_data.inscriptions.filter_by(event=event_data).all()
    user = current_user
    return render_template("view_coureur.html", user_data=user, event_data=event_data, coureur_data = coureur_data, inscriptions=inscriptions)
