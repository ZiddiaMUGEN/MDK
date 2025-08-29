from enum import Enum, EnumType, Flag, auto

from mdk.types.context import CompilerContext
from mdk.types.expressions import Expression

class CompositeFlag(EnumType):
    def __getattr__(cls, name: str) -> Expression:
        ctx = CompilerContext.instance()

        ## find the FlagType which owns this Flag enum
        target_type = None
        for type_name in ctx.typedefs:
            typedef = ctx.typedefs[type_name]
            if hasattr(typedef, 'inner_type') and typedef.inner_type == cls: # type: ignore
                target_type = typedef
                break
        if target_type == None:
            raise Exception(f"Could not determine the type definition to use for composite flag type {cls.__name__}.")

        if name in cls.__members__:
            return Expression(f"{target_type.name}.{name}", target_type)
        for character in name:
            if character not in cls.__members__:
                raise AttributeError(f"Could not find member {character} on flag type {cls}.")
        return Expression(f"{target_type.name}.{name}", target_type)

class StateType(Enum):
    """State type defined in statedef properties."""
    S = 0
    C = 1
    A = 2
    L = 3
    U = 4

class MoveType(Enum):
    """Move type (attack/idle/hurt) defined in statedef properties."""
    A = 0
    I = 1
    H = 2
    U = 3

class PhysicsType(Enum):
    """Physics type defined in statedef properties."""
    S = 0
    C = 1
    A = 2
    N = 3
    U = 4

class HitType(Flag, metaclass=CompositeFlag):
    """Hit type as defined in e.g. a HitDef attr block."""
    S = 1
    C = auto()
    A = auto()

class HitAttr(Flag, metaclass=CompositeFlag):
    """Hit type as defined in e.g. a HitDef attr block."""
    N = 1
    S = auto()
    H = auto()
    A = auto()
    T = auto()
    P = auto()

class TransType(Enum):
    """Type of transparency to apply in a visual display."""
    Add = 0
    Add1 = 1
    AddAlpha = 2
    Sub = 3
    none = 4

class AssertType(Enum):
    """Assertions which can be applied via the AssertSpecial controller."""
    Intro = 0
    Invisible = 1
    RoundNotOver = 2
    NoBarDisplay = 3
    NoBG = 4
    NoFG = 5
    NoStandGuard = 6
    NoCrouchGuard = 7
    NoAirGuard = 8
    NoAutoTurn = 9
    NoJuggleCheck = 10
    NoKOSnd = 11
    NoKOSlow = 12
    NoKO = 13
    NoShadow = 14
    GlobalNoShadow = 15
    NoMusic = 16
    NoWalk = 17
    TimerFreeze = 18
    Unguardable = 19

class WaveType(Enum):
    """Wave type used for ForceFeedback controllers."""
    Sine = 0
    Square = 1
    SineSquare = 2
    Off = 3

class HelperType(Enum):
    """Type of helper to be spawned from a Helper controller."""
    Normal = 0
    Player = 1
    Proj = 2

class TeamType(Enum):
    """Target team type for controllers such as HitDef."""
    E = 0
    F = 1
    B = 2

class HitAnimType(Enum):
    """Animation type to use when the target is hit by a HitDef or similar."""
    Light = 0
    Medium = 1
    Hard = 2
    Back = 3
    Up = 4
    DiagUp = 5

class AttackType(Enum):
    """The type of the attack (indicates where the attack will land)."""
    High = 0
    Low = 1
    Trip = 2
    none = 3

class PriorityType(Enum):
    """Priority of an attack, for clashing HitDefs."""
    Hit = 0
    Miss = 1
    Dodge = 2

class PosType(Enum):
    """Indicates position to base offsets from in e.g. Explod, Helper controllers."""
    P1 = 0
    P2 = 1
    Front = 3
    Back = 4
    Left = 5
    Right = 6
    none = 7

class SpaceType(Enum):
    """(1.1 only) indicates the space to use when calculating positions for e.g. Explod, Helper controllers."""
    Screen = 0
    Stage = 1

class TeamModeType(Enum):
    """Indicates the team mode which is currently in use (for TeamMode trigger)."""
    Single = 0
    Simul = 1
    Turns = 2

class HitFlagType(Flag, metaclass=CompositeFlag):
    """Used for a hitflag in a HitDef controller."""
    H = 1
    L = auto()
    A = auto()
    F = auto()
    D = auto()
    M = auto()

class GuardFlagType(Flag, metaclass=CompositeFlag):
    """Used for a guardflag in a HitDef controller."""
    H = 1
    L = auto()
    A = auto()
    M = auto()

__all__ = [
    "StateType", "MoveType", "PhysicsType", "HitType", "HitAttr", "TransType", "AssertType",
    "WaveType", "HelperType", "TeamType", "HitAnimType", "AttackType", "PriorityType", "PosType",
    "SpaceType", "TeamModeType", "HitFlagType", "GuardFlagType",
    "CompositeFlag"
]