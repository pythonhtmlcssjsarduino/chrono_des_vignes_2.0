from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, DateTimeField, IntegerField, FloatField, FieldList
from flask_app.custom_validators import DataRequired, Length, DateTimeNotPast, DateTimeBefore, InputRequired

class NewKeyForm(FlaskForm):
    name = StringField('nom', validators=[DataRequired(), Length(max=40)])
    stands = FieldList(SelectField('stand'))
    submit_btn= SubmitField('créer')

class ChronoLoginForm(FlaskForm):
    key = StringField('clé', validators=[DataRequired()])
    submit_btn= SubmitField('valider')
