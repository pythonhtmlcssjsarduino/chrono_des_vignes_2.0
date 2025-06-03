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

from __future__ import annotations
from html import escape
from chrono_des_vignes import db, DEFAULT_PROFIL_PIC
from sqlalchemy_utils import ColorType as ColorType_sql_utils, JSONType
from colour import Color
from flask_login import UserMixin
from datetime import datetime, timedelta
from chrono_des_vignes.lib import calc_points_dist
from typing import Iterator, Iterable, Literal
from collections import namedtuple
from markdown import markdown
from sqlalchemy import func, not_
from flask_sqlalchemy.model import Model

md_extentions:list[str] = ['admonition', 'markdown.extensions.tables']
def get_html_from_markdown(markdown_text: str) -> str:
    return markdown(
        escape(markdown_text),
        extensions=md_extentions,
        extension_configs={},
        output_format='html'
    )

def get_column_max_length(table:db.Model, column_name:str) -> int |None:
    for column in table.__table__.columns:
        if column.name == column_name:
            return column.type.length
    return None

class ColorType(ColorType_sql_utils):
    STORE_FORMAT='hex_l'

TracePoint: namedtuple = namedtuple('TracePoint', ['lat', 'lng', 'alt'], defaults=[None])

editions_parcours: db.Table = db.Table(
    'editions_parcours',
    db.Column('edition_id', db.Integer, db.ForeignKey('edition.id')),
    db.Column('parcours_id', db.Integer, db.ForeignKey('parcours.id')),
)

passagekey_stand:db.Table = db.Table(
    'passagekey_stand',
    db.Column('passage_key_id', db.Integer, db.ForeignKey('passage_key.id')),
    db.Column('stand_id', db.Integer, db.ForeignKey('stand.id')),
)

class User(UserMixin, db.Model):
    __allow_unmapped__ = True
    id = db.Column(db.Integer, primary_key=True)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    avatar = db.Column(db.String(80), nullable=False, default=DEFAULT_PROFIL_PIC)
    name= db.Column(db.String(40), nullable=False)
    lastname = db.Column(db.String(40), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(40), nullable=False, unique=True)
    email = db.Column(db.String(80), nullable=True)
    phone = db.Column(db.String(25), nullable=True)
    datenaiss = db.Column(db.DateTime, nullable=False)
    inscriptions = db.relationship('Inscription', backref='inscrit', lazy='dynamic')
    admin = db.Column(db.Boolean, nullable=False, default=False)
    creations=db.relationship('Event', backref='createur', lazy='dynamic')

    def __repr__(self) -> str:
        return f'<username : {self.username}, password: {self.password}, {self.avatar}>'

class Event(db.Model):
    __allow_unmapped__ = True
    id = db.Column(db.Integer, primary_key=True)
    creation_date=db.Column(db.DateTime, nullable=False, default=datetime.now)
    name= db.Column(db.String(40), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False, default='')
    parcours=db.relationship('Parcours', backref='event', lazy='dynamic')
    editions=db.relationship('Edition', backref='event', lazy='dynamic')
    inscrits=db.relationship('Inscription', backref='event', lazy='dynamic')
    createur_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    passage_keys=db.relationship('PassageKey', backref='event', lazy='dynamic')

    
    @property
    def description_html(self):
        return get_html_from_markdown(self.description)

    def get_unique_inscrits(self):
        uniques =[]
        ids =set()
        for inscrit in self.inscrits.all():
            if inscrit.inscrit.id not in ids:
                ids.add(inscrit.inscrit.id)
                uniques.append(inscrit)
        return uniques

