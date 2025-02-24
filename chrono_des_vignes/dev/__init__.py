'''
# Chrono Des Vignes
# a timing system for sports events
# 
# Copyright © 2024-2025 Romain Maurer
# This file is part of Chrono Des Vignes
# 
# Chrono Des Vignes is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# 
# Chrono Des Vignes is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with Foobar.
# If not, see <https://www.gnu.org/licenses/>.
# 
# You may contact me at chrono-des-vignes@ikmail.com
'''

from flask import Blueprint, redirect, render_template, flash, jsonify, request, abort
from chrono_des_vignes import admin_required, db, app, LANGAGES, lang_url_for as url_for
from functools import wraps
import glob, os
from babel.messages.pofile import read_po, write_po
from babel.messages.catalog import Catalog
from io import StringIO
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from chrono_des_vignes.custom_validators import DataRequired


class langForm(FlaskForm):
    data = StringField('data', validators=[DataRequired()])
    submit_btn = SubmitField('submit')

def dev_required(func):
    """
    Modified login_required decorator to restrict access to dev
    """

    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not app.debug:
            flash('dev is not enable')
            return abort(404)
        return func(*args, **kwargs)
    return decorated_view

dev = Blueprint('dev', __name__, template_folder='template', subdomain='dev')

@dev.route('/error/<int:code>')
@dev_required
def error(code):
    abort(code)

@dev.route('/')
@dev_required
def dev_home():
    return render_template('dev_home.html')

def create_cfg():
    files = ''
    for ext, name in (('py', 'python'), ('html', 'jinja2')):
        for path in glob.iglob(f'{app.root_path}/**/*.{ext}', recursive=True):
            files += f'\n[{name}: {os.path.relpath(path)}]'.replace('\\', '/')


    with open(f'{app.root_path}/babel.cfg', '+w') as file:
        file.write(files)

def export_strings(source='en', target:list[str]=None):
    target = target if target else LANGAGES
    with open(f'{app.root_path}/translations/{source}/LC_MESSAGES/messages.po', 'r', encoding='utf-8') as file:
        source_str = StringIO(file.read())
    source_catalog = read_po(source_str)
    for_tron = { message.id: {source: message.string}
                 for message in source_catalog if message.id }

    for locale in target:
        if locale != source:
            with open(f'{app.root_path}/translations/{locale}/LC_MESSAGES/messages.po', 'r', encoding='utf-8') as file:
                target_str = StringIO( file.read())
            target_catalog = read_po(target_str)

            for message in target_catalog:
                if message.id and message.id in for_tron.keys():
                    for_tron[message.id][locale]=message.string

    return for_tron

@dev.route('/lang_json/<lang_id>', methods=['get', 'post'])
@dev_required
def lang_json(lang_id):
    langs = export_strings(source='fr', target=[lang for lang in LANGAGES if lang not in ('ids', 'pseudo')])

    return jsonify({lang['fr']: lang[lang_id] for lang in langs.values()})

