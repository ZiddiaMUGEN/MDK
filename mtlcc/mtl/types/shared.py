from dataclasses import dataclass
import os
import enum

class DebugCategory(enum.Enum):
    VERSION_HEADER = 0
    VARIABLE_TABLE = 1
    VARIABLE_ALLOCATION = 2
    TYPE_DEFINITION = 3
    TRIGGER_DEFINITION = 4
    TEMPLATE_DEFINITION = 5
    LOCATION = 6
    STATEDEF = 7

@dataclass
class Location:
    filename: str
    line: int

    def __str__(self):
        return f"{os.path.realpath(self.filename)}:{self.line}"
    
class DebuggerError(Exception):
    pass

class TranslationError(Exception):
    message: str

    def __init__(self, message: str, location: Location):
        super().__init__(f"Translation error at {location}: {message}")
        self.message = f"{location}: {message}"