class Parcours(db.Model):
    __allow_unmapped__ = True
    id = db.Column(db.Integer, primary_key=True)
    creation_date=db.Column(db.DateTime, nullable=False, default=datetime.now)
    stands = db.relationship('Stand', backref='parcours', foreign_keys='Stand.parcours_id', lazy ='dynamic')
    traces = db.relationship('Trace', backref='parcours', foreign_keys='Trace.parcours_id', lazy ='dynamic')
    start_stand = db.relationship('Stand', foreign_keys='Stand.start_stand', uselist=False)
    end_stand = db.relationship('Stand', foreign_keys='Stand.end_stand', uselist=False)
    name= db.Column(db.String(40), nullable=False)
    event_id=db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    editions = db.relationship('Edition', secondary=editions_parcours, back_populates='parcours', lazy ='dynamic')
    inscriptions=db.relationship('Inscription', backref='parcours', lazy='dynamic')
    description = db.Column(db.Text, nullable=False, default='')
    archived = db.Column(db.Boolean, nullable=False, default=False)
    chronos_list = db.Column(db.Text, nullable=False, default='[]')

    def __repr__(self):
        return f'<Parcours name:{self.name}, event:{self.event.name}>'
    
    def __len__(self):
        return len(iter(self))

    def __iter__(self) ->Iterator[Stand|Trace]:
        start = self.start_stand
        if start:
            stand = start
            yield start
            turn_nb = 0
            while True:
                if stand == start:
                    turn_nb+=1
                old_stand = stand
                trace = old_stand.start_trace.filter_by(turn_nb=turn_nb).first()
                if trace is not None:
                    yield trace
                    stand=trace.end
                    yield stand
                else:
                    break

    def iter_turn(self, turn_nb:int)->Iterator[Stand|Trace]:
        start = self.start_stand
        if start:
            stand = start
            yield start
            while True:
                trace = stand.start_trace.filter_by(turn_nb=turn_nb).first()
                if trace is not None:
                    yield trace
                    stand=trace.end
                    yield stand
                else:
                    break
                if stand == start:
                    break

    def iter_chrono_list(self)->Iterator[Stand]:
        for id in eval(self.chronos_list):
            yield Stand.query.get(id)

    def get_chrono_dists(self)->list[float]:
        dist=0
        dist_list=[]
        for e in self:
            if isinstance(e, Stand):
                if e.chrono:
                    dist_list.append(dist)
            else:
                dist+=e.get_dist()
        return dist_list

    def get_nb_turns(self)->int:
        return max([t.turn_nb for t in self.traces])

class Stand(db.Model):
    __allow_unmapped__ = True
    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(40), nullable=False)
    lat = db.Column( db.Float, nullable=False)
    lng = db.Column( db.Float, nullable=False)
    elevation = db.Column( db.Float)
    parcours_id:int = db.Column(db.Integer, db.ForeignKey('parcours.id'))
    parcours:Parcours
    # id du parcours dont il est le debut (le meme que parcours_id) ne rien mettre si pas le premier
    start_stand:int = db.Column(db.Integer, db.ForeignKey('parcours.id'))
    # id du parcours dont il est la fin (le meme que parcours_id) ne rien mettre si pas le dernier
    end_stand:int = db.Column(db.Integer, db.ForeignKey('parcours.id'))
    color:Color = db.Column(ColorType , nullable =False, default=Color('red'))
    chrono:bool = db.Column(db.Boolean, nullable=False, default=False)
    #traces qui partent de ce stand
    start_trace=db.relationship('Trace', backref='start', foreign_keys='Trace.start_id', lazy='dynamic')
    # traces qui finissent a ce stand
    end_trace=db.relationship('Trace', backref='end', foreign_keys='Trace.end_id', lazy='dynamic')
    passage_keys = db.relationship('PassageKey', secondary=passagekey_stand, back_populates='stands', lazy='dynamic')

    def __repr__(self):
        return f'<Stand id:{self.id}, name:{self.name}, parcours:{self.parcours_id}>'

