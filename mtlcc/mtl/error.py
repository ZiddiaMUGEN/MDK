import os

from mtl.shared import Location

class TranslationError(Exception):
    message: str

    def __init__(self, message: str, location: Location):
        super().__init__(f"Translation error at {os.path.realpath(location.filename)}:{location.line}: {message}")
        self.message = f"{os.path.realpath(location.filename)}:{location.line}: {message}"