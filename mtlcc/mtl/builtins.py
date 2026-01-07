from mtl.types.context import TranslationContext
from mtl.types.translation import *
from mtl.types.shared import TranslationError
from mtl.types.builtins import *
from mtl.utils.compiler import find_type, find_statedef, get_widest_match, compiler_internal
from mtl.utils.func import tryparse
from mtl.writer import emit_enum

from ctypes import c_int32

def getBaseTypes() -> list[TypeDefinition]:
    return [
        BUILTIN_ANY,
        BUILTIN_INT,
        BUILTIN_FLOAT,
        BUILTIN_SHORT,
        BUILTIN_BYTE,
        BUILTIN_CHAR,
        BUILTIN_BOOL,
        BUILTIN_TARGET,
        BUILTIN_STATE,
        ## this is a special type which is used to represent a type in the compiler state.
        ## if it's used at runtime, it is replaced with the integer ID of the type it represents.
        BUILTIN_TYPE,
        ## this is a special int type which can support character prefixes. it's used for things like sounds and anims.
        ## it's not legal to create a variable with this type.
        BUILTIN_CINT,
        ## this represents strings, which are not legal to construct.
        BUILTIN_STRING,
        ## these are built-in structure types
        BUILTIN_VECTOR,
        ## these are built-in enum/flag types
        BUILTIN_STATETYPE,
        BUILTIN_MOVETYPE,
        BUILTIN_PHYSICSTYPE,
        BUILTIN_HITTYPE,
        BUILTIN_HITATTR,
        BUILTIN_TRANSTYPE,
        BUILTIN_ASSERTTYPE,
        BUILTIN_BINDTYPE,
        BUILTIN_POSTYPE,
        BUILTIN_SPACETYPE,
        BUILTIN_WAVETYPE,
        BUILTIN_HELPERTYPE,
        BUILTIN_HITFLAG,
        BUILTIN_GUARDFLAG,
        BUILTIN_TEAMTYPE,
        BUILTIN_HITANIMTYPE,
        BUILTIN_ATTACKTYPE,
        BUILTIN_PRIORITYTYPE,
        BUILTIN_HITVARTYPE_INT,
        BUILTIN_HITVARTYPE_FLOAT,
        BUILTIN_HITVARTYPE_BOOL,
        BUILTIN_CONSTTYPE_INT,
        BUILTIN_CONSTTYPE_FLOAT,
        BUILTIN_CONSTTYPE_BOOL,
        BUILTIN_STAGEVAR,
        ## built-in union types
        BUILTIN_NUMERIC,
        BUILTIN_PREFINT,
        BUILTIN_SPRITE,
        BUILTIN_SOUND,
        BUILTIN_ANIM,
        BUILTIN_STATENO
    ]

