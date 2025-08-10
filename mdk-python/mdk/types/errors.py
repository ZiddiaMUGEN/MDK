class TriggerException(Exception):
    def __init__(self, msg: str, file: str, line: int):
        self.msg = msg
        self.file = file
        self.line = line
    def get_message(self) -> str:
        return f"Compilation terminated with an error.\n\t{self.msg}\nat {self.file}:{self.line}"
    
class CompilationException(Exception):
    pass