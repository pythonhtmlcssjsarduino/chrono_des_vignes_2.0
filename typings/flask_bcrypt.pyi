from typing import Optional, Union
from flask import Flask

class Bcrypt:
    def __init__(self, app: Optional[Flask] = ...) -> None: ...
    def init_app(self, app: Flask) -> None: ...

    def generate_password_hash(
        self,
        password: Union[str, bytes],
        rounds: Optional[int] = ...,
        prefix: Optional[bytes] = ...,
    ) -> bytes: ...

    def check_password_hash(
        self,
        pw_hash: Union[str, bytes],
        password: Union[str, bytes]
    ) -> bool: ...