from flask import Blueprint, render_template
from flask_login import login_required, current_user
from flask_app import admin_required
from flask_app.models import Event
from flask_app.admin.editions import editions
from flask_app.admin.parcours import parcours
from flask_app.admin.coureurs import coureurs

admin = Blueprint('admin', __name__, template_folder='templates')
admin.register_blueprint(parcours)
admin.register_blueprint(editions)
admin.register_blueprint(coureurs)


@admin.route('/event/<event_name>')
@login_required
@admin_required
def home_event(event_name):
    #* page to access and modify an event
    event_data = Event.query.filter_by(name=event_name).first()
    user = current_user
    return render_template("home_event.html", user_data=user, event_data=event_data, event_modif=True)

