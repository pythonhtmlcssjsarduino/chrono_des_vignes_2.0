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
from sqlalchemy.orm import DynamicMapped, Mapper, mapped_column, Mapped
from chrono_des_vignes import db, DEFAULT_PROFIL_PIC
from sqlalchemy_utils import ColorType as ColorType_sql_utils  # pyright: ignore[reportMissingTypeStubs]
from colour import Color
from flask_login import UserMixin
from datetime import datetime, timedelta
from chrono_des_vignes.lib import calc_points_dist
from typing import NamedTuple, TypeVar, cast
from collections.abc import Iterable, Iterator
from markdown import markdown
from sqlalchemy import not_, Table, Integer, ForeignKey, DateTime, String, Boolean, Text, Float, Column
from sqlalchemy.orm import relationship
from sqlalchemy.inspection import inspect
from ast import literal_eval

Model = db.Model

md_extentions:list[str] = ['admonition', 'markdown.extensions.tables']
def get_html_from_markdown(markdown_text: str) -> str:
    return markdown(
        escape(markdown_text),
        extensions=md_extentions,
        extension_configs={},
        output_format='html'
    )

T = TypeVar("T", bound=Model)
def get_column_max_length(table:type[T], column_name:str) -> int:
    mapper : Mapper[T] = cast(Mapper[T], inspect(table, True))
    column = mapper.columns[column_name]

    if isinstance(column.type, String) and column.type.length is not None:
        return column.type.length
    # max int possible
    return 2147483647

class ColorType(ColorType_sql_utils):
    STORE_FORMAT='hex_l'  # pyright: ignore[reportUnannotatedClassAttribute]

class TracePoint(NamedTuple):
    lat: float
    lng: float
    alt: float | None=None

editions_parcours: Table = db.Table(
    'editions_parcours',
    Column('edition_id', Integer, ForeignKey('edition.id')),
    Column('parcours_id', Integer, ForeignKey('parcours.id')),
)

passagekey_stand:Table = db.Table(
    'passagekey_stand',
    Column('passage_key_id', Integer, ForeignKey('passage_key.id')),
    Column('stand_id', Integer, ForeignKey('stand.id')),
)

class User(UserMixin, Model):
    id: Mapped[int] = mapped_column( primary_key=True, repr=True)

    name: Mapped[str]= mapped_column(String(40), nullable=False, repr=False)
    lastname: Mapped[str] = mapped_column(String(40), nullable=False, repr=False)
    password: Mapped[str] = mapped_column(String(80), nullable=False, repr=False)
    username: Mapped[str] = mapped_column(String(40), nullable=False, unique=True, repr=True)
    email: Mapped[str|None] = mapped_column(String(80), nullable=True, repr=False)
    phone: Mapped[str|None] = mapped_column(String(25), nullable=True, repr=False)
    datenaiss: Mapped[datetime] = mapped_column(nullable=False, repr=False)

    admin: Mapped[bool] = mapped_column(nullable=False, default=False, repr=True)
    creation_date: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now, repr=False)
    avatar: Mapped[str] = mapped_column(String(80), nullable=False, default=DEFAULT_PROFIL_PIC, repr=False)
    
    creations:DynamicMapped[Event]=relationship('Event', back_populates='createur', lazy='dynamic', init=False, repr=False)
    inscriptions:DynamicMapped[Inscription] = relationship('Inscription', back_populates='inscrit', lazy='dynamic', init=False, repr=False)
    __tablename__:str = 'user'

class Event(Model):
    id: Mapped[int] = mapped_column(primary_key=True, repr=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False, unique=True, repr=True)

    createur_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False, repr=False)
    createur: Mapped[User] = relationship('User', back_populates='creations',lazy='select', repr=True, init=False)

    creation_date: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now, repr=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default='', repr=False)

    parcours: DynamicMapped[Parcours] = relationship('Parcours', back_populates='event', lazy='dynamic', repr=False, init=False)
    editions: DynamicMapped[Edition] = relationship('Edition', backref='event', lazy='dynamic', repr=False, init=False)
    inscrits: DynamicMapped[Inscription] = relationship('Inscription', back_populates='event', lazy='dynamic', repr=False, init=False)
    passage_keys: DynamicMapped[PassageKey] = relationship('PassageKey', back_populates='event', lazy='dynamic', repr=False, init=False)
    __tablename__:str = 'event'

    @property
    def description_html(self)-> str:
        return get_html_from_markdown(self.description)

    def get_unique_inscrits(self):
        uniques:list[Inscription] =[]
        ids:set[int] =set()
        for inscrit in self.inscrits.all():
            if inscrit.inscrit.id not in ids:
                ids.add(inscrit.inscrit.id)
                uniques.append(inscrit)
        return uniques

