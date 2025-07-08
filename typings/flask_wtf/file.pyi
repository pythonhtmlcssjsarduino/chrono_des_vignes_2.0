# flask_wtf/file.pyi

from typing import Any, Optional
from wtforms.fields.core import Field
from werkzeug.datastructures import FileStorage

class FileAllowed:
    def __init__(self, upload_set: Any, message: Optional[str] = ...) -> None: ...
    def __call__(self, form: Any, field: Any) -> None: ...

class FileRequired:
    def __init__(self, message: Optional[str] = ...) -> None: ...
    def __call__(self, form: Any, field: Any) -> None: ...

class FileField(Field):
    data: Optional[FileStorage]
    name: str

    def process_formdata(self, valuelist: list[Any]) -> None: ...
    def has_file(self) -> bool: ...
