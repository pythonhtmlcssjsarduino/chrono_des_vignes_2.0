from flask_wtf import FlaskForm
from flask_app.models import User
from wtforms import StringField, PasswordField, SubmitField, EmailField, DateField
from flask_app.custom_validators import DataRequired, Length, EqualTo, DonTExist
from flask_app.custom_field import MultiCheckboxFieldWithDescription
from flask_babel import lazy_gettext as _


class Login_form(FlaskForm):
    username = StringField(_('form.username'), validators=[
                           DataRequired(), Length(min=2, max=20)])
    password = PasswordField(_('form.pwd'), validators=[DataRequired()])
    submit_btn = SubmitField(_('form.connect'))


class Signup_form(FlaskForm):
    name = StringField(_('form.name'), validators=[DataRequired(), Length(max=60)])
    lastname = StringField(_('form.lastname'), validators=[DataRequired(), Length(max=26)])
    username = StringField(_('form.username'), validators=[
                           DataRequired(), Length(min=2, max=20), DonTExist(User, 'username')])
    email = EmailField(_('form.email'))
    phone = StringField(_('form.tel'))
    datenaiss = DateField(_('form.birth'), validators=[DataRequired()])
    password = PasswordField(_('form.pwd'), validators=[DataRequired(), Length(max=20)])
    repeatpassword = PasswordField(_('form.repetepwd'), validators=[EqualTo('password')])
    submit_btn = SubmitField(_('form.createaccount'))

class Inscription_connected_form(FlaskForm):
    parcours = MultiCheckboxFieldWithDescription(_('form.choosedparcours'), validators=[DataRequired()])

    submit_btn = SubmitField(_('form.register'))

class Inscription_form(FlaskForm):
    name = StringField(_('form.name'), validators=[DataRequired(), Length(max=60)])
    lastname = StringField(_('form.lastname'), validators=[DataRequired(), Length(max=26)])
    email = EmailField(_('form.email'))
    phone = StringField(_('form.tel'))
    datenaiss = DateField(_('form.birth'), validators=[DataRequired()])

    parcours = MultiCheckboxFieldWithDescription(_('form.choosedparcours'), validators=[DataRequired()])

    submit_btn = SubmitField(_('form.register'))

class ModifyForm(FlaskForm):
    name = StringField(_('form.name'), validators=[DataRequired(), Length(max=60)])
    lastname = StringField(_('form.lastname'), validators=[DataRequired(), Length(max=26)])
    username = StringField(_('form.username'), validators=[DataRequired(), Length(min=2, max=20)])
    email = EmailField(_('form.email'))
    phone = StringField(_('form.tel'))
    datenaiss = DateField(_('form.birth'), validators=[DataRequired()])
    submit_btn = SubmitField(_('form.modifyaccount'))