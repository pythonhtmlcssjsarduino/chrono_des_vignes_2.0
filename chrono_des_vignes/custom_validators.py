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

from typing import override
from wtforms import validators
from datetime import datetime

from chrono_des_vignes.models import get_column_max_length
from chrono_des_vignes import db
from wtforms import StringField, DateTimeField
from wtforms.form import BaseForm

Base = db.Model

class Email(validators.Email):
    def __init__(self, message:str|None=None):
        super().__init__(message)

    @override
    def __call__(self, form: BaseForm, field:StringField)->None:
        super().__call__(form, field)

class DataRequired:
    def __init__(self, message:str|None=None):
        self.validator: validators.DataRequired = validators.DataRequired(message)

    def __call__(self, form: BaseForm, field: StringField)->None:
        self.validator.__call__(form, field)

class InputRequired:
    def __init__(self, message:str|None=None):
        self.validator: validators.InputRequired = validators.InputRequired(message)
    def __call__(self, form: BaseForm, field: StringField)->None:
        self.validator.__call__(form, field)

class Length:
    def __init__(self,min:int = -1, max:int=-1, message:str|None=None):
        self.validator: validators.Length = validators.Length(min,max,message)

    def __call__(self, form: BaseForm, field: StringField)->None:
        self.validator.__call__(form, field)

class DbLength(Length):
    def __init__(self, table:type[Base], column:str, min:int=-1, message:str|None=None):
        max = get_column_max_length(table, column)
        super().__init__(min, max, message)

class EqualTo:
    def __init__(self, fieldname: str, message:str|None=None):
        self.validator: validators.EqualTo = validators.EqualTo(fieldname,message)

    def __call__(self, form: BaseForm, field: StringField)->None:
        self.validator.__call__(form, field)

class DateTimeNotPast:
    def __init__(self, message:str|None=None):
        self.message:str=message if message else 'The date cannot be in the past!'

    def __call__(self,form: BaseForm, field: DateTimeField)->None:
        if field.render_kw.get('disabled') == "disabled":
            return
        if field.data is None:
            return
        if field.data.date() < datetime.now().date():
            raise validators.ValidationError(self.message)

class DateTimeBefore:
    def __init__(self, other_field:str, message:str|None=None):
        self.other_field:str = other_field
        self.message:str|None = message

    def __call__(self, form: BaseForm, field: DateTimeField)->None:
        try:
            other = form[self.other_field]
        except KeyError:
            raise validators.ValidationError(field.gettext(f"Invalid field name '{self.other_field}'."))

        if not isinstance(other, (DateTimeField)):
            raise validators.ValidationError(field.gettext(f"Field '{self.other_field}' is not a DateTimeField."))
        
        if field.render_kw.get('disabled') == "disabled":
            return
        if field.data is None or other.data is None:
            return

        if field.data.date() > other.data.date():
            message = self.message if self.message else f'The date must be before {self.other_field}!'
            raise validators.ValidationError(message)


class DonTExist:
    def __init__(self, table: type[Base], filter:str, id: int|None = None, message: str|None = None):
        self.message:str|None = message
        self.table: type[Base] = table
        self.filter:str =filter

    def __call__(self, form: BaseForm, field: StringField)->None:
        filter = {self.filter:field.data}
        first = db.session.query(self.table).filter_by(**filter).first()
        if first:
            message = self.message if self.message else 'This name is already took by someone else!'
            raise validators.ValidationError(message)