def getBaseTriggers() -> list[TriggerDefinition]:
    baseTriggers: list[TriggerDefinition] =  [
        ## MUGEN trigger functions
        TriggerDefinition("abs", BUILTIN_INT, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("abs", BUILTIN_FLOAT, None, [TypeParameter("exprn", BUILTIN_FLOAT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("acos", BUILTIN_FLOAT, None, [TypeParameter("exprn", BUILTIN_FLOAT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("AiLevel", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("Alive", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("Anim", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("AnimElem", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("AnimElemNo", BUILTIN_INT, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("AnimElemTime", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("AnimElemTime", BUILTIN_INT, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("AnimExist", BUILTIN_BOOL, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("AnimExist", BUILTIN_BOOL, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("AnimTime", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("asin", BUILTIN_FLOAT, None, [TypeParameter("exprn", BUILTIN_FLOAT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("atan", BUILTIN_FLOAT, None, [TypeParameter("exprn", BUILTIN_FLOAT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("AuthorName", BUILTIN_STRING, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("BackEdgeBodyDist", BUILTIN_FLOAT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("BackEdgeDist", BUILTIN_FLOAT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("CameraPos", BUILTIN_VECTOR, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("CanRecover", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("ceil", BUILTIN_INT, None, [TypeParameter("exprn", BUILTIN_FLOAT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("Command", BUILTIN_STRING, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("cond", BUILTIN_ANY, builtin_cond, [TypeParameter("condition", BUILTIN_BOOL), TypeParameter("exprn1", BUILTIN_ANY), TypeParameter("exprn2", BUILTIN_ANY)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("Const", BUILTIN_INT, None, [TypeParameter("param_name", BUILTIN_CONSTTYPE_INT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("Const", BUILTIN_FLOAT, None, [TypeParameter("param_name", BUILTIN_CONSTTYPE_FLOAT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("Const", BUILTIN_BOOL, None, [TypeParameter("param_name", BUILTIN_CONSTTYPE_BOOL)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("Const240p", BUILTIN_FLOAT, None, [TypeParameter("exprn", BUILTIN_FLOAT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("Const480p", BUILTIN_FLOAT, None, [TypeParameter("exprn", BUILTIN_FLOAT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("Const720p", BUILTIN_FLOAT, None, [TypeParameter("exprn", BUILTIN_FLOAT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("cos", BUILTIN_FLOAT, None, [TypeParameter("exprn", BUILTIN_FLOAT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("Ctrl", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("DrawGame", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("e", BUILTIN_FLOAT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("exp", BUILTIN_FLOAT, None, [TypeParameter("exprn", BUILTIN_FLOAT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("Facing", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("floor", BUILTIN_INT, None, [TypeParameter("exprn", BUILTIN_FLOAT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("FrontEdgeBodyDist", BUILTIN_FLOAT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("FrontEdgeDist", BUILTIN_FLOAT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("fvar", BUILTIN_FLOAT, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("GameHeight", BUILTIN_FLOAT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("GameTime", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("GameWidth", BUILTIN_FLOAT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("GetHitVar", BUILTIN_INT, None, [TypeParameter("param_name", BUILTIN_HITVARTYPE_INT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("GetHitVar", BUILTIN_FLOAT, None, [TypeParameter("param_name", BUILTIN_HITVARTYPE_FLOAT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("GetHitVar", BUILTIN_BOOL, None, [TypeParameter("param_name", BUILTIN_HITVARTYPE_BOOL)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("HitCount", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("HitDefAttr", BUILTIN_ANY, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("HitFall", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("HitOver", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("HitPauseTime", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("HitShakeOver", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("HitVel", BUILTIN_VECTOR, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("ID", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("ifelse", BUILTIN_ANY, builtin_cond, [TypeParameter("condition", BUILTIN_BOOL), TypeParameter("exprn1", BUILTIN_ANY), TypeParameter("exprn2", BUILTIN_ANY)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("InGuardDist", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("IsHelper", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("IsHelper", BUILTIN_BOOL, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("IsHomeTeam", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("Life", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("LifeMax", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("ln", BUILTIN_FLOAT, None, [TypeParameter("exprn", BUILTIN_FLOAT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("log", BUILTIN_FLOAT, None, [TypeParameter("exp1", BUILTIN_FLOAT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("Lose", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("LoseKO", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("LoseTime", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("MatchNo", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("MatchOver", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("MoveContact", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("MoveGuarded", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("MoveHit", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("MoveReversed", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("MoveType", BUILTIN_MOVETYPE, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("Name", BUILTIN_STRING, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("NumEnemy", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("NumExplod", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("NumExplod", BUILTIN_INT, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("NumHelper", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("NumHelper", BUILTIN_INT, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("NumPartner", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("NumProj", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("NumProjID", BUILTIN_INT, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("NumTarget", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("NumTarget", BUILTIN_INT, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("P1Name", BUILTIN_STRING, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("P2BodyDist", BUILTIN_VECTOR, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("P2Dist", BUILTIN_VECTOR, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("P2Life", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("P2Name", BUILTIN_STRING, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("P2StateNo", BUILTIN_STATE, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("P3Name", BUILTIN_STRING, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("P4Name", BUILTIN_STRING, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("PalNo", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("ParentDist", BUILTIN_VECTOR, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("pi", BUILTIN_FLOAT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("Pos", BUILTIN_VECTOR, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("Power", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("PowerMax", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("PlayerIDExist", BUILTIN_BOOL, None, [TypeParameter("ID_number", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("PrevStateNo", BUILTIN_STATE, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("ProjCancelTime", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("ProjCancelTime", BUILTIN_INT, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("ProjContactTime", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("ProjContactTime", BUILTIN_INT, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("ProjGuardedTime", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("ProjGuardedTime", BUILTIN_INT, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("ProjHitTime", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("ProjHitTime", BUILTIN_INT, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("Random", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("RootDist", BUILTIN_VECTOR, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("RoundNo", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("RoundsExisted", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("RoundState", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("ScreenPos", BUILTIN_VECTOR, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("ScreenWidth", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("ScreenHeight", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("SelfAnimExist", BUILTIN_BOOL, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("sin", BUILTIN_FLOAT, None, [TypeParameter("exprn", BUILTIN_FLOAT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("StateNo", BUILTIN_STATE, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("StateType", BUILTIN_STATETYPE, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("StageVar", BUILTIN_STRING, None, [TypeParameter("param_name", BUILTIN_STAGEVAR)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("sysfvar", BUILTIN_FLOAT, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("sysvar", BUILTIN_INT, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("tan", BUILTIN_FLOAT, None, [TypeParameter("exprn", BUILTIN_FLOAT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("TeamSide", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("TicksPerSecond", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("Time", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("var", BUILTIN_INT, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("Vel", BUILTIN_VECTOR, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("Win", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("WinKO", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("WinTime", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("WinPerfect", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),

        ## requirements because CNS is inconsistent
        ## it's legal to do `F(100)` instead of F100 in cint contexts. so it needs to be treated as a trigger...
        TriggerDefinition("F", BUILTIN_CINT, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("S", BUILTIN_CINT, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),

        ## redirection triggers
        TriggerDefinition("parent", BUILTIN_TARGET, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("root", BUILTIN_TARGET, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("helper", BUILTIN_TARGET, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("helper", BUILTIN_TARGET, None, [TypeParameter("id", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("target", BUILTIN_TARGET, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("target", BUILTIN_TARGET, None, [TypeParameter("id", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("partner", BUILTIN_TARGET, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("enemy", BUILTIN_TARGET, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("enemy", BUILTIN_TARGET, None, [TypeParameter("id", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("enemynear", BUILTIN_TARGET, None, [], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("enemynear", BUILTIN_TARGET, None, [TypeParameter("id", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("playerID", BUILTIN_TARGET, None, [TypeParameter("id", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),

        ## builtin operator functions
        TriggerDefinition("operator%", BUILTIN_INT, builtin_mod, [TypeParameter("expr1", BUILTIN_INT), TypeParameter("expr2", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.OPERATOR),
        TriggerDefinition("operator=", BUILTIN_BOOL, builtin_eq, [TypeParameter("expr1", BUILTIN_STRING), TypeParameter("expr2", BUILTIN_STRING)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.OPERATOR),
        TriggerDefinition("operator!=", BUILTIN_BOOL, builtin_neq, [TypeParameter("expr1", BUILTIN_STRING), TypeParameter("expr2", BUILTIN_STRING)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.OPERATOR),

        TriggerDefinition("operator&&", BUILTIN_BOOL, builtin_and, [TypeParameter("expr1", BUILTIN_BOOL), TypeParameter("expr2", BUILTIN_BOOL)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.OPERATOR),
        TriggerDefinition("operator||", BUILTIN_BOOL, builtin_or, [TypeParameter("expr1", BUILTIN_BOOL), TypeParameter("expr2", BUILTIN_BOOL)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.OPERATOR),
        TriggerDefinition("operator^^", BUILTIN_BOOL, builtin_xor, [TypeParameter("expr1", BUILTIN_BOOL), TypeParameter("expr2", BUILTIN_BOOL)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.OPERATOR),

        ## builtin constant/compiler functions
        TriggerDefinition("cast", BUILTIN_ANY, builtin_cast, [TypeParameter("expr", BUILTIN_ANY), TypeParameter("t", BUILTIN_TYPE)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("typeof", BUILTIN_TYPE, builtin_typeof, [TypeParameter("expr", BUILTIN_ANY)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("sizeof", BUILTIN_INT, builtin_sizeof, [TypeParameter("t", BUILTIN_TYPE)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("asint", BUILTIN_INT, builtin_asint, [TypeParameter("expr", BUILTIN_ANY)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        #TriggerDefinition("asenum", BUILTIN_ANY, builtin_asenum, [TypeParameter("i", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        #TriggerDefinition("asflag", BUILTIN_ANY, builtin_asflag, [TypeParameter("i", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("rescope", BUILTIN_TARGET, builtin_rescope, [TypeParameter("expr", BUILTIN_TARGET), TypeParameter("sc", BUILTIN_TARGET)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
        TriggerDefinition("tostateno", BUILTIN_INT, builtin_tostateno, [TypeParameter("expr", BUILTIN_STATE)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.BUILTIN),
    ]

    ## add generic operators for each of these builtin types.
    for typedef in [BUILTIN_INT, BUILTIN_FLOAT, BUILTIN_BOOL, BUILTIN_CHAR, BUILTIN_BYTE, BUILTIN_SHORT]:
        baseTriggers.append(TriggerDefinition("operator!", BUILTIN_BOOL, builtin_not, [TypeParameter("expr", typedef)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.OPERATOR))
        baseTriggers.append(TriggerDefinition("operator=", BUILTIN_BOOL, builtin_eq, [TypeParameter("expr1", typedef), TypeParameter("expr2", typedef)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.OPERATOR))
        baseTriggers.append(TriggerDefinition("operator!=", BUILTIN_BOOL, builtin_neq, [TypeParameter("expr1", typedef), TypeParameter("expr2", typedef)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.OPERATOR))
        baseTriggers.append(TriggerDefinition("operator:=", typedef, builtin_assign, [TypeParameter("expr1", typedef), TypeParameter("expr2", typedef)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.OPERATOR))

        if typedef != BUILTIN_BOOL:
            baseTriggers.append(TriggerDefinition("operator-", typedef, builtin_negate, [TypeParameter("expr", typedef)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.OPERATOR))
            baseTriggers.append(TriggerDefinition("operator+", typedef, builtin_add, [TypeParameter("expr1", typedef), TypeParameter("expr2", typedef)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.OPERATOR))
            baseTriggers.append(TriggerDefinition("operator-", typedef, builtin_sub, [TypeParameter("expr1", typedef), TypeParameter("expr2", typedef)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.OPERATOR))
            baseTriggers.append(TriggerDefinition("operator*", typedef, builtin_mult, [TypeParameter("expr1", typedef), TypeParameter("expr2", typedef)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.OPERATOR))
            baseTriggers.append(TriggerDefinition("operator**", typedef, builtin_exp, [TypeParameter("expr1", typedef), TypeParameter("expr2", typedef)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.OPERATOR))
            baseTriggers.append(TriggerDefinition("operator/", BUILTIN_FLOAT, builtin_div, [TypeParameter("expr1", typedef), TypeParameter("expr2", typedef)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.OPERATOR))
            baseTriggers.append(TriggerDefinition("operator<", BUILTIN_BOOL, builtin_lt, [TypeParameter("expr1", typedef), TypeParameter("expr2", typedef)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.OPERATOR))
            baseTriggers.append(TriggerDefinition("operator<=", BUILTIN_BOOL, builtin_lte, [TypeParameter("expr1", typedef), TypeParameter("expr2", typedef)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.OPERATOR))
            baseTriggers.append(TriggerDefinition("operator>", BUILTIN_BOOL, builtin_gt, [TypeParameter("expr1", typedef), TypeParameter("expr2", typedef)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.OPERATOR))
            baseTriggers.append(TriggerDefinition("operator>=", BUILTIN_BOOL, builtin_gte, [TypeParameter("expr1", typedef), TypeParameter("expr2", typedef)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.OPERATOR))

        if typedef != BUILTIN_FLOAT:
            baseTriggers.append(TriggerDefinition("operator~", typedef, builtin_bitnot, [TypeParameter("expr", typedef)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.OPERATOR))
            baseTriggers.append(TriggerDefinition("operator&", typedef, builtin_bitand, [TypeParameter("expr1", typedef), TypeParameter("expr2", typedef)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.OPERATOR))
            baseTriggers.append(TriggerDefinition("operator|", typedef, builtin_bitor, [TypeParameter("expr1", typedef), TypeParameter("expr2", typedef)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.OPERATOR))
            baseTriggers.append(TriggerDefinition("operator^", typedef, builtin_bitxor, [TypeParameter("expr1", typedef), TypeParameter("expr2", typedef)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.OPERATOR))

    ## add generic equality/assignment operators for int-equivalent types (stateno, anim)
    for typedef in [BUILTIN_STATE, BUILTIN_ANIM]:
        baseTriggers.append(TriggerDefinition("operator=", BUILTIN_BOOL, builtin_eq, [TypeParameter("expr1", typedef), TypeParameter("expr2", typedef)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.OPERATOR))
        baseTriggers.append(TriggerDefinition("operator!=", BUILTIN_BOOL, builtin_neq, [TypeParameter("expr1", typedef), TypeParameter("expr2", typedef)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.OPERATOR))
        baseTriggers.append(TriggerDefinition("operator:=", typedef, builtin_assign, [TypeParameter("expr1", typedef), TypeParameter("expr2", typedef)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.OPERATOR))

    ## add generic equality operators for the Enum and Flag builtin types which have triggers
    ## TODO: should this be done automatically for all user-defined enum/flag types also?
    ## it seems dumb to require the user to define their own equality operators on these types.
    for typedef in [
        BUILTIN_STATE, BUILTIN_STATETYPE, BUILTIN_MOVETYPE, BUILTIN_PHYSICSTYPE
    ]:
        baseTriggers.append(TriggerDefinition("operator=", BUILTIN_BOOL, builtin_eq, [TypeParameter("expr1", typedef), TypeParameter("expr2", typedef)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.OPERATOR))
        baseTriggers.append(TriggerDefinition("operator!=", BUILTIN_BOOL, builtin_neq, [TypeParameter("expr1", typedef), TypeParameter("expr2", typedef)], None, Location("mtl/builtins.py", line_number()), "", category = TriggerCategory.OPERATOR))

    for trig in baseTriggers:
        trig._lower = trig.name.lower()

    return baseTriggers

def builtin_cond(exprs: list[Expression], ctx: TranslationContext) -> Expression:
    if (widest := get_widest_match(exprs[1].type, exprs[2].type, ctx, compiler_internal(ctx.compiler_flags))) == None:
        raise TranslationError(f"Conditional expression (cond and ifelse) must provide 2 expressions with compatible types.", Location("mtl/builtins.py", line_number()))
    return Expression(widest, f"cond({exprs[0].value}, {exprs[1].value}, {exprs[2].value})")

def builtin_cast(exprs: list[Expression], ctx: TranslationContext) -> Expression:
    if exprs[1].type != BUILTIN_TYPE or (target_type := find_type(exprs[1].value, ctx)) == None:
        raise TranslationError(f"Second argument to cast must be a type name, not {exprs[1].value}", Location("mtl/builtins.py", line_number()))
    return Expression(target_type, exprs[0].value)

def builtin_typeof(exprs: list[Expression], ctx: TranslationContext) -> Expression:
    return Expression(BUILTIN_TYPE, exprs[0].type.name)

def builtin_sizeof(exprs: list[Expression], ctx: TranslationContext) -> Expression:
    if (target_type := find_type(exprs[0].value, ctx)) == None:
        raise TranslationError(f"Argument to sizeof must be a type name, not {exprs[0].value}", Location("mtl/builtins.py", line_number()))
    return Expression(BUILTIN_INT, str(target_type.size))

def builtin_asint(exprs: list[Expression], ctx: TranslationContext) -> Expression:
    return Expression(BUILTIN_INT, emit_enum(exprs[0].value, exprs[0].type))

def builtin_tostateno(exprs: list[Expression], ctx: TranslationContext) -> Expression:
    if (state := find_statedef(exprs[0].value, ctx)) == None or state.parameters.id == None:
        raise TranslationError(f"Could not find any state definition with name {exprs[0].value}.", Location("mtl/builtins.py", line_number()))
    return Expression(BUILTIN_INT, str(state.parameters.id))

def builtin_rescope(exprs: list[Expression], ctx: TranslationContext) -> Expression:
    target_scope = StateDefinitionScope(StateScopeType.SHARED, None)
    if exprs[1].value.startswith("(") and exprs[1].value.endswith(")"):
        exprs[1].value = exprs[1].value[1:-1]
    if exprs[1].value == "root":
        target_scope.type = StateScopeType.PLAYER
    elif exprs[1].value == "helper":
        target_scope.type = StateScopeType.HELPER
    elif exprs[1].value == "target":
        target_scope.type = StateScopeType.TARGET
    if exprs[1].value.lower().startswith("helper") and "(" in exprs[1].value:
        if (ival := tryparse(exprs[1].value.split("(")[1].split(")")[0], int)) != None:
            target_scope.target = ival
        target_scope.type = StateScopeType.HELPER
    return RescopeExpression(BUILTIN_TARGET, f"{exprs[0].value}", target_scope)

def builtin_not(exprs: list[Expression], ctx: TranslationContext) -> Expression:
    return Expression(BUILTIN_BOOL, f"(!{exprs[0].value})")

def builtin_negate(exprs: list[Expression], ctx: TranslationContext) -> Expression:
    return Expression(exprs[0].type, f"(-{exprs[0].value})")

def builtin_bitnot(exprs: list[Expression], ctx: TranslationContext) -> Expression:
    return Expression(exprs[0].type, f"(~{exprs[0].value})")

def builtin_binary(exprs: list[Expression], ctx: TranslationContext, op: str) -> Expression:
    if (result := get_widest_match(exprs[0].type, exprs[1].type, ctx, compiler_internal(ctx.compiler_flags))) != None:
        return Expression(result, f"({exprs[0].value} {op} {exprs[1].value})")
    raise TranslationError(f"Failed to convert an expression of type {exprs[0].type.name} to type {exprs[1].type.name} for operator {op}.", Location("mtl/builtins.py", line_number()))

def builtin_compare(exprs: list[Expression], ctx: TranslationContext, op: str) -> Expression:
    if get_widest_match(exprs[0].type, exprs[1].type, ctx, compiler_internal(ctx.compiler_flags)) != None:
        return Expression(BUILTIN_BOOL, f"({exprs[0].value} {op} {exprs[1].value})")
    raise TranslationError(f"Failed to convert an expression of type {exprs[0].type.name} to type {exprs[1].type.name} for operator {op}.", Location("mtl/builtins.py", line_number()))

def builtin_assign(exprs: list[Expression], ctx: TranslationContext) -> Expression:
    ## the output of the walrus operator needs to be masked.
    ## for example, in the expression `(myVar := true) * 5`, the expected result is 5.
    ## however if `myVar` is a 1-bit bool allocated at (0, 8), the resulting expression is
    ## `(var(0) := ((1 & 1) * 256)) * 5` which is incorrect.
    ## this step also needs to mask the RESULT of the walrus operator, and then shift right, producing e.g.
    ## `((var(0) := (((1 & 1) * 256)) & 256) / 256) * 5`
    ## that means adding the left-shift at the end of this expression.
    if isinstance(exprs[0], VariableExpression):
        exprs[0].value = f"var({exprs[0].allocation[0]})"
        if exprs[0].is_float: exprs[0].value = f"f{exprs[0].value}"
        if exprs[0].is_system: exprs[0].value = f"sys{exprs[0].value}"
    exprn = builtin_binary(exprs, ctx, ":=")
    if isinstance(exprs[0], VariableExpression):
        offset = exprs[0].allocation[1]
        if exprs[0].type.size != 32:
            start_pow2 = 2 ** exprs[0].allocation[1]
            end_pow2 = 2 ** (offset + exprs[0].type.size)
            mask = c_int32(end_pow2 - start_pow2)
            exprn.value = f"({exprn.value} & {mask.value})"
    return exprn

def builtin_add(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "+")
def builtin_sub(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "-")
def builtin_mult(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "*")
def builtin_div(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "/")
def builtin_mod(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "%")
def builtin_exp(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "**")
def builtin_xor(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "^^")
def builtin_bitand(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "&")
def builtin_bitxor(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "^")
def builtin_lt(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_compare(exprs, ctx, "<")
def builtin_lte(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_compare(exprs, ctx, "<=")
def builtin_gt(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_compare(exprs, ctx, ">")
def builtin_gte(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_compare(exprs, ctx, ">=")
def builtin_and(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "&&")
def builtin_or(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "||")

## these have special logic to push flag expressions into the flag_eq/flag_neq options.
def builtin_eq(exprs: list[Expression], ctx: TranslationContext) -> Expression:
    if exprs[0].type.category == TypeCategory.FLAG and exprs[1].type.category == TypeCategory.FLAG:
        return flag_eq(exprs, ctx)
    return builtin_compare(exprs, ctx, "=")
def builtin_neq(exprs: list[Expression], ctx: TranslationContext) -> Expression:
    if exprs[0].type.category == TypeCategory.FLAG and exprs[1].type.category == TypeCategory.FLAG:
        return flag_neq(exprs, ctx) 
    return builtin_compare(exprs, ctx, "!=")
def builtin_bitor(exprs: list[Expression], ctx: TranslationContext) -> Expression: 
    if exprs[0].type.category == TypeCategory.FLAG and exprs[1].type.category == TypeCategory.FLAG:
        return flag_join(exprs, ctx)
    return builtin_binary(exprs, ctx, "|")

def flag_eq(exprs: list[Expression], ctx: TranslationContext):
    if get_widest_match(exprs[0].type, exprs[1].type, ctx, compiler_internal(ctx.compiler_flags)) != None:
        return Expression(BUILTIN_BOOL, f"({exprs[0].value} & {exprs[1].value}) = {exprs[1].value}")
    raise TranslationError(f"Failed to convert an expression of type {exprs[0].type.name} to type {exprs[1].type.name} for flag membership.", Location("mtl/builtins.py", line_number()))

def flag_neq(exprs: list[Expression], ctx: TranslationContext):
    if get_widest_match(exprs[0].type, exprs[1].type, ctx, compiler_internal(ctx.compiler_flags)) != None:
        return Expression(BUILTIN_BOOL, f"({exprs[0].value} & {exprs[1].value}) != {exprs[1].value}")
    raise TranslationError(f"Failed to convert an expression of type {exprs[0].type.name} to type {exprs[1].type.name} for flag non-membership.", Location("mtl/builtins.py", line_number()))

def flag_join(exprs: list[Expression], ctx: TranslationContext):
    if get_widest_match(exprs[0].type, exprs[1].type, ctx, compiler_internal(ctx.compiler_flags)) != None:
        return Expression(exprs[0].type, f"({exprs[0].value} | {exprs[1].value})")
    raise TranslationError(f"Failed to convert an expression of type {exprs[0].type.name} to type {exprs[1].type.name} for flag combination.", Location("mtl/builtins.py", line_number()))

def getBaseTemplates() -> list[TemplateDefinition]:
    return [
        TemplateDefinition("AfterImage", [TemplateParameter("time", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("length", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("palcolor", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("palinvertall", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("palbright", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("palcontrast", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("palpostbright", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("paladd", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("palmul", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("timegap", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("framegap", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("trans", [TypeSpecifier(BUILTIN_TRANSTYPE)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("AfterImageTime", [TemplateParameter("time", [TypeSpecifier(BUILTIN_INT)], True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("AllPalFX", [TemplateParameter("time", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("add", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("mul", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("sinadd", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("invertall", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("color", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("AngleAdd", [TemplateParameter("value", [TypeSpecifier(BUILTIN_FLOAT)], True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("AngleDraw", [TemplateParameter("value", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("scale", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("AngleMul", [TemplateParameter("value", [TypeSpecifier(BUILTIN_FLOAT)], True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("AngleSet", [TemplateParameter("value", [TypeSpecifier(BUILTIN_FLOAT)], True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("AppendToClipboard", [TemplateParameter("text", [TypeSpecifier(BUILTIN_STRING)], True), TemplateParameter("params", [TypeSpecifier(BUILTIN_ANY, repeat = True)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("AssertSpecial", [TemplateParameter("flag", [TypeSpecifier(BUILTIN_ASSERTTYPE)], True), TemplateParameter("flag2", [TypeSpecifier(BUILTIN_ASSERTTYPE)], False), TemplateParameter("flag3", [TypeSpecifier(BUILTIN_ASSERTTYPE)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("AttackDist", [TemplateParameter("value", [TypeSpecifier(BUILTIN_INT)], True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("AttackMulSet", [TemplateParameter("value", [TypeSpecifier(BUILTIN_FLOAT)], True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("BGPalFX", [TemplateParameter("time", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("add", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("mul", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("sinadd", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("invertall", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("color", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("BindToParent", [TemplateParameter("time", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("facing", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("pos", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("BindToRoot", [TemplateParameter("time", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("facing", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("pos", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("BindToTarget", [TemplateParameter("time", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("id", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("pos", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_BINDTYPE)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("ChangeAnim", [TemplateParameter("value", [TypeSpecifier(BUILTIN_INT)], True), TemplateParameter("elem", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("ChangeAnim2", [TemplateParameter("value", [TypeSpecifier(BUILTIN_INT)], True), TemplateParameter("elem", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("ChangeState", [TemplateParameter("value", [TypeSpecifier(BUILTIN_STATENO)], True), TemplateParameter("ctrl", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("anim", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("ClearClipboard", [], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("CtrlSet", [TemplateParameter("ctrl", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("value", [TypeSpecifier(BUILTIN_BOOL)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("DefenceMulSet", [TemplateParameter("value", [TypeSpecifier(BUILTIN_FLOAT)], True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("DestroySelf", [], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("DisplayToClipboard", [TemplateParameter("text", [TypeSpecifier(BUILTIN_STRING)], True), TemplateParameter("params", [TypeSpecifier(BUILTIN_ANY, repeat = True)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("EnvColor", [TemplateParameter("value", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("time", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("under", [TypeSpecifier(BUILTIN_BOOL)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("EnvShake", [TemplateParameter("time", [TypeSpecifier(BUILTIN_INT)], True), TemplateParameter("freq", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("ampl", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("phase", [TypeSpecifier(BUILTIN_FLOAT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("Explod", [TemplateParameter("anim", [TypeSpecifier(BUILTIN_ANIM)], True), TemplateParameter("id", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("pos", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("postype", [TypeSpecifier(BUILTIN_POSTYPE)], False), TemplateParameter("space", [TypeSpecifier(BUILTIN_SPACETYPE)], False), TemplateParameter("facing", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("vfacing", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("bindtime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("vel", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("accel", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("random", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("removetime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("supermove", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("supermovetime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("pausemovetime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("scale", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("sprpriority", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("ontop", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("shadow", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("ownpal", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("removeongethit", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("ignorehitpause", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("trans", [TypeSpecifier(BUILTIN_TRANSTYPE)], False), TemplateParameter("angle", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("ExplodBindTime", [TemplateParameter("id", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("time", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("ForceFeedback", [TemplateParameter("waveform", [TypeSpecifier(BUILTIN_WAVETYPE)], False), TemplateParameter("time", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("freq", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_FLOAT, required = False), TypeSpecifier(BUILTIN_FLOAT, required = False), TypeSpecifier(BUILTIN_FLOAT, required = False)], False), TemplateParameter("ampl", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_FLOAT, required = False), TypeSpecifier(BUILTIN_FLOAT, required = False), TypeSpecifier(BUILTIN_FLOAT, required = False)], False), TemplateParameter("self", [TypeSpecifier(BUILTIN_BOOL)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("FallEnvShake", [], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("GameMakeint", [TemplateParameter("value", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("under", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("pos", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("random", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("Gravity", [], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("Helper", [TemplateParameter("helpertype", [TypeSpecifier(BUILTIN_HELPERTYPE)], False), TemplateParameter("name", [TypeSpecifier(BUILTIN_STRING)], False), TemplateParameter("id", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("pos", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("postype", [TypeSpecifier(BUILTIN_POSTYPE)], False), TemplateParameter("facing", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("stateno", [TypeSpecifier(BUILTIN_STATENO)], False), TemplateParameter("keyctrl", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("ownpal", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("supermovetime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("pausemovetime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("size.xscale", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("size.yscale", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("size.ground.back", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("size.ground.front", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("size.air.back", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("size.ait.front", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("size.height", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("size.proj.doscale", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("size.head.pos", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("size.mid.pos", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("size.shadowoffset", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("HitAdd", [TemplateParameter("value", [TypeSpecifier(BUILTIN_INT)], True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("HitBy", [TemplateParameter("value", [TypeSpecifier(BUILTIN_HITTYPE), TypeSpecifier(BUILTIN_HITATTR, False, True)], False), TemplateParameter("value2", [TypeSpecifier(BUILTIN_HITTYPE), TypeSpecifier(BUILTIN_HITATTR, False, True)], False), TemplateParameter("time", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("HitDef", [TemplateParameter("attr", [TypeSpecifier(BUILTIN_HITTYPE), TypeSpecifier(BUILTIN_HITATTR, False, True)], True), TemplateParameter("hitflag", [TypeSpecifier(BUILTIN_HITFLAG)], False), TemplateParameter("guardflag", [TypeSpecifier(BUILTIN_GUARDFLAG)], False), TemplateParameter("affectteam", [TypeSpecifier(BUILTIN_TEAMTYPE)], False), TemplateParameter("animtype", [TypeSpecifier(BUILTIN_HITANIMTYPE)], False), TemplateParameter("air.animtype", [TypeSpecifier(BUILTIN_HITANIMTYPE)], False), TemplateParameter("fall.animtype", [TypeSpecifier(BUILTIN_HITANIMTYPE)], False), TemplateParameter("priority", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_PRIORITYTYPE, False)], False), TemplateParameter("damage", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT, required = False)], False), TemplateParameter("pausetime", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("guard.pausetime", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("sparkno", [TypeSpecifier(BUILTIN_SPRITE)], False), TemplateParameter("guard.sparkno", [TypeSpecifier(BUILTIN_SPRITE)], False), TemplateParameter("sparkxy", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("hitsound", [TypeSpecifier(BUILTIN_SOUND), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("guardsound", [TypeSpecifier(BUILTIN_SOUND), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("ground.type", [TypeSpecifier(BUILTIN_ATTACKTYPE)], False), TemplateParameter("air.type", [TypeSpecifier(BUILTIN_ATTACKTYPE)], False), TemplateParameter("ground.slidetime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("guard.slidetime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("ground.hittime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("guard.hittime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("air.hittime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("guard.ctrltime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("guard.dist", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("yaccel", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("ground.velocity", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("guard.velocity", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("air.velocity", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("airguard.velocity", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("ground.cornerpush.veloff", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("air.cornerpush.veloff", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("down.cornerpush.veloff", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("guard.cornerpush.veloff", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("airguard.cornerpush.veloff", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("airguard.ctrltime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("air.juggle", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("mindist", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("maxdist", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("snap", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("p1sprpriority", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("p2sprpriority", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("p1facing", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("p1getp2facing", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("p2facing", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("p1stateno", [TypeSpecifier(BUILTIN_STATENO)], False), TemplateParameter("p2stateno", [TypeSpecifier(BUILTIN_STATENO)], False), TemplateParameter("p2getp1state", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("forcestand", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("fall", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("fall.xvelocity", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("fall.yvelocity", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("fall.recover", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("fall.recovertime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("fall.damage", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("air.fall", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("forcenofall", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("down.velocity", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("down.hittime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("down.bounce", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("id", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("chainid", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("nochainid", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("hitonce", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("kill", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("guard.kill", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("fall.kill", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("numhits", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("getpower", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT, required = False)], False), TemplateParameter("givepower", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT, required = False)], False), TemplateParameter("palfx.time", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("palfx.mul", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("palfx.add", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("envshake.time", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("envshake.freq", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("envshake.ampl", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("envshake.phase", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("fall.envshake.time", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("fall.envshake.freq", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("fall.envshake.ampl", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("fall.envshake.phase", [TypeSpecifier(BUILTIN_FLOAT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("HitFallDamage", [], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("HitFallSet", [TemplateParameter("value", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("xvel", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("yvel", [TypeSpecifier(BUILTIN_FLOAT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("HitFallVel", [], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("HitOverride", [TemplateParameter("attr", [TypeSpecifier(BUILTIN_HITTYPE), TypeSpecifier(BUILTIN_HITATTR, False, True)], True), TemplateParameter("stateno", [TypeSpecifier(BUILTIN_STATENO)], False), TemplateParameter("slot", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("time", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("forceair", [TypeSpecifier(BUILTIN_BOOL)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("HitVelSet", [TemplateParameter("x", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("y", [TypeSpecifier(BUILTIN_BOOL)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("LifeAdd", [TemplateParameter("value", [TypeSpecifier(BUILTIN_INT)], True), TemplateParameter("kill", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("absolute", [TypeSpecifier(BUILTIN_BOOL)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("LifeSet", [TemplateParameter("value", [TypeSpecifier(BUILTIN_INT)], True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("MakeDust", [TemplateParameter("pos", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("pos2", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("spacing", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("ModifyExplod", [TemplateParameter("id", [TypeSpecifier(BUILTIN_INT)], True), TemplateParameter("int", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("pos", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("postype", [TypeSpecifier(BUILTIN_POSTYPE)], False), TemplateParameter("facing", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("vfacing", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("bindtime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("vel", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("accel", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("random", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("removetime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("supermove", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("supermovetime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("pausemovetime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("scale", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("sprpriority", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("ontop", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("shadow", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("ownpal", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("removeongethit", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("ignorehitpause", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("trans", [TypeSpecifier(BUILTIN_TRANSTYPE)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("MoveHitReset", [], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("NotHitBy", [TemplateParameter("value", [TypeSpecifier(BUILTIN_HITTYPE), TypeSpecifier(BUILTIN_HITATTR, False, True)], False), TemplateParameter("value2", [TypeSpecifier(BUILTIN_HITTYPE), TypeSpecifier(BUILTIN_HITATTR, False, True)], False), TemplateParameter("time", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("Null", [], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("Offset", [TemplateParameter("x", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("y", [TypeSpecifier(BUILTIN_FLOAT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("PalFX", [TemplateParameter("time", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("add", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("mul", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("sinadd", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("invertall", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("color", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("ParentVarAdd", [TemplateParameter("v", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("fv", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("value", [TypeSpecifier(BUILTIN_FLOAT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("ParentVarSet", [TemplateParameter("v", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("fv", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("value", [TypeSpecifier(BUILTIN_FLOAT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("Pause", [TemplateParameter("time", [TypeSpecifier(BUILTIN_INT)], True), TemplateParameter("endcmdbuftime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("movetime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("pausebg", [TypeSpecifier(BUILTIN_BOOL)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("PlayerPush", [TemplateParameter("value", [TypeSpecifier(BUILTIN_BOOL)], True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("PlaySnd", [TemplateParameter("value", [TypeSpecifier(BUILTIN_SOUND), TypeSpecifier(BUILTIN_INT)], True), TemplateParameter("volumescale", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("channel", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("lowpriority", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("freqmul", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("loop", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("pan", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("abspan", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("PosAdd", [TemplateParameter("x", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("y", [TypeSpecifier(BUILTIN_FLOAT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("PosFreeze", [TemplateParameter("value", [TypeSpecifier(BUILTIN_BOOL)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("PosSet", [TemplateParameter("x", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("y", [TypeSpecifier(BUILTIN_FLOAT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("PowerAdd", [TemplateParameter("value", [TypeSpecifier(BUILTIN_INT)], True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("PowerSet", [TemplateParameter("value", [TypeSpecifier(BUILTIN_INT)], True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("Projectile", [TemplateParameter("projid", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("projanim", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("projhitanim", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("projremanim", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("projscale", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("projremove", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("projremovetime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("velocity", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("remvelocity", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("accel", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("velmul", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("projhits", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("projmisstime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("projpriority", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("projsprpriority", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("projedgebound", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("projstagebound", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("projheightbound", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("offset", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("postype", [TypeSpecifier(BUILTIN_POSTYPE)], False), TemplateParameter("projshadow", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("supermovetime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("pausemovetime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("afterimage.time", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("afterimage.length", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("afterimage.palcolor", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("afterimage.palinvertall", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("afterimage.palbright", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("afterimage.palcontrast", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("afterimage.palpostbright", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("afterimage.paladd", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("afterimage.palmul", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("afterimage.timegap", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("afterimage.framegap", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("afterimage.trans", [TypeSpecifier(BUILTIN_TRANSTYPE)], False), TemplateParameter("attr", [TypeSpecifier(BUILTIN_HITTYPE), TypeSpecifier(BUILTIN_HITATTR, False, True)], True), TemplateParameter("hitflag", [TypeSpecifier(BUILTIN_HITFLAG)], False), TemplateParameter("guardflag", [TypeSpecifier(BUILTIN_GUARDFLAG)], False), TemplateParameter("affectteam", [TypeSpecifier(BUILTIN_TEAMTYPE)], False), TemplateParameter("animtype", [TypeSpecifier(BUILTIN_HITANIMTYPE)], False), TemplateParameter("air.animtype", [TypeSpecifier(BUILTIN_HITANIMTYPE)], False), TemplateParameter("fall.animtype", [TypeSpecifier(BUILTIN_HITANIMTYPE)], False), TemplateParameter("priority", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_PRIORITYTYPE, False)], False), TemplateParameter("damage", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT, required = False)], False), TemplateParameter("pausetime", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("guard.pausetime", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("sparkno", [TypeSpecifier(BUILTIN_SPRITE)], False), TemplateParameter("guard.sparkno", [TypeSpecifier(BUILTIN_SPRITE)], False), TemplateParameter("sparkxy", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("hitsound", [TypeSpecifier(BUILTIN_SOUND), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("guardsound", [TypeSpecifier(BUILTIN_SOUND), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("ground.type", [TypeSpecifier(BUILTIN_ATTACKTYPE)], False), TemplateParameter("air.type", [TypeSpecifier(BUILTIN_ATTACKTYPE)], False), TemplateParameter("ground.slidetime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("guard.slidetime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("ground.hittime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("guard.hittime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("air.hittime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("guard.ctrltime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("guard.dist", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("yaccel", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("ground.velocity", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("guard.velocity", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("air.velocity", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("airguard.velocity", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("ground.cornerpush.veloff", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("air.cornerpush.veloff", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("down.cornerpush.veloff", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("guard.cornerpush.veloff", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("airguard.cornerpush.veloff", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("airguard.ctrltime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("air.juggle", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("mindist", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("maxdist", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("snap", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("p1sprpriority", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("p2sprpriority", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("p1facing", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("p1getp2facing", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("p2facing", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("p1stateno", [TypeSpecifier(BUILTIN_STATENO)], False), TemplateParameter("p2stateno", [TypeSpecifier(BUILTIN_STATENO)], False), TemplateParameter("p2getp1state", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("forcestand", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("fall", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("fall.xvelocity", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("fall.yvelocity", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("fall.recover", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("fall.recovertime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("fall.damage", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("air.fall", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("forcenofall", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("down.velocity", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("down.hittime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("down.bounce", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("id", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("chainid", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("nochainid", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("hitonce", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("kill", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("guard.kill", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("fall.kill", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("numhits", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("getpower", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT, required = False)], False), TemplateParameter("givepower", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT, required = False)], False), TemplateParameter("palfx.time", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("palfx.mul", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("palfx.add", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("envshake.time", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("envshake.freq", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("envshake.ampl", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("envshake.phase", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("fall.envshake.time", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("fall.envshake.freq", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("fall.envshake.ampl", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("fall.envshake.phase", [TypeSpecifier(BUILTIN_FLOAT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("RemapPal", [TemplateParameter("source", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], True), TemplateParameter("dest", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("RemoveExplod", [TemplateParameter("id", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("ReversalDef", [TemplateParameter("reversal.attr", [TypeSpecifier(BUILTIN_HITTYPE), TypeSpecifier(BUILTIN_HITATTR, False, True)], True), TemplateParameter("pausetime", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("sparkno", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("hitsound", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("p1stateno", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("p2stateno", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("p1sprpriority", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("p2sprpriority", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("sparkxy", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("ScreenBound", [TemplateParameter("value", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("movecamera", [TypeSpecifier(BUILTIN_BOOL), TypeSpecifier(BUILTIN_BOOL)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("SelfState", [TemplateParameter("value", [TypeSpecifier(BUILTIN_STATENO)], True), TemplateParameter("ctrl", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("anim", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("SprPriority", [TemplateParameter("value", [TypeSpecifier(BUILTIN_INT)], True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("StateTypeSet", [TemplateParameter("statetype", [TypeSpecifier(BUILTIN_STATETYPE)], False), TemplateParameter("movetype", [TypeSpecifier(BUILTIN_MOVETYPE)], False), TemplateParameter("physics", [TypeSpecifier(BUILTIN_PHYSICSTYPE)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("SndPan", [TemplateParameter("channel", [TypeSpecifier(BUILTIN_INT)], True), TemplateParameter("pan", [TypeSpecifier(BUILTIN_INT)], True), TemplateParameter("abspan", [TypeSpecifier(BUILTIN_INT)], True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("StopSnd", [TemplateParameter("channel", [TypeSpecifier(BUILTIN_INT)], True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("SuperPause", [TemplateParameter("time", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("anim", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("sound", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("pos", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("darken", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("p2defmul", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("poweradd", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("unhittable", [TypeSpecifier(BUILTIN_BOOL)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("TargetBind", [TemplateParameter("time", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("id", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("pos", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("TargetDrop", [TemplateParameter("excludeid", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("keepone", [TypeSpecifier(BUILTIN_BOOL)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("TargetFacing", [TemplateParameter("value", [TypeSpecifier(BUILTIN_INT)], True), TemplateParameter("id", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("TargetLifeAdd", [TemplateParameter("value", [TypeSpecifier(BUILTIN_INT)], True), TemplateParameter("id", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("kill", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("absolute", [TypeSpecifier(BUILTIN_BOOL)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("TargetPowerAdd", [TemplateParameter("value", [TypeSpecifier(BUILTIN_INT)], True), TemplateParameter("id", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("TargetState", [TemplateParameter("value", [TypeSpecifier(BUILTIN_STATENO)], True), TemplateParameter("id", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("TargetVelAdd", [TemplateParameter("x", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("y", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("id", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("TargetVelSet", [TemplateParameter("x", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("y", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("id", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("Trans", [TemplateParameter("trans", [TypeSpecifier(BUILTIN_TRANSTYPE)], True), TemplateParameter("alpha", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("Turn", [], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("VarAdd", [TemplateParameter("v", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("fv", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("value", [TypeSpecifier(BUILTIN_FLOAT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("VarSet", [TemplateParameter("v", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("fv", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("value", [TypeSpecifier(BUILTIN_FLOAT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("VarRandom", [TemplateParameter("v", [TypeSpecifier(BUILTIN_INT)], True), TemplateParameter("range", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("VarRangeSet", [TemplateParameter("value", [TypeSpecifier(BUILTIN_INT)], True), TemplateParameter("fvalue", [TypeSpecifier(BUILTIN_FLOAT)], True), TemplateParameter("first", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("last", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("VelAdd", [TemplateParameter("x", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("y", [TypeSpecifier(BUILTIN_FLOAT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("VelMul", [TemplateParameter("x", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("y", [TypeSpecifier(BUILTIN_FLOAT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("VelSet", [TemplateParameter("x", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("y", [TypeSpecifier(BUILTIN_FLOAT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("VictoryQuote", [TemplateParameter("value", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("Width", [TemplateParameter("edge", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("player", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("value", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN)
    ]