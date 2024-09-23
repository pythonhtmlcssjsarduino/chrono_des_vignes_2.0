from flask import Blueprint, redirect, render_template, flash, url_for, jsonify, request
from flask_app import admin_required, db, DEV_ENABLE, app, LANGAGES
from functools import wraps
import glob, os
from babel.messages.pofile import read_po, write_po
from babel.messages.catalog import Catalog
from io import StringIO
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_app.custom_validators import DataRequired


class langForm(FlaskForm):
    data = StringField('data', validators=[DataRequired()])
    submit_btn = SubmitField('submit')

def dev_required(func):
    """
    Modified login_required decorator to restrict access to dev
    """

    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not DEV_ENABLE:
            flash('dev is not enable')
            return redirect(url_for('home'))
        return func(*args, **kwargs)
    return decorated_view

dev = Blueprint('dev', __name__, template_folder='template', subdomain='dev')


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
        os.system('pybabel compile -f -d flask_app/translations')
        return redirect(url_for('dev.languages'))
    app.run()
    return render_template('languages.html', langs = langs, form=form)

@dev.route('/reload_translations')
@dev_required
def reload():
    create_cfg()

    os.system('pybabel extract -F flask_app/babel.cfg -k lazy_gettext -o flask_app/messages.pot .')
    os.system('pybabel update -i flask_app/messages.pot -d flask_app/translations')

    translations = export_strings()
    new = translations.copy()
    for id, langs in translations.items():
        for lang, trad in langs.items():
            if lang == 'ids':
                new[id][lang]=id
            elif lang == 'pseudo':
                new[id][lang]='XXXXXXXX'
    save_translations(new)

    os.system('pybabel compile -f -d flask_app/translations')

    return redirect(url_for('dev.languages'))