class Trace(db.Model):
    __allow_unmapped__ = True
    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(40), nullable=False)
    parcours_id = db.Column(db.Integer, db.ForeignKey('parcours.id'))
    start_id=db.Column(db.Integer, db.ForeignKey('stand.id'), nullable=False)
    end_id=db.Column(db.Integer, db.ForeignKey('stand.id'), nullable=False)
    trace = db.Column(db.Text, nullable=False, default='[]')
    turn_nb = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Trace id: {self.id} turn_nb: {self.turn_nb} start: {self.start} end:{self.end}'
    
    def __iter__(self)->Iterator[TracePoint]:
        for lat, lng, alt in eval(self.trace):
            yield TracePoint(lat, lng, alt if alt else None)
    
    def __len__(self)->int:
        return len(eval(self.trace))

    def set_trace(self, trace:Iterable[TracePoint|tuple[float, float, float|None]])->None:
        '''
            sterilise et defini la valeure du champ trace
            !!! ne commit pas les changement !!
        '''
        sterilised_trace = []
        for point in trace:
            sterilised_trace.append((point[0], point[1], point[2]))
        self.trace = str(sterilised_trace)
        
    def has_alt(self)-> bool:
        return all((bool(point.alt) for point in self))
    
    def get_dist(self)->float:
        dist = 0
        last_point = self.start.lat, self.start.lng
        for lat, lng, alt in self:
            dist += calc_points_dist(lat, lng, last_point[0], last_point[1])
            last_point = lat, lng
        dist += calc_points_dist(self.end.lat, self.end.lng, last_point[0], last_point[1])
        return dist

    def is_last_trace(self)->bool:
        #ic(self.end == self.parcours.end_stand and self.end.end_trace.filter_by(turn_nb=self.turn_nb+1).count()==0, self.end , self.parcours.end_stand, self.end.end_trace.filter_by(turn_nb=self.turn_nb+1).count())
        return self.end == self.parcours.end_stand and self.end.end_trace.filter_by(turn_nb=self.turn_nb+1).count()==0
    
    def is_first_trace(self)->bool:
        return self.start == self.parcours.start_stand and self.turn_nb==1

    def get_next_trace(self)->Trace:
        if self.end == self.parcours.start_stand:
            return self.end.start_trace.filter_by(turn_nb=self.turn_nb+1).first()
        else:
            return self.end.start_trace.filter_by(turn_nb=self.turn_nb).first()

    def get_last_trace(self)->Trace:
        if self.start == self.parcours.start_stand:
            return self.start.end_trace.filter_by(turn_nb=self.turn_nb-1).first()
        else:
            return self.start.end_trace.filter_by(turn_nb=self.turn_nb).first()

    '''def get_points_dist(self, start_dist:float=0)-> list[float]:
        dists = []
        trace = eval(self.trace)
        last_point = trace[0]
        for lat, lng, alt in trace[1:]:
            dists.append(start_dist+calc_points_dist(lat, lng, last_point[0], last_point[1]))
            last_point = lat, lng
        return dists'''

class Edition(db.Model):
    __allow_unmapped__ = True
    id = db.Column(db.Integer, primary_key=True)
    creation_date=db.Column(db.DateTime, nullable=False, default=datetime.now)
    description = db.Column(db.Text, nullable=False, default='')
    name= db.Column(db.String(40), nullable=False)
    event_id=db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    parcours = db.relationship('Parcours', secondary=editions_parcours, back_populates='editions', lazy ='dynamic')
    inscriptions=db.relationship('Inscription', backref='edition', lazy='dynamic')
    edition_date = db.Column( db.DateTime, nullable=False)
    first_inscription = db.Column( db.DateTime, nullable=False)
    last_inscription =db.Column( db.DateTime, nullable=False)
    rdv_lat = db.Column( db.Float, nullable=False, default=46.58)
    rdv_lng = db.Column( db.Float, nullable=False, default=6.52)
    passage_keys=db.relationship('PassageKey', backref='edition', foreign_keys='PassageKey.edition_id', lazy='dynamic')

    @property
    def description_html(self):
        return get_html_from_markdown(self.description)

