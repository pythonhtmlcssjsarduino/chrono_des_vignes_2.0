from flask_wtf import FlaskForm
from flask_app.models import User
from wtforms import StringField, PasswordField, SubmitField, EmailField, DateField
from flask_app.custum_validators import DataRequired, Length, EqualTo, DonTExist


class Login_form(FlaskForm):
    username = StringField('nom d\'utilisateur', validators=[
                           DataRequired(), Length(min=2, max=20)])
    password = PasswordField('mot de passe', validators=[DataRequired()])
    submit_btn = SubmitField('se connecter')


class Signup_form(FlaskForm):
    name = StringField('prénom', validators=[DataRequired(), Length(max=60)])
    lastname = StringField('nom', validators=[DataRequired(), Length(max=26)])
    username = StringField('nom d\'utilisateur', validators=[
                           DataRequired(), Length(min=2, max=20), DonTExist(User, 'username')])
    email = EmailField('email')
    phone = StringField('n de tel')
    datenaiss = DateField('date de naissance', validators=[DataRequired()])
    password = PasswordField('entrer un mot de passe', validators=[DataRequired(), Length(max=20)])
    repeatpassword = PasswordField('repeter le mot de passe', validators=[EqualTo('password')])
    submit_btn = SubmitField('se creer un compte')
