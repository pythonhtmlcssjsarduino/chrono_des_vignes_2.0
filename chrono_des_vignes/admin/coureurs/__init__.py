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

from flask import Blueprint, render_template, Response
from flask_login import current_user, login_required
from chrono_des_vignes import admin_required, set_route
from chrono_des_vignes.models import Event, User
from flask_babel import _

coureurs = Blueprint("coureurs", __name__, template_folder='templates')

@set_route(coureurs, '/event/<event_name>/coureurs')
@login_required
@admin_required
def coureurs_page(event_name: str)->str|Response:
    # * page to access the different runner that will or had participate to the event
    event_data = Event.query.filter_by(name=event_name).first()
    user = current_user
    return render_template("coureurs.html", user_data=user, event_data=event_data, event_modif=True)

@set_route(coureurs, '/event/<event_name>/coureurs/<coureur>')
def view_coureur_page(event_name:str, coureur: str)->str|Response:
    event_data = Event.query.filter_by(name=event_name).first()
    coureur_data:User = User.query.get_or_404(coureur, _('admin.view.error.coureurdontexist:coureur').format(coureur=coureur))
    inscriptions = coureur_data.inscriptions.filter_by(event=event_data).all()
    user = current_user
    return render_template("view_coureur.html", user_data=user, event_data=event_data, coureur_data = coureur_data, inscriptions=inscriptions, event_modif=True)
