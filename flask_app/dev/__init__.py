from flask import Blueprint, redirect, render_template, flash, url_for, jsonify, request
from flask_app import admin_required, db, DEV_ENABLE
from functools import wraps

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


@dev.route('/', subdomain='dev')
@dev_required
def dev_home():
    return render_template('dev_home.html')


@dev.route('/languages', subdomain='dev')
@dev_required
def languages():
    return render_template('languages.html')