class Inscription(db.Model):
    __allow_unmapped__ = True
    id = db.Column(db.Integer, primary_key=True)
    creation_date=db.Column(db.DateTime, nullable=False, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id=db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    edition_id=db.Column(db.Integer, db.ForeignKey('edition.id'), nullable=False)
    edition:Edition
    parcours_id=db.Column(db.Integer, db.ForeignKey('parcours.id'), nullable=False)
    parcours:Parcours
    dossard=db.Column(db.Integer)
    passages=db.relationship('Passage', backref='inscription', lazy='dynamic')
    present=db.Column(db.Boolean, nullable=False, default=False)
    end=db.Column(db.String(10)) # abandon, disqual, absent, finish or None

    def __repr__(self) -> str:
        return f'<Inscription id:{self.id} dossard:{self.dossard} user:{self.inscrit.username}>'
    
    def has_started(self)->bool:
        return bool(self.passages.count())
    
    def get_last_passage(self)->Passage:
        return self.passages.order_by(Passage.time_stamp.desc()).first()
    
    def get_first_passage(self)->Passage:
        return self.passages.order_by(Passage.time_stamp.asc()).first()

    @property
    def status(self)->str:
        if not self.has_started():
            return 'pas partit'
        else:
            match self.end:
                case 'abandon':
                    return 'abandon'
                case 'disqual':
                    return 'disqualifié'
                case 'absent':
                    return 'absent'
                case 'finish':
                    return 'arrivé'
                case _:
                    return 'en cours'

    @property
    def start_time(self)->datetime:
        return self.get_first_passage().time_stamp

    @property
    def last_time(self)->datetime:
        return self.get_last_passage().time_stamp
    
    def get_time(self)->timedelta|Literal['']:
        if not self.has_started():
            return ''
        return self.last_time - self.start_time

    def get_run(self):
        user_passages:list[Passage] = self.passages.filter(Passage.time_stamp<=self.get_last_passage().time_stamp).all()
        run=[]
        if len(user_passages)>0:
            for stand in self.parcours.iter_chrono_list():
                if len(user_passages)>0 and stand == user_passages[0].get_stand():
                    user_passages.pop(0)
                    run.append(True)
                elif len(user_passages)>0:
                    run.append(False)
                else:
                    run.append(None)
        return run

    def has_all_right(self)->bool:
        if not self.has_started():
            return False
        run = self.get_run()
        return all(run)

    def has_finish(self)->bool:
        if not self.has_started():
            return False
        run = self.get_run()
        return run[-1]!=None

    @property
    def rank(self)->int:
        if self.end != 'finish':
            return {'abandon':'abandon', 'disqual':'disqualifié', 'absent':'absent'}.get(self.end, None)
        # all inscriptions that are in the same parcours and edition
        inscriptions = Inscription.query.filter(Inscription.parcours==self.parcours, Inscription.edition==self.edition)
        # get all the inscription that there last time is smaller than this one
        inscriptions = inscriptions.filter(not_(Inscription.passages.any(Passage.time_stamp>self.get_time())))
        # get only those that have finished
        inscriptions = inscriptions.filter(Inscription.end=='finish')
        return inscriptions.count()+1

class PassageKey(db.Model):
    __allow_unmapped__ = True
    id = db.Column(db.Integer, primary_key=True)
    creation_date=db.Column(db.DateTime, nullable=False, default=datetime.now)
    event_id=db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    edition_id=db.Column(db.Integer, db.ForeignKey('edition.id'), nullable=False)
    stands=db.relationship('Stand', secondary=passagekey_stand, back_populates='passage_keys', lazy='dynamic')
    passages=db.relationship('Passage', backref='key', lazy='dynamic')
    key=db.Column(db.String(20), nullable=False, unique=True)
    name=db.Column(db.String(40), nullable=False)

    def __repr__(self) -> str:
        return f"<PassageKey edition:{self.edition.name} stands={', '.join(str(stand) for stand in self.stands.all())}>"

class Passage(db.Model):
    __allow_unmapped__ = True
    id = db.Column(db.Integer, primary_key=True)
    time_stamp:datetime=db.Column(db.DateTime, nullable=False)
    key_id=db.Column(db.Integer, db.ForeignKey('passage_key.id'), nullable=True) # pas de key implique demmaré par l'admin
    key:PassageKey
    inscription_id = db.Column(db.Integer, db.ForeignKey('inscription.id'), nullable=False)
    inscription:Inscription

    def __repr__(self) -> str:
        return f'<Passage time={self.time_stamp} key={self.key.name if self.key else None} inscription={self.inscription.inscrit.username} >'
    
    def get_stand(self)->Stand:
        if self.key is None:
            stand = self.inscription.parcours.start_stand
        else:
            stand = self.key.stands.filter_by(parcours=self.inscription.parcours).first()
        return stand