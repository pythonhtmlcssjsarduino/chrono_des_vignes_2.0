from flask import Flask, redirect, url_for, flash
from datetime import datetime
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"

db = SQLAlchemy()
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

#todo fake data a enlever
from flask_app.models import Users
fake_data = {'course des vignes':{'name': 'course des vignes',
             'editions': [{'name': '2020'}, {'name': '2021'}, {'name': '2022'}, {'name': '2023'}],
             'parcours': [{'name': 'A'}, {'name': 'B'}, {'name': 'C'}, {'name': 'W'}],
             'coureurs': [{'name': 'moi'}, {'name': 'toi'}, {'name': 'il'}, {'name': 'ils'}]
            }}
users={'romain.maurer':Users(name='romain', lastname='Maurer', password='12345', username='romain.maurer', phone='0774428642', datenaiss=datetime(year=2007,month=7, day=28), id=9, creation_date=datetime(year=2023,month=9, day=21), admin=True)}
id_to_username ={'9':'romain.maurer'}
#todo fin des fake data

@login_manager.user_loader
def load_user(user_id:str ):
    print(user_id)
    print(users[id_to_username.get(user_id, None)])
    return users[id_to_username.get(user_id, None)]

# defini les pages du site web
from flask_app import routes


#* erreur 403 acces non autorisé
def error403():
    flash('tu doit etre connecté pour acceder a cette page.', 'danger')
    return redirect(url_for('home'))
login_manager.unauthorized_handler(error403)
