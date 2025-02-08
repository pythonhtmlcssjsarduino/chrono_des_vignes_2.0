from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeLocalField, FloatField, SubmitField, TextAreaField
from chrono_des_vignes.custom_validators import DataRequired, Length, DateTimeNotPast, DateTimeBefore, InputRequired
from chrono_des_vignes.custom_field import MultiCheckboxFieldWithDescription
from flask_babel import lazy_gettext as _


class EventForm(FlaskForm):
    description = TextAreaField(_('form.eventdescription'), render_kw={'style':'height:400px'})
    submit_btn = SubmitField(_('form.save'))