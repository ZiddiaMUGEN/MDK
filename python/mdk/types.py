from enum import Enum

## enums for types
class StateType(Enum):
    S = 0
    C = 1
    A = 2
    L = 3
    U = 4

class MoveType(Enum):
    I = 0
    A = 1
    H = 2
    U = 3

class PhysicsType(Enum):
    S = 0
    C = 1
    A = 2
    N = 3
    U = 4

class Transparency(Enum):
    none = 0, ## casing sucks here but None is a reserved word.
    Add = 1,
    Add1 = 2,
    Sub = 3