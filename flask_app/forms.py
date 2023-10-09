from flask_wtf import FlaskForm
from flask_app.models import User, Edition, Parcours
from wtforms import StringField, PasswordField, SubmitField, EmailField, DateField, DateTimeLocalField, FloatField
from flask_app.custum_validators import DataRequired, Length, EqualTo, DateTimeNotPast, DateTimeBefore, DonTExist

class Login_form(FlaskForm):
    username = StringField('nom d\'utilisateur', validators=[
                           DataRequired(), Length(min=2, max=20)])
    password = PasswordField('mot de passe', validators=[DataRequired()])
    submit = SubmitField('se connecter')


class Signup_form(FlaskForm):
    name = StringField('nom', validators=[DataRequired(), Length(max=60)])
    lastname = StringField('prénom', validators=[DataRequired(), Length(max=26)])
    username = StringField('nom d\'utilisateur', validators=[
                           DataRequired(), Length(min=2, max=20), DonTExist(User, 'username')], render_kw={'placeholder':'coucou'})
    email = EmailField('email')
    phone = StringField('n de tel')
    datenaiss = DateField('date de naissance', validators=[DataRequired()])
    password = PasswordField('entrer un mot de passe', validators=[DataRequired(), Length(max=20)])
    repeatpassword = PasswordField('repeter le mot de passe', validators=[EqualTo('password')])
    submit = SubmitField('se creer un compte')

class Edition_form(FlaskForm):
    name = StringField('nom de l\'edition', validators=[DataRequired(), Length(max=20), DonTExist(Edition, 'name')])
    edition_date = DateTimeLocalField('date le l\'edition', format='%Y-%m-%dT%H:%M', render_kw={}, validators=[DataRequired(), DateTimeNotPast()])
    first_inscription = DateTimeLocalField('date d\'ouverture des inscriptions', format='%Y-%m-%dT%H:%M', render_kw={}, validators=[DataRequired(), DateTimeNotPast(), DateTimeBefore('last_inscription')])
    last_inscription = DateTimeLocalField('date de fermeture des inscriptions', format='%Y-%m-%dT%H:%M', render_kw={}, validators=[DataRequired(), DateTimeNotPast(), DateTimeBefore('edition_date')])
    rdv_lat= FloatField('latitude du point de rendez vous', validators=[DataRequired()], default=46.58)
    rdv_lng= FloatField('longitude du point de rendez vous', validators=[DataRequired()], default=6.52)
    submit = SubmitField('sauvegarder')


class Parcours_name_form(FlaskForm):
    name= StringField('nom du parcours', validators=[DataRequired(), DonTExist(Parcours, 'name')])
    submit=SubmitField('sauvegarder')

