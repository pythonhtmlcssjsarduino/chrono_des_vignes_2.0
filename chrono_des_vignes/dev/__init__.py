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
from flask import Blueprint, redirect, render_template, flash, jsonify, abort
from chrono_des_vignes import app, LANGAGES, lang_url_for as url_for
from functools import wraps
import glob
import os
from babel.messages.pofile import read_po, write_po
from babel.messages.catalog import Catalog
from io import StringIO
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from chrono_des_vignes.custom_validators import DataRequired


class langForm(FlaskForm):
    lang_data = StringField('data', validators=[DataRequired()])
    submit_btn = SubmitField('submit')

def dev_required(func):
    """
    Modified login_required decorator to restrict access to dev
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not app.debug:
            flash('dev is not enabled')
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

def export_strings(source='en', target=None):
    target = target or LANGAGES
    with open(f'{app.root_path}/translations/{source}/LC_MESSAGES/messages.po', 'r', encoding='utf-8') as file:
        source_str = StringIO(file.read())
    source_catalog = read_po(source_str)
    for_tron = {message.id: {source: message.string}
                 for message in source_catalog if message.id}

    for locale in target:
        if locale != source:
            with open(f'{app.root_path}/translations/{locale}/LC_MESSAGES/messages.po', 'r', encoding='utf-8') as file:
                target_str = StringIO(file.read())
            target_catalog = read_po(target_str)

            for message in target_catalog:
                if message.id and message.id in for_tron.keys():
                    for_tron[message.id][locale] = message.string

    return for_tron

@dev.route('/lang_json/<lang_id>', methods=['GET', 'POST'])
@dev_required
def lang_json(lang_id):
    langs = export_strings(source='fr', target=[lang for lang in LANGAGES if lang not in ('ids', 'pseudo')])
    return jsonify({lang['fr']: lang[lang_id] for lang in langs.values()})

def save_translations(translations):
    if not translations:
       #ic("No translations provided.")
        return
    with open(f'{app.root_path}/messages.pot', 'r', encoding='utf-8') as file:
        template = read_po(StringIO(file.read()))

    for locale in translations[next(iter(translations))]:
        new_catalog = Catalog()
        for id in translations:
            new_catalog.add(id, translations[id][locale])
        new_catalog.update(template)
        with open(f'{app.root_path}/translations/{locale}/LC_MESSAGES/messages.po', 'wb') as file:
            write_po(file, new_catalog)

@dev.route('/languages', methods=['GET', 'POST'])
@dev_required
def languages():
    langs = export_strings(source='fr', target=[lang for lang in LANGAGES if lang not in ('ids', 'pseudo')])
    form = langForm()
    if form.validate_on_submit():
        data = eval(form.data.data)
        save_translations(data)
        os.system('pybabel compile -f -d chrono_des_vignes/translations')
        return redirect(url_for('dev.languages'))
    return render_template('languages.html', langs=langs, form=form)

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
                new[id][lang] = id
            elif lang == 'pseudo':
                new[id][lang] = 'XXXXXXXX'
    save_translations(new)

    os.system('pybabel compile -f -d chrono_des_vignes/translations')

    return redirect(url_for('dev.languages'))
