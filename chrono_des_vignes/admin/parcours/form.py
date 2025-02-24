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
from wtforms import StringField, SubmitField, FloatField, BooleanField, TextAreaField
from chrono_des_vignes.custom_validators import DataRequired, InputRequired, Length
from chrono_des_vignes.custom_field import ColorField
from flask_babel import lazy_gettext as _

class Parcours_name_form(FlaskForm):
    name= StringField(_('form.parcoursname'), validators=[DataRequired(), Length(max=40)])
    description = TextAreaField(_('form.parcoursdescription'), validators=[], default='', render_kw={'style':'height:200px'})
    submit_btn=SubmitField(_('form.save'))

class Stand_modif_form(FlaskForm):
    name = StringField(_('form.standname'), validators=[DataRequired(), Length(max=40)])
    lat = FloatField(_('form.standlat'), validators=[InputRequired()])
    lng = FloatField(_('form.standlng'), validators=[InputRequired()])
    color = ColorField(_('form.standcouleur'), validators=[DataRequired()], default='#ff0000')
    chrono = BooleanField(_('form.chrono'), validators=[])
    submit_btn = SubmitField(_('form.save'))

class Etape_modif_form(FlaskForm):
    name = StringField(_('form.etapename'), validators=[DataRequired(), Length(max=40)])
    path = StringField(_('form.path'), validators=[DataRequired()])
    submit_btn = SubmitField(_('form.save'))

class New_parcours_form(FlaskForm):
    name = StringField(_('form.parcoursname'), validators=[DataRequired(), Length(max=40)])
    start_lat = FloatField(_('form.startlat'), validators=[InputRequired()])
    start_lng = FloatField(_('form.startlng'), validators=[InputRequired()])

    submit_btn = SubmitField(_('form.create'))