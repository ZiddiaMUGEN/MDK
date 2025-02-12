import uuid

ENABLED_MDK_DEBUG: bool = True

## debug logging, done the worst possible way
def debug(msg: str):
    if ENABLED_MDK_DEBUG: print(msg)

## UUID generator
def short_uuid() -> str:
    return str(uuid.uuid4())[:8]

## formatters from Python types to CNS types
def format_tuple(tp: tuple) -> str:
    return f"{tp[0]}, {tp[1]}"

def format_bool(b: bool) -> str:
    return "1" if b else "0"