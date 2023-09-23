from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, TelField, DateField
from flask_app.custum_validators import DataRequired, Length, EqualTo

class Login_form(FlaskForm):
    username = StringField('nom d\'utilisateur', validators=[
                           DataRequired(), Length(min=2, max=20)])
    password = PasswordField('mot de passe', validators=[DataRequired()])
    submit = SubmitField('se connecter')


class Signup_form(FlaskForm):
    name = StringField('nom', validators=[DataRequired(), Length(max=60)])
    lastname = StringField('prénom', validators=[DataRequired(), Length(max=26)])
    username = StringField('nom d\'utilisateur', validators=[
                           DataRequired(), Length(min=2, max=20)], render_kw={'placeholder':'coucou'})
    email = EmailField('email')
    phone = StringField('n de tel')
    datenaiss = DateField('date de naissance', validators=[DataRequired()])
    password = PasswordField('entrer un mot de passe', validators=[DataRequired(), Length(max=20)])
    repeatpassword = PasswordField('repeter le mot de passe', validators=[EqualTo('password')])
    submit = SubmitField('se creer un compte')
