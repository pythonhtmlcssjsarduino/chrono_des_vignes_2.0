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

from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeLocalField, FloatField, SubmitField, TextAreaField
from chrono_des_vignes.custom_validators import DataRequired, Length, DateTimeNotPast, DateTimeBefore, InputRequired
from chrono_des_vignes.custom_field import MultiCheckboxFieldWithDescription
from flask_babel import lazy_gettext as _

class Edition_form(FlaskForm):
    name = StringField(_('form.edition_name'), validators=[DataRequired(), Length(max=40)])
    edition_date = DateTimeLocalField(_('form.edition_date'), format='%Y-%m-%dT%H:%M', render_kw={}, validators=[DataRequired(), DateTimeNotPast()])
    description = TextAreaField(_('form.description'), render_kw={'style':'height:200px'})
    parcours = MultiCheckboxFieldWithDescription(_('form.parcours'), validators=[DataRequired()])
    first_inscription = DateTimeLocalField(_('form.firstinscriptiondate'), format='%Y-%m-%dT%H:%M', render_kw={}, validators=[DataRequired(), DateTimeNotPast(), DateTimeBefore('last_inscription')])
    last_inscription = DateTimeLocalField(_('form.lastinscriptiondate'), format='%Y-%m-%dT%H:%M', render_kw={}, validators=[DataRequired(), DateTimeNotPast(), DateTimeBefore('edition_date')])
    rdv_lat= FloatField(_('form.rdvlng'), validators=[DataRequired()], default=46.54685605692591)
    rdv_lng= FloatField(_('form.rdvlat'), validators=[DataRequired()], default=6.449900437449806)
    submit_btn = SubmitField(_('form.save'))