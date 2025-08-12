from _typeshed import Incomplete

class TriggerException(Exception):
    msg: str
    file: str
    line: int
    def __init__(self, msg: str, file: str, line: int) -> None: ...
    def get_message(self) -> str: ...

class CompilationException(Exception): ...
