from flask import Blueprint, flash, render_template, redirect, url_for
from flask_app import admin_required, db
from flask_app.admin.editions.forms import Edition_form
from flask_login import login_required, current_user
from flask_app.models import  Event, Parcours, Edition
from datetime import datetime

dossard = Blueprint('dossard', __name__, template_folder='templates')

@dossard.route('/event/<event_name>/editions/<edition_name>/dossard', methods=['POST', 'GET'])
@login_required
@admin_required
def dossard_page(event_name, edition_name):
    user = current_user
    return render_template('dossard.html', user_data=user, pyscript=True)