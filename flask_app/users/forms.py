from flask_wtf import FlaskForm
from flask_app.models import User
from wtforms import StringField, PasswordField, SubmitField, EmailField, DateField
from flask_wtf.file import FileField, FileAllowed
from flask_app.custom_validators import DataRequired, Length, EqualTo, DonTExist, DbLength
from flask_app.custom_field import MultiCheckboxFieldWithDescription
from flask_babel import lazy_gettext as _


class Login_form(FlaskForm):
    username = StringField(_('form.username'), validators=[
                           DataRequired(), DbLength(min=2, table=User, column='username')])
    password = PasswordField(_('form.pwd'), validators=[DataRequired()])
    submit_btn = SubmitField(_('form.connect'))

class Signup_form(FlaskForm):
    name = StringField(_('form.name'), validators=[DataRequired(), DbLength(table=User, column='name')])
    lastname = StringField(_('form.lastname'), validators=[DataRequired(), DbLength(table=User, column='lastname')])
    username = StringField(_('form.username'), validators=[
                           DataRequired(), DbLength(min=2, table=User, column='username')])
    email = EmailField(_('form.email'))
    phone = StringField(_('form.tel'))
    datenaiss = DateField(_('form.birth'), validators=[DataRequired()])
    password = PasswordField(_('form.pwd'), validators=[DataRequired(), DbLength(table=User, column='password')])
    repeatpassword = PasswordField(_('form.repetepwd'), validators=[EqualTo('password')])
    submit_btn = SubmitField(_('form.createaccount'))

class Inscription_connected_form(FlaskForm):
    parcours = MultiCheckboxFieldWithDescription(_('form.choosedparcours'), validators=[DataRequired()])

    submit_btn = SubmitField(_('form.register'))

class Inscription_form(FlaskForm):
    name = StringField(_('form.name'), validators=[DataRequired(), DbLength(table=User, column='name')])
    lastname = StringField(_('form.lastname'), validators=[DataRequired(), DbLength(table=User, column='lastname')])
    email = EmailField(_('form.email'))
    phone = StringField(_('form.tel'))
    datenaiss = DateField(_('form.birth'), validators=[DataRequired()])

    parcours = MultiCheckboxFieldWithDescription(_('form.choosedparcours'), validators=[DataRequired()])

    submit_btn = SubmitField(_('form.register'))

class ModifyForm(FlaskForm):
    name = StringField(_('form.name'), validators=[DataRequired(), DbLength(table=User, column='name')])
    lastname = StringField(_('form.lastname'), validators=[DataRequired(), DbLength(table=User, column='lastname')])
    username = StringField(_('form.username'), validators=[DataRequired(), DbLength(min=2, table=User, column='username')])
    email = EmailField(_('form.email'))
    phone = StringField(_('form.tel'))
    datenaiss = DateField(_('form.birth'), validators=[DataRequired()])
    profil_pic = FileField(_('form.profilpic'), validators=[FileAllowed(['jpg', 'png'])])
    submit_btn = SubmitField(_('form.modifyaccount'))