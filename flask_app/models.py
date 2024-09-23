from flask_app import db, DEFAULT_PROFIL_PIC
from sqlalchemy_utils import ColorType
from colour import Color
from flask_login import UserMixin
from datetime import datetime

editions_parcours = db.Table(
    'editions_parcours',
    db.Column('edition_id', db.Integer, db.ForeignKey('edition.id')),
    db.Column('parcours_id', db.Integer, db.ForeignKey('parcours.id')),
)

passagekey_stand = db.Table(
    'passagekey_stand',
    db.Column('passage_key_id', db.Integer, db.ForeignKey('passage_key.id')),
    db.Column('stand_id', db.Integer, db.ForeignKey('stand.id')),
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    avatar = db.Column(db.String(80), nullable=False, default=DEFAULT_PROFIL_PIC)
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
        return f'<username : {self.username}, password: {self.password}, {self.avatar}>'


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creation_date=db.Column(db.DateTime, nullable=False, default=datetime.now)
    name= db.Column(db.String(20), nullable=False, unique=True)
    parcours=db.relationship('Parcours', backref='event', lazy='dynamic')
    editions=db.relationship('Edition', backref='event', lazy='dynamic')
    inscrits=db.relationship('Inscription', backref='event', lazy='dynamic')
    createur_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    passage_keys=db.relationship('PassageKey', backref='event', lazy='dynamic')

    def get_unique_inscrits(self):
        uniques =[]
        ids =set()
        for inscrit in self.inscrits.all():
            if inscrit.inscrit.id not in ids:
                ids.add(inscrit.inscrit.id)
                uniques.append(inscrit)
        return uniques

class Parcours(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creation_date=db.Column(db.DateTime, nullable=False, default=datetime.now)
    stands = db.relationship('Stand', backref='parcours', foreign_keys='Stand.parcours_id', lazy ='dynamic')
    traces = db.relationship('Trace', backref='parcours', foreign_keys='Trace.parcours_id', lazy ='dynamic')
    start_stand = db.relationship('Stand', foreign_keys='Stand.start_stand', uselist=False)
    end_stand = db.relationship('Stand', foreign_keys='Stand.end_stand', uselist=False)
    name= db.Column(db.String(20), nullable=False)
    event_id=db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    editions = db.relationship('Edition', secondary=editions_parcours, back_populates='parcours', lazy ='dynamic')
    inscriptions=db.relationship('Inscription', backref='parcours', lazy='dynamic')
    description = db.Column(db.Text, nullable=False, default='')
    archived = db.Column(db.Boolean, nullable=False, default=False)
    chronos_list = db.Column(db.Text, nullable=False, default='[]')

    def __repr__(self):
        return f'<Parcours name:{self.name}, event:{self.event.name}>'

class Stand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(20), nullable=False)
    lat = db.Column( db.Float, nullable=False)
    lng = db.Column( db.Float, nullable=False)
    elevation = db.Column( db.Float)
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
    passage_keys = db.relationship('PassageKey', secondary=passagekey_stand, back_populates='stands', lazy='dynamic')

    def __repr__(self):
        return f'<Stand id:{self.id}, name:{self.name}, parcours:{self.parcours_id}>'


class Trace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(20), nullable=False)
    parcours_id = db.Column(db.Integer, db.ForeignKey('parcours.id'))
    start_id=db.Column(db.Integer, db.ForeignKey('stand.id'), nullable=False)
    end_id=db.Column(db.Integer, db.ForeignKey('stand.id'), nullable=False)
    trace = db.Column(db.Text, nullable=False, default='[]')
    turn_nb = db.Column(db.Integer, nullable=False)

    def __str__(self):
        return f'<Trace id: {self.id} start: {self.start} end:{self.end}'

class Edition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creation_date=db.Column(db.DateTime, nullable=False, default=datetime.now)
    name= db.Column(db.String(20), nullable=False)
    event_id=db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    parcours = db.relationship('Parcours', secondary=editions_parcours, back_populates='editions', lazy ='dynamic')
    inscriptions=db.relationship('Inscription', backref='edition', lazy='dynamic')
    edition_date = db.Column( db.DateTime, nullable=False)
    first_inscription = db.Column( db.DateTime, nullable=False)
    last_inscription =db.Column( db.DateTime, nullable=False)
    rdv_lat = db.Column( db.Float, nullable=False, default=46.58)
    rdv_lng = db.Column( db.Float, nullable=False, default=6.52)
    passage_keys=db.relationship('PassageKey', backref='edition', lazy='dynamic')

class Inscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creation_date=db.Column(db.DateTime, nullable=False, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id=db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    edition_id=db.Column(db.Integer, db.ForeignKey('edition.id'), nullable=False)
    parcours_id=db.Column(db.Integer, db.ForeignKey('parcours.id'), nullable=False)
    dossard=db.Column(db.Integer)
    passages=db.relationship('Passage', backref='inscription', lazy='dynamic')

class PassageKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creation_date=db.Column(db.DateTime, nullable=False, default=datetime.now)
    event_id=db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    edition_id=db.Column(db.Integer, db.ForeignKey('edition.id'), nullable=False)
    stands=db.relationship('Stand', secondary=passagekey_stand, back_populates='passage_keys', lazy='dynamic')
    passages=db.relationship('Passage', backref='key', lazy='dynamic')
    key=db.Column(db.String(20), nullable=False, unique=True)
    name=db.Column(db.String(20), nullable=False)

class Passage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creation_date=db.Column(db.DateTime, nullable=False, default=datetime.now)
    time_stamp=db.Column(db.DateTime, nullable=False)
    key_id=db.Column(db.Integer, db.ForeignKey('passage_key.id'), nullable=False)
    inscription_id = db.Column(db.Integer, db.ForeignKey('inscription.id'), nullable=False)

    def __repr__(self) -> str:
        return f'<Passage time={self.time_stamp} key={self.key.name} inscription={self.inscription.inscrit.username} >'