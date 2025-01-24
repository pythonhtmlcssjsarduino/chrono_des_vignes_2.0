from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField, BooleanField, TextAreaField
from flask_app.custom_validators import DataRequired, InputRequired, Length
from flask_app.custom_field import ColorField
from flask_babel import lazy_gettext as _

class Parcours_name_form(FlaskForm):
    name= StringField(_('form.parcoursname'), validators=[DataRequired(), Length(max=40)])
    description = TextAreaField(_('form.parcoursdescription'), validators=[], default='', render_kw={'style':'height:200px'})
    submit_btn=SubmitField(_('form.save'))

class Stand_modif_form(FlaskForm):
    name = StringField(_('form.standname'), validators=[DataRequired(), Length(max=40)])
    lat = DecimalField(_('form.standlat'), validators=[InputRequired()], places=None)
    lng = DecimalField(_('form.standlng'), validators=[InputRequired()], places=None)
    color = ColorField(_('form.standcouleur'), validators=[DataRequired()], default='#ff0000')
    chrono = BooleanField(_('form.chrono'), validators=[])
    submit_btn = SubmitField(_('form.save'))

class Etape_modif_form(FlaskForm):
    name = StringField(_('form.etapename'), validators=[DataRequired(), Length(max=40)])
    path = StringField(_('form.path'), validators=[DataRequired()])
    submit_btn = SubmitField(_('form.save'))

class New_parcours_form(FlaskForm):
    name = StringField(_('form.parcoursname'), validators=[DataRequired(), Length(max=40)])
    start_lat = DecimalField(_('form.startlat'), validators=[InputRequired()], places=None)
    start_lng = DecimalField(_('form.startlng'), validators=[InputRequired()], places=None)

    submit_btn = SubmitField(_('form.create'))