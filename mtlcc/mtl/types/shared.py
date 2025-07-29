from dataclasses import dataclass
import os

@dataclass
class Location:
    filename: str
    line: int

    def __str__(self):
        return f"{os.path.realpath(self.filename)}:{self.line}"

class TranslationError(Exception):
    message: str

    def __init__(self, message: str, location: Location):
        super().__init__(f"Translation error at {location}: {message}")
        self.message = f"{location}: {message}"