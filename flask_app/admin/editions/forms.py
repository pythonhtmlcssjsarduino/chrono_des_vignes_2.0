from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeLocalField, FloatField, SubmitField
from flask_app.custum_validators import DataRequired, Length, DonTExist, DateTimeNotPast, DateTimeBefore
from flask_app.models import Edition

class Edition_form(FlaskForm):
    name = StringField('nom de l\'edition', validators=[DataRequired(), Length(max=20), DonTExist(Edition, 'name')])
    edition_date = DateTimeLocalField('date le l\'edition', format='%Y-%m-%dT%H:%M', render_kw={}, validators=[DataRequired(), DateTimeNotPast()])
    first_inscription = DateTimeLocalField('date d\'ouverture des inscriptions', format='%Y-%m-%dT%H:%M', render_kw={}, validators=[DataRequired(), DateTimeNotPast(), DateTimeBefore('last_inscription')])
    last_inscription = DateTimeLocalField('date de fermeture des inscriptions', format='%Y-%m-%dT%H:%M', render_kw={}, validators=[DataRequired(), DateTimeNotPast(), DateTimeBefore('edition_date')])
    rdv_lat= FloatField('latitude du point de rendez vous', validators=[DataRequired()], default=46.58)
    rdv_lng= FloatField('longitude du point de rendez vous', validators=[DataRequired()], default=6.52)
    submit_btn = SubmitField('sauvegarder')
