from typing import Optional, Union
from flask import Flask

class Bcrypt:
    def __init__(self, app: Optional[Flask] = ...) -> None: ...
    def init_app(self, app: Flask) -> None: ...

    def generate_password_hash(
        self,
        password: str,
        rounds: Optional[int] = ...,
        prefix: Optional[bytes] = ...,
    ) -> bytes: ...

    def check_password_hash(
        self,
        pw_hash: str,
        password: Union[str, bytes]
    ) -> bool: ...