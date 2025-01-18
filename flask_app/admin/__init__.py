from flask import Blueprint, render_template, flash
from flask_login import login_required, current_user
from flask_app import admin_required, set_route, db
from flask_app.models import Event
from .form import EventForm
from .editions import editions
from .parcours import parcours_bp
from .coureurs import coureurs

admin = Blueprint('admin', __name__, template_folder='templates')
admin.register_blueprint(parcours_bp)
admin.register_blueprint(editions)
admin.register_blueprint(coureurs)


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

