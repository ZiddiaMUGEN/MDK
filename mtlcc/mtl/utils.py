from typing import Optional
from enum import Enum

def tryParseFloat(input: str) -> Optional[float]:
    try:
        return float(input)
    except ValueError:
        return None
    
def tryParseInt(input: str) -> Optional[int]:
    try:
        return int(input)
    except ValueError:
        return None
    
def tryParseBool(input: str) -> Optional[bool]:
    if input == "true": return True
    elif input == "false": return False
    else: return None

