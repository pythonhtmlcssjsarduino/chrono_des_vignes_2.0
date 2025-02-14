from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeLocalField, FloatField, SubmitField, TextAreaField, EmailField, DateField, IntegerField, TelField
from chrono_des_vignes.custom_validators import DataRequired, Length, DateTimeNotPast, DateTimeBefore, InputRequired, Email
from chrono_des_vignes.custom_field import MultiCheckboxFieldWithDescription
from flask_babel import lazy_gettext as _
from chrono_des_vignes.models import User
from wtforms.validators import Optional
from chrono_des_vignes.custom_validators import DbLength

class NewCoureurForm(FlaskForm):
    name = StringField(_('form.name'), validators=[DbLength(table=User, column='name')])
    lastname = StringField(_('form.lastname'), validators=[DbLength(table=User, column='lastname')])
    username = StringField(_('form.username'))
    email = EmailField(_('form.email'), validators=[Optional(), Email()])
    phone = TelField(_('form.tel'))
    datenaiss = DateField(_('form.birth'), validators=[DataRequired()])

    parcours = MultiCheckboxFieldWithDescription(_('form.choosedparcours'), validators=[DataRequired()])

    submit_btn = SubmitField(_('form.register'))

class ValidateNewCoureurForm(FlaskForm):
    user_id = IntegerField('user_id', validators=[DataRequired()])
    
    name = StringField(_('form.name'), validators=[DbLength(table=User, column='name')])
    lastname = StringField(_('form.lastname'), validators=[DbLength(table=User, column='lastname')])
    username = StringField(_('form.username'))
    email = EmailField(_('form.email'), validators=[Optional(), Email()])
    phone = TelField(_('form.tel'))
    datenaiss = DateField(_('form.birth'), validators=[DataRequired()])

    parcours = MultiCheckboxFieldWithDescription(_('form.choosedparcours'), validators=[DataRequired()])