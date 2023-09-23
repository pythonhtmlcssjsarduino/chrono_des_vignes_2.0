from flask_app import db
from flask_login import UserMixin
from datetime import datetime

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    avatar = db.Column(db.String(80), nullable=False, default='icone.png')
    name= db.Column(db.String(20), nullable=False)
    lastname = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(80), nullable=True)
    phone = db.Column(db.String(15), nullable=True)
    datenaiss = db.Column(db.DateTime, nullable=False)
    #* inscriptions = db.relationship('Inscriptions')
    admin = db.Column(db.Boolean, nullable=False)
    #* creations=db.relationship('Event')

    def __repr__(self) -> str:
        return f'username : {self.username}, password: {self.password}'