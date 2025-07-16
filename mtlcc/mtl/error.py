import os

class TranslationError(Exception):
    def __init__(self, message: str, filename: str, line: int):
        super().__init__(f"Translation error at {os.path.realpath(filename)}:{line}: {message}")