# @dev.route('/save_lang')
# @dev_required
# def save_lang():
#     data = {"+ distance": "+ distance","+ temps": "+ time","Les inscriptions ne sont pas encore ouvertes!": "Registrations are not yet open!","Les inscriptions ne sont pas encore ouvertes! Elles ouvrent le {date}": "Registrations are not yet open! They will open on {date}","abandonner": "abandon","about": "about","activer le chrono pour ce stand": "activate the timer for this stand","ajouter un nouveau coureur": "add a new runner","altitude": "altitude","ancien mot de passe": "old password","archiver": "archive","bienvenue {name}, tu es bien connecté": "welcome {name}, you are successfully logged in","cdv 2.0": "cdv 2.0","ce n'est pas votre inscription.": "this is not your registration.","changer la position": "change position","chemin": "path","chronometrer": "timekeeping","cliquer où vous voulez ajouter le stand": "click where you want to add the stand","clé": "key","commencer par créer un parcours": "start by creating a course","couleur du stand": "stand color","coureur": "runner","coureurs": "runners","course des vignes 2.0": "vineyard race 2.0","créer": "create","créer un compte": "create an account","créer un nouveau Parcours": "create a new course","créer une copie du parcours": "create a copy of the course","date": "date","date d'ouverture des inscriptions": "registration opening date","date de fermeture des inscriptions": "registration closing date","date de l'édition": "edition date","date de naissance": "date of birth","des utilisateur on été trouvé avec les mêmes nom. choisir qui inscrire": "users with the same name have been found. choose who to register","desarchiver": "unarchive","description de l'évenement": "event description","description du parcours": "course description","disqualifier": "disqualify","distance": "distance","documentation": "documentation","dossard": "bib number","e-mail": "e-mail","editions": "editions","email": "email","enter le nom du nouvel évènement": "enter the name of the new event","entrer le numéro de dossard": "enter the bib number","exporter au format excel": "export to Excel format","fermer": "close","fini": "finished","finir le parcours": "finish the course","fr": "fr","générer": "generate","gérer les dossard": "manage bib numbers","gérer les parcours": "manage courses","gérer les passages": "manage checkpoints","heure": "time","heure d'arrivée": "arrival time","heure de départ": "departure time","image de profile": "profile picture","info": "info","inscriptions": "registrations","l'utilisateur {username} a été inscrit avec succes": "user {username} has been successfully registered","l'édition \"{edition}\" n'existe pas": "the edition \"{edition}\" does not exist","l'évènement n'as pas pu être supprimé": "the event could not be deleted","l'événement \"{event}\" n'existe pas": "the event \"{event}\" does not exist","la clé a bien été supprimée": "the key has been successfully deleted","la clé n'as pas pu être suprimée": "the key could not be deleted","lancer le parcours": "start the course","langues": "languages","latitude du depart": "starting latitude","latitude du départ": "starting latitude","latitude du stand": "stand latitude","le coureur ayans l\\'id {coureur} n\\'existe pas.": "the runner with id {coureur} does not exist.","le mot de passe ou le nom d'utilisateur n'est pas valide": "the password or username is invalid","le parcours \"{parcours}\" n'existe pas": "the course \"{parcours}\" does not exist","les inscriptions sont déjà fermées!": "registrations are already closed!","lieu de rendez-vous": "meeting place","longitude du depart": "starting longitude","longitude du départ": "starting longitude","longitude du stand": "stand longitude","modifier le mot de passe": "change password","modifier son compte": "modify account","modifier son mot de passe": "change password","modifier son profil": "modify profile","mot de passe": "password","ne plus participer": "no longer participate","nom": "name","nom complet": "full name","nom d'utilisateur": "username","nom de l'etape": "stage name","nom de l'édition": "edition name","nom de l'évenement": "event name","nom de l'événement": "event name","nom du parcours": "course name","nom du stand": "stand name","nous contacter": "contact us","nouveau mot de passe": "new password","nouveau stand": "new stand","nouvelle édition": "new edition","numéro de téléphone": "phone number","ouvrir sur Google Maps": "open in Google Maps","parcours": "course","parcours archivés": "archived courses","parcours choisis": "chosen courses","parcours non modifiable car déjà utilisé dans une édition": "course not editable as it has already been used in an edition","participations": "participations","place": "place","prochain événements": "upcoming events","profil": "profile","prénom": "first name","présents": "present","rang": "rank","rendez-vous": "appointment","répéter le mot de passe": "repeat password","répéter le nouveau mot de passe": "repeat new password","résultats": "results","s'inscrire": "register","sauver": "save","se connecter": "log in","se déconnecter": "log out","se désinscrire": "unregister","stand": "stand","supprimer": "delete","supprimer l'etape": "delete the stage","supprimer l'évenement": "delete the event","temps": "time","tu doit être admin de cet evenement pour acceder a cette page.": "you must be admin of this event to access this page.","tu doit être admin pour accéder à cette page.": "you must be admin to access this page.","tu es bien déconnecté !": "you are successfully logged out!","télephone": "telephone","téléphone": "telephone","username": "username","valider": "validate","vos inscriptions": "your registrations","vos événement": "your events","votre compte a bien été créé": "your account has been successfully created","édition": "edition","éditions": "editions","état": "state","événement": "event"}


#     langs = export_strings(source='fr', target=[lang for lang in LANGAGES if lang not in ('ids', 'pseudo')])
#     ic(langs)
#     for key, val in langs.items():
#         if val['fr'] in langs.values():
#             langs[key]['en'] = val['en']
#     ic(langs)
#     save_translations(langs)
#     return 'ok'

def save_translations(translations):
    with open(f'{app.root_path}/messages.pot', 'r', encoding='utf-8') as file:
        template = read_po(StringIO(file.read()))

    for locale in translations[next(iter(translations))]:
        new_catalog = Catalog()
        for id in translations:
            new_catalog.add(id, translations[id][locale])
        new_catalog.update(template)
        with open(f'{app.root_path}/translations/{locale}/LC_MESSAGES/messages.po', 'wb') as file:
            write_po(file , new_catalog)

@dev.route('/languages', methods=['get', 'post'])
@dev_required
def languages():
    langs = export_strings(source='fr', target=[lang for lang in LANGAGES if lang not in ('ids', 'pseudo')])
    form:langForm = langForm()
    if form.validate_on_submit():
        data = eval(form.data.data)
        save_translations(data)
        os.system('pybabel compile -f -d chrono_des_vignes/translations')
        return redirect(url_for('dev.languages'))
    app.run()
    return render_template('languages.html', langs = langs, form=form)

@dev.route('/reload_translations')
@dev_required
def reload():
    create_cfg()

    os.system('pybabel extract -F chrono_des_vignes/babel.cfg -k lazy_gettext -o chrono_des_vignes/messages.pot .')
    os.system('pybabel update -i chrono_des_vignes/messages.pot -d chrono_des_vignes/translations --no-fuzzy-matching')

    translations = export_strings()
    new = translations.copy()
    for id, langs in translations.items():
        for lang, trad in langs.items():
            if lang == 'ids':
                new[id][lang]=id
            elif lang == 'pseudo':
                new[id][lang]='XXXXXXXX'
    save_translations(new)

    os.system('pybabel compile -f -d chrono_des_vignes/translations')

    return redirect(url_for('dev.languages'))
