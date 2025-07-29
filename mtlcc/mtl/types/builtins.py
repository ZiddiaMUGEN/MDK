from mtl.types.translation import *

from inspect import currentframe

def line_number() -> int:
    cf = currentframe()
    if cf != None and cf.f_back != None:
        return cf.f_back.f_lineno
    else:
        return 0

BUILTIN_ANY = TypeDefinition("any", TypeCategory.BUILTIN_DENY, 32, [], Location("mtl/builtins.py", line_number()))

BUILTIN_INT = TypeDefinition("int", TypeCategory.BUILTIN, 32, [], Location("mtl/builtins.py", line_number()))
BUILTIN_FLOAT = TypeDefinition("float", TypeCategory.BUILTIN, 32, [], Location("mtl/builtins.py", line_number()))
BUILTIN_SHORT = TypeDefinition("short", TypeCategory.BUILTIN, 16, [], Location("mtl/builtins.py", line_number()))
BUILTIN_BYTE = TypeDefinition("byte", TypeCategory.BUILTIN, 8, [], Location("mtl/builtins.py", line_number()))
BUILTIN_CHAR = TypeDefinition("char", TypeCategory.BUILTIN, 8, [], Location("mtl/builtins.py", line_number()))
BUILTIN_BOOL = TypeDefinition("bool", TypeCategory.BUILTIN, 1, [], Location("mtl/builtins.py", line_number()))
BUILTIN_CINT = TypeDefinition("cint", TypeCategory.BUILTIN_DENY, 32, [], Location("mtl/builtins.py", line_number()))
BUILTIN_STRING = TypeDefinition("string", TypeCategory.BUILTIN_DENY, 32, [], Location("mtl/builtins.py", line_number()))
BUILTIN_TYPE = TypeDefinition("type", TypeCategory.BUILTIN, 32, [], Location("mtl/builtins.py", line_number()))
BUILTIN_VECTOR = TypeDefinition("vector", TypeCategory.BUILTIN_STRUCTURE, 32, ["X:float", "Y:float"], Location("mtl/builtins.py", line_number()))

BUILTIN_STATETYPE = TypeDefinition("StateType", TypeCategory.STRING_ENUM, 32, ["S", "C", "A", "L", "U"], Location("mtl/builtins.py", line_number()))
BUILTIN_MOVETYPE = TypeDefinition("MoveType", TypeCategory.STRING_ENUM, 32, ["A", "I", "H", "U"], Location("mtl/builtins.py", line_number()))
BUILTIN_PHYSICSTYPE = TypeDefinition("PhysicsType", TypeCategory.STRING_ENUM, 32, ["S", "C", "A", "N", "U"], Location("mtl/builtins.py", line_number()))
BUILTIN_HITTYPE = TypeDefinition("HitType", TypeCategory.STRING_FLAG, 32, ["S", "C", "A"], Location("mtl/builtins.py", line_number()))
BUILTIN_HITATTR = TypeDefinition("HitAttr", TypeCategory.STRING_FLAG, 32, ["N", "S", "H", "A", "T", "P"], Location("mtl/builtins.py", line_number()))
BUILTIN_TRANSTYPE = TypeDefinition("TransType", TypeCategory.STRING_ENUM, 32, ["add", "add1", "sub", "none"], Location("mtl/builtins.py", line_number()))
BUILTIN_ASSERTTYPE = TypeDefinition("AssertType", TypeCategory.STRING_ENUM, 32, ["Intro", "Invisible", "RoundNotOver", "NoBarDisplay", "NoBG", "NoFG", "NoStandGuard", "NoCrouchGuard", "NoAirGuard", "NoAutoTurn", "NoJuggleCheck", "NoKOSnd", "NoKOSlow", "NoKO", "NoShadow", "GlobalNoShadow", "NoMusic", "NoWalk", "TimerFreeze", "Unguardable"], Location("mtl/builtins.py", line_number()))
BUILTIN_BINDTYPE = TypeDefinition("BindType", TypeCategory.STRING_ENUM, 32, ["Foot", "Mid", "Head"], Location("mtl/builtins.py", line_number()))
BUILTIN_POSTYPE = TypeDefinition("PosType", TypeCategory.STRING_ENUM, 32, ["P1", "P2", "Front", "Back", "Left", "Right", "None"], Location("mtl/builtins.py", line_number()))
BUILTIN_WAVETYPE = TypeDefinition("WaveType", TypeCategory.STRING_ENUM, 32, ["Sine", "Square", "SineSquare", "Off"], Location("mtl/builtins.py", line_number()))
BUILTIN_HELPERTYPE = TypeDefinition("HelperType", TypeCategory.STRING_ENUM, 32, ["Normal", "Player", "Proj"], Location("mtl/builtins.py", line_number()))
BUILTIN_HITFLAG = TypeDefinition("HitFlag", TypeCategory.STRING_FLAG, 32, ["H", "L", "A", "M", "F", "D", "+", "-"], Location("mtl/builtins.py", line_number()))
BUILTIN_GUARDFLAG = TypeDefinition("GuardFlag", TypeCategory.STRING_FLAG, 32, ["H", "L", "A", "M"], Location("mtl/builtins.py", line_number()))
BUILTIN_TEAMTYPE = TypeDefinition("TeamType", TypeCategory.STRING_ENUM, 32, ["E", "B", "F"], Location("mtl/builtins.py", line_number()))
BUILTIN_HITANIMTYPE = TypeDefinition("HitAnimType", TypeCategory.STRING_ENUM, 32, ["Light", "Medium", "Hard", "Back", "Up", "DiagUp"], Location("mtl/builtins.py", line_number()))
BUILTIN_ATTACKTYPE = TypeDefinition("AttackType", TypeCategory.STRING_ENUM, 32, ["High", "Low", "Trip", "None"], Location("mtl/builtins.py", line_number()))
BUILTIN_PRIORITYTYPE = TypeDefinition("PriorityType", TypeCategory.STRING_ENUM, 32, ["Hit", "Miss", "Dodge"], Location("mtl/builtins.py", line_number()))
BUILTIN_HITVARTYPE = TypeDefinition("HitVarType", TypeCategory.STRING_ENUM, 32, ["isbound"], Location("mtl/builtins.py", line_number()))
BUILTIN_CONSTTYPE = TypeDefinition("ConstType", TypeCategory.STRING_ENUM, 32, ["movement.yaccel"], Location("mtl/builtins.py", line_number()))
BUILTIN_STAGEVAR = TypeDefinition("StageVarType", TypeCategory.STRING_ENUM, 32, [], Location("mtl/builtins.py", line_number()))

BUILTIN_NUMERIC = TypeDefinition("numeric", TypeCategory.UNION, 32, ["int", "float"], Location("mtl/builtins.py", line_number()))
BUILTIN_PREFINT = TypeDefinition("prefixed_int", TypeCategory.UNION, 32, ["cint", "int"], Location("mtl/builtins.py", line_number()))
BUILTIN_SPRITE = TypeDefinition("sprite", TypeCategory.ALIAS, 32, ["prefixed_int"], Location("mtl/builtins.py", line_number()))
BUILTIN_SOUND = TypeDefinition("sound", TypeCategory.ALIAS, 32, ["prefixed_int"], Location("mtl/builtins.py", line_number()))
BUILTIN_ANIM = TypeDefinition("anim", TypeCategory.ALIAS, 32, ["prefixed_int"], Location("mtl/builtins.py", line_number()))