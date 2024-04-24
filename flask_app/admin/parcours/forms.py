from flask_wtf import FlaskForm
from flask_app.models import  Parcours, Stand
from wtforms import StringField, SubmitField, DecimalField, BooleanField
from flask_app.custum_validators import DataRequired, DonTExist, InputRequired

class Parcours_name_form(FlaskForm):
    name= StringField('nom du parcours', validators=[DataRequired(), DonTExist(Parcours, 'name')])
    submit_btn=SubmitField('sauvegarder')

class Stand_modif_form(FlaskForm):
    name = StringField('nom du stand', validators=[DataRequired(), DonTExist(Stand, 'name')])
    lat = DecimalField('latidude du stand', validators=[InputRequired()], places=None)
    lng = DecimalField('longitude du stand', validators=[InputRequired()], places=None)
    color = StringField('couleur du stand', validators=[DataRequired()], default='#f00')
    chrono = BooleanField('activer le chronometrage du stand', validators=[])
    submit_btn = SubmitField('enregistrer')

class Etape_modif_form(FlaskForm):
    name = StringField('nom de l\'etape', validators=[DataRequired(), DonTExist(Stand, 'name')])
    path = StringField('path', validators=[DataRequired()])
    submit_btn = SubmitField('enregistrer')