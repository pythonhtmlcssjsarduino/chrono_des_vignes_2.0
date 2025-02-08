from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, DateTimeField, IntegerField, FloatField, FieldList
from chrono_des_vignes.custom_validators import DataRequired, Length, DateTimeNotPast, DateTimeBefore, InputRequired
from flask_babel import lazy_gettext as _

class NewKeyForm(FlaskForm):
    name = StringField(_('form.lastname'), validators=[DataRequired(), Length(max=40)])
    stands = FieldList(SelectField(_('form.stand')))
    submit_btn= SubmitField('form.create')

class ChronoLoginForm(FlaskForm):
    key = StringField(_('form.key'), validators=[DataRequired()])
    submit_btn= SubmitField(_('form.validate'))
