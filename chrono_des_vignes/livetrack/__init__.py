'''
# Chrono Des Vignes
# a timing system for sports events
# 
# Copyright © 2025 Romain Maurer
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

from flask import Blueprint, render_template
from chrono_des_vignes import app, set_route
from chrono_des_vignes.models import Inscription, Passage
from chrono_des_vignes.lib import format_timedelta

livetrack = Blueprint('livetrack', __name__, template_folder='templates')

def get_run_result(inscription:Inscription, json=False)->list[dict]:
    data = []

    user_passages:list[Passage] = inscription.passages.order_by(Passage.time_stamp.asc()).all()
    if len(user_passages)>0:
        first_passage = user_passages[0]
        last_time = first_passage.time_stamp
        last_dist = 0
        current=False
        for stand, dist in zip(inscription.parcours.iter_chrono_list(), inscription.parcours.get_chrono_dists()):
            if len(user_passages)>0 and stand == user_passages[0].get_stand():
                delta=user_passages[0].time_stamp-first_passage.time_stamp
                time_delta = format_timedelta(user_passages[0].time_stamp-last_time)
                dist_delta = round(dist-last_dist, 3)
                last_dist = dist
                last_time = user_passages[0].time_stamp
                user_passages.pop(0)
                success=True
            elif len(user_passages)>0:
                delta=None
                success=False
                time_delta = None
                dist_delta = None
            else:
                if not current:
                    current=True
                    data[-1]['current']=True
                success=None
                delta=None
                time_delta = None
                dist_delta = None

            data.append({'stand':stand if not json else {'name':stand.name}, 'dist':round(dist, 3), 'time':format_timedelta(delta) if delta is not None else None, 'success':success, 'time_delta':time_delta, 'dist_delta':dist_delta})
        for p in user_passages:
            success=None
            delta = p.time_stamp-first_passage.time_stamp
            data.append({'stand':p.get_stand() if not json else {'name':p.get_stand().name}, 'dist':None, 'time':format_timedelta(delta), 'success':success, 'time_delta':format_timedelta(p.time_stamp-last_time), 'dist_delta':None})
            last_time = p.time_stamp
        if not current:
            data[-1]['current']=True
    return data

@set_route(livetrack, '/livetrack/<inscription_id>')
def livetrack_page(inscription_id):
    inscription:Inscription = Inscription.query.get_or_404(inscription_id)

    ic(get_run_result(inscription))

    return render_template('livetrack.html', inscription=inscription, run=get_run_result(inscription))