class Parcours(Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    stands: DynamicMapped[Stand] = relationship('Stand', back_populates='parcours', foreign_keys='Stand.parcours_id', lazy ='dynamic', init=False)
    traces: DynamicMapped[Trace] = relationship('Trace', back_populates='parcours', foreign_keys='Trace.parcours_id', lazy ='dynamic', init=False)
    start_stand: Mapped[Stand] = relationship('Stand', foreign_keys='Stand.start_stand', uselist=False, init=False)
    end_stand:Mapped[Stand] = relationship('Stand', foreign_keys='Stand.end_stand', uselist=False, init=False)
    name: Mapped[str]= mapped_column(String(40), nullable=False)
    event_id: Mapped[int]=mapped_column(Integer, ForeignKey('event.id'), nullable=False)
    event:Mapped[Event] = relationship('Event', back_populates='parcours', lazy='select', init=False)
    editions:DynamicMapped[Edition] = relationship('Edition', secondary=editions_parcours, back_populates='parcours', lazy ='dynamic', init=False)
    inscriptions:DynamicMapped[Inscription]=relationship('Inscription', back_populates='parcours', lazy='dynamic', init=False)

    creation_date:Mapped[datetime]=mapped_column(DateTime, nullable=False, default=datetime.now)
    description: Mapped[str] = mapped_column(Text, nullable=False, default='')
    archived:Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    chronos_list:Mapped[str] = mapped_column(Text, nullable=False, default='[]')
    __tablename__:str = 'parcours'
    
    # region
    def __len__(self)-> int:
        return len(tuple(self))

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
        for id in cast(list[int],literal_eval(self.chronos_list)):
            yield Stand.query.get(id)  # pyright: ignore[reportReturnType]

    def get_chrono_dists(self):
        dist:float=0
        dist_list:list[float]=[]
        for e in self:
            if isinstance(e, Stand):
                if e.chrono:
                    dist_list.append(dist)
            else:
                dist+=e.get_dist()
        return dist_list

    def get_nb_turns(self)->int:
        return max([t.turn_nb for t in self.traces])#type: ignore[no-any-return]

    # endregion

class Stand(Model):
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    name:Mapped[str]= mapped_column(String(40), nullable=False)
    lat:Mapped[float] = mapped_column( Float, nullable=False)
    lng:Mapped[float] = mapped_column( Float, nullable=False)
    elevation:Mapped[float] = mapped_column( Float)
    parcours_id:Mapped[int] = mapped_column(Integer, ForeignKey('parcours.id'))
    parcours:Mapped[Parcours] = relationship('Parcours', back_populates='stands',foreign_keys=[parcours_id], lazy='select', init=False)
    # id du parcours dont il est le debut (le meme que parcours_id) ne rien mettre si pas le premier
    start_stand:Mapped[int] = mapped_column(Integer, ForeignKey('parcours.id'))
    # id du parcours dont il est la fin (le meme que parcours_id) ne rien mettre si pas le dernier
    end_stand:Mapped[int] = mapped_column(Integer, ForeignKey('parcours.id'))
    color:Mapped[Color] = mapped_column(ColorType , nullable =False, default=lambda:Color('red'))
    chrono:Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    #traces qui partent de ce stand
    start_trace:DynamicMapped[Trace]=relationship('Trace', back_populates='start', foreign_keys='Trace.start_id', lazy='dynamic', init=False)
    # traces qui finissent a ce stand
    end_trace:DynamicMapped[Trace]=relationship('Trace', back_populates='end', foreign_keys='Trace.end_id', lazy='dynamic', init=False)
    passage_keys:DynamicMapped[PassageKey] = relationship('PassageKey', secondary=passagekey_stand, back_populates='stands', lazy='dynamic', init=False)
    __tablename__:str = 'stand'

class Trace(Model):
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    name:Mapped[str]= mapped_column(String(40), nullable=False)
    parcours_id:Mapped[int] = mapped_column(Integer, ForeignKey('parcours.id'))
    parcours:Mapped[Parcours] = relationship('Parcours', back_populates='traces', lazy='select', init=False)
    start_id:Mapped[int]=mapped_column(Integer, ForeignKey('stand.id'), nullable=False)
    start:Mapped[Stand] = relationship('Stand', back_populates='start_trace', foreign_keys=[start_id], lazy='select', init=False)
    end_id:Mapped[int]=mapped_column(Integer, ForeignKey('stand.id'), nullable=False)
    end:Mapped[Stand] = relationship('Stand', back_populates='end_trace', foreign_keys=[end_id], lazy='select', init=False)
    turn_nb:Mapped[int] = mapped_column(Integer, nullable=False)
    trace:Mapped[str] = mapped_column(Text, nullable=False, default='[]')
    __tablename__:str = 'trace'

    # region fonctions
    def __iter__(self)->Iterator[TracePoint]:
        for lat, lng, alt in cast(list[tuple[float, float, float]],literal_eval(self.trace)):
            yield TracePoint(lat, lng, alt if alt else None)
    
    def __len__(self)->int:
        return len(cast(list[tuple[float, float, float]],literal_eval(self.trace)))

    def set_trace(self, trace:Iterable[TracePoint|tuple[float, float, float|None]])->None:
        '''
            sterilise et defini la valeure du champ trace
            !!! ne commit pas les changement !!
        '''
        sterilised_trace:list[tuple[float, float, float|None]] = []
        for point in trace:
            sterilised_trace.append((point[0], point[1], point[2]))
        self.trace = str(sterilised_trace)#type:ignore
        
    def has_alt(self)-> bool:
        return all((bool(point.alt) for point in self))
    
    def get_dist(self)->float:
        dist:float = 0
        last_point = self.start.lat, self.start.lng
        for lat, lng, alt in self:  # pyright: ignore[reportUnusedVariable]
            dist += calc_points_dist(lat, lng, last_point[0], last_point[1])
            last_point = lat, lng
        dist += calc_points_dist(self.end.lat, self.end.lng, last_point[0], last_point[1])
        return dist

    def is_last_trace(self)->bool:
        #ic(self.end == self.parcours.end_stand and self.end.end_trace.filter_by(turn_nb=self.turn_nb+1).count()==0, self.end , self.parcours.end_stand, self.end.end_trace.filter_by(turn_nb=self.turn_nb+1).count())
        return bool(self.end == self.parcours.end_stand and self.end.end_trace.filter_by(turn_nb=self.turn_nb+1).count()==0)
    
    def is_first_trace(self)->bool:
        return bool(self.start == self.parcours.start_stand and self.turn_nb==1)

    def get_next_trace(self)->Trace|None:
        if self.end == self.parcours.start_stand:
            return self.end.start_trace.filter_by(turn_nb=self.turn_nb+1).first()
        else:
            return self.end.start_trace.filter_by(turn_nb=self.turn_nb).first()

    def get_last_trace(self)->Trace|None:
        if self.start == self.parcours.start_stand:
            return self.start.end_trace.filter_by(turn_nb=self.turn_nb-1).first()
        else:
            return self.start.end_trace.filter_by(turn_nb=self.turn_nb).first()

    # endregion

class Edition(Model):
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    name:Mapped[str]= mapped_column(String(40), nullable=False)
    event_id:Mapped[int]=mapped_column(Integer, ForeignKey('event.id'), nullable=False)
    parcours:DynamicMapped[Parcours] = relationship('Parcours', secondary=editions_parcours, back_populates='editions', lazy ='dynamic', init=False)
    inscriptions:DynamicMapped[Inscription]=relationship('Inscription', back_populates='edition', lazy='dynamic', init=False)
    edition_date:Mapped[datetime] = mapped_column( DateTime, nullable=False)
    first_inscription:Mapped[datetime] = mapped_column( DateTime, nullable=False)
    last_inscription:Mapped[datetime] =mapped_column( DateTime, nullable=False)
    description:Mapped[str] = mapped_column(Text, nullable=False, default='')
    creation_date:Mapped[datetime]=mapped_column(DateTime, nullable=False, default=datetime.now)
    rdv_lat:Mapped[float] = mapped_column( Float, nullable=False, default=46.58)
    rdv_lng:Mapped[float] = mapped_column( Float, nullable=False, default=6.52)
    passage_keys:DynamicMapped[PassageKey]=relationship('PassageKey', back_populates='edition', foreign_keys='PassageKey.edition_id', lazy='dynamic', init=False)
    __tablename__:str = 'edition'

    @property
    def description_html(self)-> str:
        return get_html_from_markdown(self.description)

class Inscription(Model):
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id:Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False)
    inscrit:Mapped[User] = relationship('User', back_populates='inscriptions', init=False)
    event_id:Mapped[int]=mapped_column(Integer, ForeignKey('event.id'), nullable=False)
    event :Mapped[Event]= relationship('Event', back_populates='inscrits', init=False)
    edition_id:Mapped[int]=mapped_column(Integer, ForeignKey('edition.id'), nullable=False)
    edition:Mapped[Edition] = relationship('Edition', back_populates='inscriptions', init=False)
    parcours_id:Mapped[int]=mapped_column(Integer, ForeignKey('parcours.id'), nullable=False)
    parcours:Mapped[Parcours] = relationship('Parcours', back_populates='inscriptions', init=False)
    dossard:Mapped[int]=mapped_column(Integer)
    passages:DynamicMapped[Passage]=relationship('Passage', back_populates='inscription', lazy='dynamic', init=False)
    end:Mapped[str]=mapped_column(String(10)) # abandon, disqual, absent, finish or None
    creation_date:Mapped[datetime]=mapped_column(DateTime, nullable=False, default=datetime.now)
    present:Mapped[bool]=mapped_column(Boolean, nullable=False, default=False)
    __tablename__:str = 'inscription'
    # region funcs
    def has_started(self)->bool:
        return bool(self.passages.count())
    
    def get_last_passage(self):
        return self.passages.order_by(Passage.time_stamp.desc()).first()
    
    def get_first_passage(self):
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
    def start_time(self):
        first_passage = self.get_first_passage()
        return first_passage.time_stamp if first_passage else None

    @property
    def last_time(self):
        last_passage = self.get_last_passage()
        return last_passage.time_stamp if last_passage else None
    
    def get_time(self)->timedelta|None:
        if not self.has_started() or not self.last_time or not self.start_time:
            return None
        return self.last_time - self.start_time

    def get_run(self)-> list[bool|None]:
        user_passages:list[Passage] = self.passages.filter(Passage.time_stamp<=self.get_last_passage().time_stamp).all()  # pyright: ignore[reportOptionalMemberAccess]
        run:list[bool|None]=[]
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
        return run[-1] is not None

    @property
    def rank(self)->int|str|None:
        if self.end != 'finish':
            return {'abandon':'abandon', 'disqual':'disqualifié', 'absent':'absent'}.get(str(self.end), None)
        # all inscriptions that are in the same parcours and edition
        inscriptions = Inscription.query.filter(Inscription.parcours==self.parcours, Inscription.edition==self.edition)
        # get all the inscription that there last time is smaller than this one
        inscriptions = inscriptions.filter(not_(Inscription.passages.any(Passage.time_stamp>self.get_time())))#type:ignore[no-untyped-call]
        # get only those that have finished
        inscriptions = inscriptions.filter(Inscription.end=='finish')
        return inscriptions.count()+1

    # endregion

