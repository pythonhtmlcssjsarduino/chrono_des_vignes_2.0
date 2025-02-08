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
    rdv_lat= FloatField(_('form.rdvlng'), validators=[DataRequired()], default=0)
    rdv_lng= FloatField(_('form.rdvlat'), validators=[DataRequired()], default=0)
    submit_btn = SubmitField(_('form.save'))