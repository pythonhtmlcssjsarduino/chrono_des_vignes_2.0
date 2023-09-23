from typing import Any
from wtforms import validators

class DataRequired:
    def __init__(self, message=None):
        self.validator = validators.DataRequired(message)

    def __call__(self, form, field) -> Any:
        self.validator.__call__(form, field)

class Length:
    def __init__(self,min = -1, max=-1, message=None):
        self.validator = validators.Length(min,max,message)

    def __call__(self, form, field) -> Any:
        self.validator.__call__(form, field)

class EqualTo:
    def __init__(self,fieldname, message=None):
        self.validator = validators.EqualTo(fieldname,message)

    def __call__(self, form, field) -> Any:
        self.validator.__call__(form, field)