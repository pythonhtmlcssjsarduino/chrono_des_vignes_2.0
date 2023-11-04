from wtforms import validators
from datetime import datetime

class DataRequired:
    def __init__(self, message=None):
        self.validator = validators.DataRequired(message)

    def __call__(self, form, field):
        self.validator.__call__(form, field)

class Length:
    def __init__(self,min = -1, max=-1, message=None):
        self.validator = validators.Length(min,max,message)

    def __call__(self, form, field):
        self.validator.__call__(form, field)

class EqualTo:
    def __init__(self, fieldname, message=None):
        self.validator = validators.EqualTo(fieldname,message)

    def __call__(self, form, field):
        self.validator.__call__(form, field)

class DateTimeNotPast:
    def __init__(self, message=None):
        self.message=message if message else 'The date cannot be in the past!'

    def __call__(self,form, field):
        if field.render_kw.get('disabled') == "disabled":
            return
        print('check not past')
        if field.data < datetime.now():
            print('is past')
            raise validators.ValidationError(self.message)

class DateTimeBefore:
    def __init__(self, other_field, message=None):
        self.other_field = other_field
        self.message = message

    def __call__(self, form, field):
        try:
            other = form[self.other_field]
        except KeyError:
            raise validators.ValidationError(field.gettext(f"Invalid field name '{self.other_field}'."))

        if field.render_kw.get('disabled') == "disabled":
            return

        if field.data >= other.data:
            message = self.message if self.message else f'The date must be before {self.other_field}!'
            raise validators.ValidationError(message)


class DonTExist:
    def __init__(self, table, filter:[str], id = None, message = None):
        self.message = message
        self.table = table
        self.filter =filter

    def __call__(self, form, field):
        filter = {self.filter:field.data}
        first = self.table.query.filter_by(**filter).first()
        if first and field.data != getattr(first, self.filter):
            message = self.message if self.message else 'This name is already took by someone else!'
            raise validators.ValidationError(message)