class PassageKey(Model):
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id:Mapped[int]=mapped_column(Integer, ForeignKey('event.id'), nullable=False)
    event:Mapped[Event]=relationship('Event', back_populates='passage_keys', init=False)
    edition_id:Mapped[int]=mapped_column(Integer, ForeignKey('edition.id'), nullable=False)
    edition:Mapped[Edition] = relationship('Edition', back_populates='passage_keys', init=False)
    stands:DynamicMapped[Stand]=relationship('Stand', secondary=passagekey_stand, back_populates='passage_keys', lazy='dynamic', init=False)
    passages:DynamicMapped[Passage]=relationship('Passage', back_populates='key', lazy='dynamic', init=False)
    key:Mapped[str]=mapped_column(String(20), nullable=False, unique=True)
    name:Mapped[str]=mapped_column(String(40), nullable=False)
    creation_date:Mapped[datetime]=mapped_column(DateTime, nullable=False, default=datetime.now)
    __tablename__:str = 'passage_key'

class Passage(Model):
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    time_stamp:Mapped[datetime]=mapped_column(DateTime, nullable=False)
    key_id:Mapped[int|None]=mapped_column(Integer, ForeignKey('passage_key.id'), nullable=True) # pas de key implique demmaré par l'admin
    key:Mapped[PassageKey|None]=relationship('PassageKey', back_populates='passages', lazy='select', init=False)
    inscription_id:Mapped[int] = mapped_column(Integer, ForeignKey('inscription.id'), nullable=False)
    inscription:Mapped[Inscription]=relationship('Inscription', back_populates='passages', lazy='select', init=False)
    __tablename__:str = 'passage'

    def get_stand(self)->Stand:
        if self.key is None:
            stand = self.inscription.parcours.start_stand
        else:
            stand = self.key.stands.filter_by(parcours=self.inscription.parcours).first()
            if stand is None:
                stand = self.inscription.parcours.start_stand
        return stand
