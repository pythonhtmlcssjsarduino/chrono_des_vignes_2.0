from flask_app import db
from sqlalchemy_utils import ColorType
from colour import Color
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import Integer

class User(UserMixin, db.Model):
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
    inscriptions = db.relationship('Inscription', backref='inscrit', lazy='dynamic')
    admin = db.Column(db.Boolean, nullable=False, default=False)
    creations=db.relationship('Event', backref='createur', lazy='dynamic')

    def __repr__(self) -> str:
        return f'username : {self.username}, password: {self.password}'


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creation_date=db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    name= db.Column(db.String(20), nullable=False, unique=True)
    parcours=db.relationship('Parcours', backref='event', lazy='dynamic')
    editions=db.relationship('Edition', backref='event', lazy='dynamic')
    inscrits=db.relationship('Inscription', backref='event', lazy='dynamic')
    createur_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Parcours(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creation_date=db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    stands = db.relationship('Stand', backref='parcours', foreign_keys='Stand.parcours_id', lazy ='dynamic')
    traces = db.relationship('Trace', backref='parcours', foreign_keys='Trace.parcours_id', lazy ='dynamic')
    start_stand = db.relationship('Stand', foreign_keys='Stand.start_stand', uselist=False)
    end_stand = db.relationship('Stand', foreign_keys='Stand.end_stand', uselist=False)
    name= db.Column(db.String(20), nullable=False, unique=True)
    event_id=db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    inscriptions=db.relationship('Inscription', backref='parcours', lazy='dynamic')

class Stand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(20), nullable=False, unique=True)
    lat = db.Column( db.Float, nullable=False)
    lng = db.Column( db.Float, nullable=False)
    parcours_id = db.Column(db.Integer, db.ForeignKey('parcours.id'))
    # id du parcours dont il est le debut (le meme que parcours_id) ne rien mettre si pas le premier
    start_stand = db.Column(db.Integer, db.ForeignKey('parcours.id'))
    # id du parcours dont il est la fin (le meme que parcours_id) ne rien mettre si pas le dernier
    end_stand = db.Column(db.Integer, db.ForeignKey('parcours.id'))
    color = db.Column(ColorType , nullable =False, default=Color('red'))
    chrono = db.Column(db.Boolean, nullable=False, default=False)
    #traces qui partent de ce stand
    start_trace=db.relationship('Trace', backref='start', foreign_keys='Trace.start_id', lazy='dynamic')
    # traces qui finissent a ce stand
    end_trace=db.relationship('Trace', backref='end', foreign_keys='Trace.end_id', lazy='dynamic')

    def __repr__(self):
        return f'<Stand id:{self.id}, name:{self.name}, parcours:{self.parcours_id}>'


class Trace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(20), nullable=False, unique=True)
    parcours_id = db.Column(db.Integer, db.ForeignKey('parcours.id'))
    start_id=db.Column(db.Integer, db.ForeignKey('stand.id'), nullable=False)
    end_id=db.Column(db.Integer, db.ForeignKey('stand.id'), nullable=False)
    trace = db.Column(db.Text, nullable=False, default='[]')
    turn_nb = db.Column(db.Integer, nullable=False)
    
    def __str__(self):
        return f'<Trace id: {self.id} start: {self.start} end:{self.end}'

class Edition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creation_date=db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    name= db.Column(db.String(20), nullable=False, unique=True)
    event_id=db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    inscriptions=db.relationship('Inscription', backref='edition', lazy='dynamic')
    edition_date = db.Column( db.DateTime, nullable=False)
    first_inscription = db.Column( db.DateTime, nullable=False)
    last_inscription =db.Column( db.DateTime, nullable=False)
    rdv_lat = db.Column( db.Float, nullable=False, default=46.58)
    rdv_lng = db.Column( db.Float, nullable=False, default=6.52)



class Inscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creation_date=db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id=db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    edition_id=db.Column(db.Integer, db.ForeignKey('edition.id'), nullable=False)
    parcours_id=db.Column(db.Integer, db.ForeignKey('parcours.id'), nullable=False)
