from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField, BooleanField, TextAreaField
from flask_app.custom_validators import DataRequired, InputRequired, Length

class Parcours_name_form(FlaskForm):
    name= StringField('nom du parcours', validators=[DataRequired(), Length(max=40)])
    description = TextAreaField('description', validators=[], default='')
    submit_btn=SubmitField('sauvegarder')

class Stand_modif_form(FlaskForm):
    name = StringField('nom du stand', validators=[DataRequired(), Length(max=40)])
    lat = DecimalField('latidude du stand', validators=[InputRequired()], places=None)
    lng = DecimalField('longitude du stand', validators=[InputRequired()], places=None)
    color = StringField('couleur du stand', validators=[DataRequired()], default='#f00')
    chrono = BooleanField('activer le chronometrage du stand', validators=[])
    submit_btn = SubmitField('enregistrer')

class Etape_modif_form(FlaskForm):
    name = StringField('nom de l\'etape', validators=[DataRequired(), Length(max=40)])
    path = StringField('path', validators=[DataRequired()])
    submit_btn = SubmitField('enregistrer')

class New_parcours_form(FlaskForm):
    name = StringField('nom du parcours', validators=[DataRequired(), Length(max=40)])
    start_lat = DecimalField('latidude du depart', validators=[InputRequired()], places=None)
    start_lng = DecimalField('longitude du depart', validators=[InputRequired()], places=None)

    submit_btn = SubmitField('créer')