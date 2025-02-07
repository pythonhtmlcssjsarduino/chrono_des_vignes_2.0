from flask import Blueprint, flash, render_template, redirect, url_for, request, session, send_file
from flask_app import admin_required, db, set_route, socketio
from flask_app.admin.editions.form import Edition_form
from flask_login import login_required, current_user
from flask_app.models import  Event, Parcours, Edition, Inscription, User
from datetime import datetime
from flask_socketio import join_room, leave_room
from xlsxwriter import Workbook
from io import BytesIO
from flask_babel import _
from flask_app.custom_validators import DataRequired, Length, EqualTo, DonTExist, DbLength, Email
from .form import NewCoureurForm, ValidateNewCoureurForm
from sqlalchemy import func, and_, or_, not_

dossard = Blueprint('dossard', __name__, template_folder='templates')

@set_route(dossard, '/event/<event_name>/editions/<edition_name>/dossard', methods=['POST', 'GET'])
@login_required
@admin_required
def edition_dossards(event_name, edition_name):
    event : Event = Event.query.filter_by(name=event_name).first_or_404()
    edition : Edition= event.editions.filter_by(name=edition_name).first_or_404()
    user = current_user

    form = NewCoureurForm()
    choices = edition.parcours
    form.parcours.choices = [str((p.name, p.description)) for p in choices]

    if form.validate_on_submit():
        users = User.query.filter(and_(or_(func.lower(User.username)==func.lower(form.username.data),
                                and_(func.lower(User.name)==func.lower(form.name.data), func.lower(User.lastname)==func.lower(form.lastname.data))),
                            User.datenaiss==form.datenaiss.data)).all()
        if len(users) > 0:
            validate_form = ValidateNewCoureurForm()
        else:
            validate_form = None

            supp_validators = {
                'name':[DataRequired(), DbLength(User, 'name')],
                'lastname':[DataRequired(), DbLength(User, 'lastname')],
                'username':[DataRequired(), DbLength(User, 'username')],
                'email':[DataRequired(), DbLength(User, 'email'), Email()]
            }
            ic('first validation', form.validate(extra_validators=supp_validators), form.parcours.data)
            if form.validate(extra_validators=supp_validators):
                # create a new user with the form data and add it to all the parcours
                if form.username.data:
                    username = form.username.data
                else:
                    username = f'{form.name.data}.{form.lastname.data}'
                    nb = User.query.filter(User.username.contains(username)).count()
                    username += str(nb) if nb>0 else ''
                hash_pwd= 'dev' # ! ''.join(secrets.choice(alphabet) for _ in range(10))

                choices = event.parcours.filter(Parcours.name.in_([eval(data)[0] for data in form.parcours.data])).all()
                user = User(name=form.name.data,
                            lastname=form.lastname.data,
                            username=username,
                            email=form.email.data if form.email.data else None,
                            phone=form.phone.data if form.phone.data else None,
                            datenaiss= form.datenaiss.data,
                            password=hash_pwd)
                db.session.add(user)
                db.session.commit()
                db.session.refresh(user)
                inscriptions = []
                for parcours in choices:
                    inscriptions.append(Inscription(user_id = user.id,
                                                    event_id=event.id,
                                                    edition_id=edition.id,
                                                    parcours_id=parcours.id))
                db.session.add_all(inscriptions)
                db.session.commit()

    else:
        users = []
        validate_form = None

    return render_template('dossard.html', user_data=user, event_data=event, edition_data=edition, now=datetime.now(), inscriptions=edition.inscriptions, event_modif=True, edition_sidebar=True, form=form, validate_form=validate_form, validate_users=users)

@set_route(dossard, '/event/<event_name>/editions/<edition_name>/dossard/newuser', methods=['POST'])
@login_required
@admin_required
def validate_new_user(event_name, edition_name):
    '''
    validate a new user that is already registered in the database
    '''
    event = Event.query.filter_by(name=event_name).first_or_404()
    edition : Edition= event.editions.filter_by(name=edition_name).first_or_404()
    form = ValidateNewCoureurForm()
    form.parcours.choices = [str((p.name, p.description)) for p in edition.parcours]
    ic(form.parcours.data)
    if form.validate_on_submit():
        user = User.query.get_or_404(form.user_id.data)

        choices = event.parcours.filter(Parcours.name.in_([eval(data)[0] for data in form.parcours.data]),
                                        not_(Parcours.inscriptions.any(Inscription.user_id==user.id))).all()
        
        inscriptions = []
        for parcours in choices:
            inscriptions.append(Inscription(user_id = user.id,
                                            event_id=event.id,
                                            edition_id=edition.id,
                                            parcours_id=parcours.id))
        db.session.add_all(inscriptions)
        db.session.commit()

        flash(_('flash.success.newuser:username:name:lastname').format(username=user.username, name=user.name, lastname=user.lastname), 'success')

        return redirect(url_for('admin.editions.dossard.edition_dossards', event_name=event_name, edition_name=edition_name))
    else:
        return {'ok':False}

@socketio.on('connect', namespace='/dossard')
def dossard_connect(auth):
    if current_user.is_authenticated and auth.get('event_id') and auth.get('edition_id'):
        event:Event = Event.query.get(auth['event_id'])
        if not event or event.createur != current_user:
            return False # connection not allowed
        edition = event.editions.filter_by(id=auth['edition_id']).first()
        if not edition:
            return False # connection not allowed
    else:
        False # connection not allowed

@socketio.on('disconnect', namespace='/dossard')
def dossard_disconnect():
    pass

@socketio.on('change_dossard', namespace='/dossard')
def change_dossard(data):
    inscription = Inscription.query.get(data['inscription_id'])
    if (not inscription and isinstance(data['new_dossard'], int) and not current_user.is_authenticated and inscription.event.createur == current_user):
        return False
    if Inscription.query.filter(Inscription.dossard == data['new_dossard'], Inscription.edition==inscription.edition, Inscription.id!=inscription.id).first():
        return {'erreur':'dossard déjà utilisé'}
    inscription.dossard = data['new_dossard']
    db.session.commit()
    return True

@socketio.on('change_presence', namespace='/dossard')
def set_presence(data):
    if not data.get('presence') is not None or not data.get('inscription_id'):
        return False
    
    inscription:Inscription = Inscription.query.get(data['inscription_id'])
    if not inscription:
        return False
    if inscription.edition.edition_date>datetime.now():
        return False

    inscription.present = bool(data['presence'])
    db.session.commit()
    return True

@set_route(dossard, '/event/<event_name>/editions/<edition_name>/dossard/generate', methods=['POST', 'GET'])
@login_required
@admin_required
def generate_all_dossard(event_name, edition_name):
    event : Event = Event.query.filter_by(name=event_name).first_or_404()
    edition : Edition= event.editions.filter_by(name=edition_name).first_or_404()
    user = current_user

    dossard_nb = [inscription.dossard for inscription in edition.inscriptions.filter(Inscription.dossard!=None).all()]
    last_dossard = 1
    for inscription in edition.inscriptions.filter(Inscription.dossard==None).all():
        while last_dossard in dossard_nb:
            last_dossard+=1
        inscription.dossard = last_dossard
        last_dossard+=1
    db.session.commit()

    return redirect(url_for("admin.editions.dossard.edition_dossards", event_name=event.name, edition_name=edition.name))


# methode for download dossard as excel
@set_route(dossard, '/event/<event_name>/editions/<edition_name>/dossard/download', methods=['POST', 'GET'])
@login_required
@admin_required
def export_dossard(event_name, edition_name):
    event : Event = Event.query.filter_by(name=event_name).first_or_404()
    edition : Edition= event.editions.filter_by(name=edition_name).first_or_404()
    user = current_user

    buffer = BytesIO()

    workbook = Workbook(buffer)
    worksheet = workbook.add_worksheet()

    headers = [_('admin.editions.dossard.dossard'),
                _('admin.editions.dossard.name'), 
                _('admin.editions.dossard.lastname'), 
                _('admin.editions.dossard.email'), 
                _('admin.editions.dossard.phone'), 
                _('admin.editions.dossard.datenaiss'), 
                _('admin.editions.dossard.username'), 
                _('admin.editions.dossard.parcours'), 
                _('admin.editions.dossard.edition_date'), 
                _('admin.editions.dossard.edition_name'), 
                _('admin.editions.dossard.event_name')]

    row :int
    for row, inscription in enumerate(edition.inscriptions.all(), 1):
        # dossard, name, lastname, email, phone, datenaiss, username, parcours, edition_date, edition_name, event_name
        worksheet.write(row, 0, inscription.dossard)
        worksheet.write(row, 1, inscription.inscrit.name)
        worksheet.write(row, 2, inscription.inscrit.lastname)
        worksheet.write(row, 3, inscription.inscrit.email)
        worksheet.write(row, 4, inscription.inscrit.phone)
        worksheet.write(row, 5, inscription.inscrit.datenaiss)
        worksheet.write(row, 6, inscription.inscrit.username)
        worksheet.write(row, 7, inscription.parcours.name)
        worksheet.write(row, 8, inscription.edition.edition_date)
        worksheet.write(row, 9, inscription.edition.name)
        worksheet.write(row, 10, inscription.event.name)

    worksheet.add_table(0,0,max(edition.inscriptions.count(), 1),len(headers)-1, {'columns': [{'header': h} for h in headers], 'autofilter': False})
    worksheet.autofit()
    workbook.close()

    buffer.seek(0)
    return send_file(buffer, download_name='dossard.xlsx', as_attachment=True)
