from mtl.types.context import TranslationContext
from mtl.types.translation import *
from mtl.types.shared import TranslationError
from mtl.types.builtins import *
from mtl.utils.compiler import find_type, get_widest_match, compiler_internal

def getBaseTypes() -> list[TypeDefinition]:
    return [
        BUILTIN_ANY,
        BUILTIN_INT,
        BUILTIN_FLOAT,
        BUILTIN_SHORT,
        BUILTIN_BYTE,
        BUILTIN_CHAR,
        BUILTIN_BOOL,
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
        BUILTIN_WAVETYPE,
        BUILTIN_HELPERTYPE,
        BUILTIN_HITFLAG,
        BUILTIN_GUARDFLAG,
        BUILTIN_TEAMTYPE,
        BUILTIN_HITANIMTYPE,
        BUILTIN_ATTACKTYPE,
        BUILTIN_PRIORITYTYPE,
        BUILTIN_HITVARTYPE,
        BUILTIN_CONSTTYPE,
        ## built-in union types
        BUILTIN_NUMERIC,
        BUILTIN_PREFINT,
        BUILTIN_SPRITE,
        BUILTIN_SOUND,
        BUILTIN_ANIM
    ]

def getBaseTriggers() -> list[TriggerDefinition]:
    return [
        ## MUGEN trigger functions
        TriggerDefinition("abs", BUILTIN_NUMERIC, None, [TypeParameter("exprn", BUILTIN_NUMERIC)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("acos", BUILTIN_FLOAT, None, [TypeParameter("exprn", BUILTIN_NUMERIC)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("AiLevel", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Alive", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Anim", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("AnimElem", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("AnimElemNo", BUILTIN_INT, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("AnimElemTime", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("AnimElemTime", BUILTIN_INT, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("AnimExist", BUILTIN_BOOL, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("AnimExist", BUILTIN_BOOL, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("AnimTime", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("asin", BUILTIN_FLOAT, None, [TypeParameter("exprn", BUILTIN_NUMERIC)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("atan", BUILTIN_FLOAT, None, [TypeParameter("exprn", BUILTIN_NUMERIC)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("AuthorName", BUILTIN_STRING, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("BackEdgeBodyDist", BUILTIN_FLOAT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("BackEdgeDist", BUILTIN_FLOAT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("CanRecover", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("ceil", BUILTIN_INT, None, [TypeParameter("exprn", BUILTIN_NUMERIC)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Command", BUILTIN_STRING, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("cond", BUILTIN_ANY, builtin_cond, [TypeParameter("condition", BUILTIN_BOOL), TypeParameter("exprn1", BUILTIN_ANY), TypeParameter("exprn2", BUILTIN_ANY)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Const", BUILTIN_NUMERIC, None, [TypeParameter("param_name", BUILTIN_CONSTTYPE)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Const240p", BUILTIN_FLOAT, None, [TypeParameter("exprn", BUILTIN_NUMERIC)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Const480p", BUILTIN_FLOAT, None, [TypeParameter("exprn", BUILTIN_NUMERIC)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Const720p", BUILTIN_FLOAT, None, [TypeParameter("exprn", BUILTIN_NUMERIC)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("cos", BUILTIN_FLOAT, None, [TypeParameter("exprn", BUILTIN_NUMERIC)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Ctrl", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("DrawGame", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("e", BUILTIN_FLOAT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("exp", BUILTIN_FLOAT, None, [TypeParameter("exprn", BUILTIN_NUMERIC)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Facing", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("floor", BUILTIN_INT, None, [TypeParameter("exprn", BUILTIN_FLOAT)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("FrontEdgeBodyDist", BUILTIN_FLOAT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("FrontEdgeDist", BUILTIN_FLOAT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("fvar", BUILTIN_FLOAT, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("GameHeight", BUILTIN_FLOAT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("GameTime", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("GameWidth", BUILTIN_FLOAT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("GetHitVar", BUILTIN_FLOAT, None, [TypeParameter("param_name", BUILTIN_HITVARTYPE)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("HitCount", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("HitFall", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("HitOver", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("HitPauseTime", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("HitShakeOver", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("HitVel", BUILTIN_VECTOR, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("ID", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("ifelse", BUILTIN_ANY, builtin_cond, [TypeParameter("condition", BUILTIN_BOOL), TypeParameter("exprn1", BUILTIN_ANY), TypeParameter("exprn2", BUILTIN_ANY)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("InGuardDist", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("IsHelper", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("IsHelper", BUILTIN_BOOL, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("IsHomeTeam", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Life", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("LifeMax", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("ln", BUILTIN_FLOAT, None, [TypeParameter("exprn", BUILTIN_NUMERIC)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("log", BUILTIN_FLOAT, None, [TypeParameter("exp1", BUILTIN_NUMERIC)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Lose", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("LoseKO", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("LoseTime", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("MatchNo", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("MatchOver", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("MoveContact", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("MoveGuarded", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("MoveHit", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("MoveReversed", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Name", BUILTIN_STRING, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("NumEnemy", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("NumExplod", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("NumExplod", BUILTIN_INT, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("NumPartner", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("NumProj", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("NumProjID", BUILTIN_INT, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("NumTarget", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("NumTarget", BUILTIN_INT, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("P1Name", BUILTIN_STRING, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("P2BodyDist", BUILTIN_VECTOR, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("P2Dist", BUILTIN_VECTOR, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("P2Life", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("P2Name", BUILTIN_STRING, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("P2StateNo", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("P3Name", BUILTIN_STRING, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("P4Name", BUILTIN_STRING, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("PalNo", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("ParentDist", BUILTIN_VECTOR, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("pi", BUILTIN_FLOAT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Pos", BUILTIN_VECTOR, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Power", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("PowerMax", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("PlayerIDExist", BUILTIN_BOOL, None, [TypeParameter("ID_number", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("PrevStateNo", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("ProjCancelTime", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("ProjCancelTime", BUILTIN_INT, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("ProjContactTime", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("ProjContactTime", BUILTIN_INT, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("ProjGuardedTime", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("ProjGuardedTime", BUILTIN_INT, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("ProjHitTime", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("ProjHitTime", BUILTIN_INT, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Random", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("RootDist", BUILTIN_VECTOR, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("RoundNo", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("RoundsExisted", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("RoundState", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("ScreenPos", BUILTIN_VECTOR, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("SelfAnimExist", BUILTIN_BOOL, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("SelfAnimExist", BUILTIN_BOOL, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("sin", BUILTIN_FLOAT, None, [TypeParameter("exprn", BUILTIN_NUMERIC)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("StateNo", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        #TriggerDefinition("StageVar", BUILTIN_STRING, None, [TypeParameter("param_name", "StageVarType")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("sysfvar", BUILTIN_FLOAT, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("sysvar", BUILTIN_INT, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("tan", BUILTIN_FLOAT, None, [TypeParameter("exprn", BUILTIN_NUMERIC)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("TeamSide", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("TicksPerSecond", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Time", BUILTIN_INT, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("var", BUILTIN_INT, None, [TypeParameter("exprn", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Vel", BUILTIN_VECTOR, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Win", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("WinKO", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("WinTime", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("WinPerfect", BUILTIN_BOOL, None, [], None, Location("mtl/builtins.py", line_number())),

        ## builtin operator functions
        TriggerDefinition("operator!", BUILTIN_BOOL, builtin_not, [TypeParameter("expr", BUILTIN_BOOL)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator!", BUILTIN_BOOL, builtin_not, [TypeParameter("expr", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator!", BUILTIN_BOOL, builtin_not, [TypeParameter("expr", BUILTIN_FLOAT)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),

        TriggerDefinition("operator-", BUILTIN_INT, builtin_negate, [TypeParameter("expr", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator-", BUILTIN_FLOAT, builtin_negate, [TypeParameter("expr", BUILTIN_FLOAT)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),

        TriggerDefinition("operator~", BUILTIN_INT, builtin_bitnot, [TypeParameter("expr", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),

        TriggerDefinition("operator+", BUILTIN_INT, builtin_add, [TypeParameter("expr1", BUILTIN_INT), TypeParameter("expr2", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator+", BUILTIN_FLOAT, builtin_add, [TypeParameter("expr1", BUILTIN_FLOAT), TypeParameter("expr2", BUILTIN_FLOAT)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator-", BUILTIN_INT, builtin_sub, [TypeParameter("expr1", BUILTIN_INT), TypeParameter("expr2", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator-", BUILTIN_FLOAT, builtin_sub, [TypeParameter("expr1", BUILTIN_FLOAT), TypeParameter("expr2", BUILTIN_FLOAT)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator*", BUILTIN_INT, builtin_mult, [TypeParameter("expr1", BUILTIN_INT), TypeParameter("expr2", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator*", BUILTIN_FLOAT, builtin_mult, [TypeParameter("expr1", BUILTIN_FLOAT), TypeParameter("expr2", BUILTIN_FLOAT)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator/", BUILTIN_INT, builtin_div, [TypeParameter("expr1", BUILTIN_INT), TypeParameter("expr2", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator/", BUILTIN_FLOAT, builtin_div, [TypeParameter("expr1", BUILTIN_FLOAT), TypeParameter("expr2", BUILTIN_FLOAT)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator%", BUILTIN_INT, builtin_div, [TypeParameter("expr1", BUILTIN_INT), TypeParameter("expr2", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator**", BUILTIN_INT, builtin_exp, [TypeParameter("expr1", BUILTIN_INT), TypeParameter("expr2", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator**", BUILTIN_FLOAT, builtin_exp, [TypeParameter("expr1", BUILTIN_FLOAT), TypeParameter("expr2", BUILTIN_FLOAT)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),

        TriggerDefinition("operator=", BUILTIN_BOOL, builtin_eq, [TypeParameter("expr1", BUILTIN_INT), TypeParameter("expr2", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator=", BUILTIN_BOOL, builtin_eq, [TypeParameter("expr1", BUILTIN_FLOAT), TypeParameter("expr2", BUILTIN_FLOAT)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator=", BUILTIN_BOOL, builtin_eq, [TypeParameter("expr1", BUILTIN_STRING), TypeParameter("expr2", BUILTIN_STRING)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator!=", BUILTIN_BOOL, builtin_neq, [TypeParameter("expr1", BUILTIN_INT), TypeParameter("expr2", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator!=", BUILTIN_BOOL, builtin_neq, [TypeParameter("expr1", BUILTIN_FLOAT), TypeParameter("expr2", BUILTIN_FLOAT)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator!=", BUILTIN_BOOL, builtin_neq, [TypeParameter("expr1", BUILTIN_STRING), TypeParameter("expr2", BUILTIN_STRING)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),

        TriggerDefinition("operator&", BUILTIN_INT, builtin_bitand, [TypeParameter("expr1", BUILTIN_INT), TypeParameter("expr2", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator|", BUILTIN_INT, builtin_bitor, [TypeParameter("expr1", BUILTIN_INT), TypeParameter("expr2", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator^", BUILTIN_INT, builtin_bitxor, [TypeParameter("expr1", BUILTIN_INT), TypeParameter("expr2", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),

        TriggerDefinition("operator:=", BUILTIN_INT, builtin_assign, [TypeParameter("expr1", BUILTIN_INT), TypeParameter("expr2", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator:=", BUILTIN_INT, builtin_assign, [TypeParameter("expr1", BUILTIN_FLOAT), TypeParameter("expr2", BUILTIN_FLOAT)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),

        TriggerDefinition("operator<", BUILTIN_BOOL, builtin_lt, [TypeParameter("expr1", BUILTIN_INT), TypeParameter("expr2", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator<=", BUILTIN_BOOL, builtin_lte, [TypeParameter("expr1", BUILTIN_INT), TypeParameter("expr2", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator>", BUILTIN_BOOL, builtin_gt, [TypeParameter("expr1", BUILTIN_INT), TypeParameter("expr2", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator>=", BUILTIN_BOOL, builtin_gte, [TypeParameter("expr1", BUILTIN_INT), TypeParameter("expr2", BUILTIN_INT)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),

        TriggerDefinition("operator<", BUILTIN_BOOL, builtin_lt, [TypeParameter("expr1", BUILTIN_FLOAT), TypeParameter("expr2", BUILTIN_FLOAT)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator<=", BUILTIN_BOOL, builtin_lte, [TypeParameter("expr1", BUILTIN_FLOAT), TypeParameter("expr2", BUILTIN_FLOAT)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator>", BUILTIN_BOOL, builtin_gt, [TypeParameter("expr1", BUILTIN_FLOAT), TypeParameter("expr2", BUILTIN_FLOAT)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator>=", BUILTIN_BOOL, builtin_gte, [TypeParameter("expr1", BUILTIN_FLOAT), TypeParameter("expr2", BUILTIN_FLOAT)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),

        TriggerDefinition("operator&&", BUILTIN_BOOL, builtin_and, [TypeParameter("expr1", BUILTIN_BOOL), TypeParameter("expr2", BUILTIN_BOOL)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator||", BUILTIN_BOOL, builtin_or, [TypeParameter("expr1", BUILTIN_BOOL), TypeParameter("expr2", BUILTIN_BOOL)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator^^", BUILTIN_BOOL, builtin_xor, [TypeParameter("expr1", BUILTIN_BOOL), TypeParameter("expr2", BUILTIN_BOOL)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),

        ## builtin constant/compiler functions
        TriggerDefinition("cast", BUILTIN_ANY, builtin_cast, [TypeParameter("expr", BUILTIN_ANY), TypeParameter("t", BUILTIN_TYPE)], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
    ]

def builtin_cond(exprs: list[Expression], ctx: TranslationContext) -> Expression:
    if exprs[1].type != exprs[2].type:
        raise TranslationError(f"Conditional expression (cond and ifelse) must provide 2 expressions of the same type.", Location("mtl/builtins.py", line_number()))
    return Expression(exprs[1].type, f"cond({exprs[0].value}, {exprs[1].value}, {exprs[2].value})")

def builtin_cast(exprs: list[Expression], ctx: TranslationContext) -> Expression:
    if exprs[1].type != BUILTIN_TYPE or (target_type := find_type(exprs[1].value, ctx)) == None:
        raise TranslationError(f"Second argument to cast must be a type name, not {exprs[1].value}", Location("mtl/builtins.py", line_number()))
    return Expression(target_type, exprs[0].value)

def builtin_not(exprs: list[Expression], ctx: TranslationContext) -> Expression:
    return Expression(BUILTIN_BOOL, f"(!{exprs[0].value})")

def builtin_negate(exprs: list[Expression], ctx: TranslationContext) -> Expression:
    return Expression(exprs[0].type, f"(-{exprs[0].value})")

def builtin_bitnot(exprs: list[Expression], ctx: TranslationContext) -> Expression:
    return Expression(exprs[0].type, f"(~{exprs[0].value})")

def builtin_binary(exprs: list[Expression], ctx: TranslationContext, op: str) -> Expression:
    if (result := get_widest_match(exprs[0].type, exprs[1].type, ctx, compiler_internal())) != None:
        return Expression(result, f"({exprs[0].value} {op} {exprs[1].value})")
    raise TranslationError(f"Failed to convert an expression of type {exprs[0].type.name} to type {exprs[1].type.name} for operator {op}.", Location("mtl/builtins.py", line_number()))

def builtin_add(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "+")
def builtin_sub(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "-")
def builtin_mult(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "*")
def builtin_div(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "/")
def builtin_mod(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "%")
def builtin_exp(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "**")
def builtin_xor(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "^^")
def builtin_eq(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "=")
def builtin_neq(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "!=")
def builtin_bitand(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "&")
def builtin_bitor(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "|")
def builtin_bitxor(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "^")
def builtin_assign(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, ":=")
def builtin_lt(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "<")
def builtin_lte(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "<=")
def builtin_gt(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, ">")
def builtin_gte(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, ">=")

# special cases. these accept variable inputs to support trigger collapsing.
## TODO: support variable inputs properly...
def builtin_and(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "&&")
def builtin_or(exprs: list[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "||")

def getBaseTemplates() -> list[TemplateDefinition]:
    return [
         TemplateDefinition("AfterImage", [TemplateParameter("time", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("length", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("palcolor", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("palinvertall", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("palbright", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("palcontrast", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("palpostbright", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("paladd", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("palmul", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("timegap", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("framegap", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("trans", [TypeSpecifier(BUILTIN_TRANSTYPE)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("AfterImageTime", [TemplateParameter("time", [TypeSpecifier(BUILTIN_INT)], True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("AngleAdd", [TemplateParameter("value", [TypeSpecifier(BUILTIN_FLOAT)], True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("AngleDraw", [TemplateParameter("value", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("scale", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("AngleMul", [TemplateParameter("value", [TypeSpecifier(BUILTIN_FLOAT)], True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("AngleSet", [TemplateParameter("value", [TypeSpecifier(BUILTIN_FLOAT)], True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("AssertSpecial", [TemplateParameter("flag", [TypeSpecifier(BUILTIN_ASSERTTYPE)], True), TemplateParameter("flag2", [TypeSpecifier(BUILTIN_ASSERTTYPE)], False), TemplateParameter("flag3", [TypeSpecifier(BUILTIN_ASSERTTYPE)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("AttackDist", [TemplateParameter("value", [TypeSpecifier(BUILTIN_INT)], True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("AttackMulSet", [TemplateParameter("value", [TypeSpecifier(BUILTIN_FLOAT)], True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("BindToParent", [TemplateParameter("time", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("facing", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("pos", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("BindToRoot", [TemplateParameter("time", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("facing", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("pos", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("BindToTarget", [TemplateParameter("time", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("id", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("pos", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_BINDTYPE)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("ChangeAnim", [TemplateParameter("value", [TypeSpecifier(BUILTIN_INT)], True), TemplateParameter("elem", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("ChangeAnim2", [TemplateParameter("value", [TypeSpecifier(BUILTIN_INT)], True), TemplateParameter("elem", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("ChangeState", [TemplateParameter("value", [TypeSpecifier(BUILTIN_INT)], True), TemplateParameter("ctrl", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("anim", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("ClearClipboard", [], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("CtrlSet", [TemplateParameter("ctrl", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("value", [TypeSpecifier(BUILTIN_BOOL)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("DefenceMulSet", [TemplateParameter("value", [TypeSpecifier(BUILTIN_FLOAT)], True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("DestroySelf", [], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("DisplayToClipboard", [TemplateParameter("text", [TypeSpecifier(BUILTIN_STRING)], True), TemplateParameter("params", [TypeSpecifier(BUILTIN_VECTOR)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("EnvColor", [TemplateParameter("value", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("time", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("under", [TypeSpecifier(BUILTIN_BOOL)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("EnvShake", [TemplateParameter("time", [TypeSpecifier(BUILTIN_INT)], True), TemplateParameter("freq", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("ampl", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("phase", [TypeSpecifier(BUILTIN_FLOAT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("Explod", [TemplateParameter("anim", [TypeSpecifier(BUILTIN_ANIM)], True), TemplateParameter("id", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("pos", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("postype", [TypeSpecifier(BUILTIN_POSTYPE)], False), TemplateParameter("facing", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("vfacing", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("bindtime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("vel", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("accel", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("random", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("removetime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("supermove", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("supermovetime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("pausemovetime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("scale", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("sprpriority", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("ontop", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("shadow", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("ownpal", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("removeongethit", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("ignorehitpause", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("trans", [TypeSpecifier(BUILTIN_TRANSTYPE)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("ExplodBindTime", [TemplateParameter("id", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("time", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("ForceFeedback", [TemplateParameter("waveform", [TypeSpecifier(BUILTIN_WAVETYPE)], False), TemplateParameter("time", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("freq", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("ampl", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("self", [TypeSpecifier(BUILTIN_BOOL)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("FallEnvShake", [], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("GameMakeint", [TemplateParameter("value", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("under", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("pos", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("random", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("Gravity", [], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("Helper", [TemplateParameter("helpertype", [TypeSpecifier(BUILTIN_HELPERTYPE)], False), TemplateParameter("name", [TypeSpecifier(BUILTIN_STRING)], False), TemplateParameter("id", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("pos", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("postype", [TypeSpecifier(BUILTIN_POSTYPE)], False), TemplateParameter("facing", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("stateno", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("keyctrl", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("ownpal", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("supermovetime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("pausemovetime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("size.xscale", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("size.yscale", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("size.ground.back", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("size.ground.front", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("size.air.back", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("size.ait.front", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("size.height", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("size.proj.doscale", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("size.head.pos", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("size.mid.pos", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("size.shadowoffset", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("HitAdd", [TemplateParameter("value", [TypeSpecifier(BUILTIN_INT)], True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("HitBy", [TemplateParameter("value", [TypeSpecifier(BUILTIN_HITTYPE), TypeSpecifier(BUILTIN_HITATTR, False, True)], False), TemplateParameter("value2", [TypeSpecifier(BUILTIN_HITTYPE), TypeSpecifier(BUILTIN_HITATTR, False, True)], False), TemplateParameter("time", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("HitDef", [TemplateParameter("attr", [TypeSpecifier(BUILTIN_HITTYPE), TypeSpecifier(BUILTIN_HITATTR, False, True)], True), TemplateParameter("hitflag", [TypeSpecifier(BUILTIN_HITFLAG)], False), TemplateParameter("guardflag", [TypeSpecifier(BUILTIN_GUARDFLAG)], False), TemplateParameter("affectteam", [TypeSpecifier(BUILTIN_TEAMTYPE)], False), TemplateParameter("animtype", [TypeSpecifier(BUILTIN_HITANIMTYPE)], False), TemplateParameter("air.animtype", [TypeSpecifier(BUILTIN_HITANIMTYPE)], False), TemplateParameter("fall.animtype", [TypeSpecifier(BUILTIN_HITANIMTYPE)], False), TemplateParameter("priority", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_PRIORITYTYPE, False)], False), TemplateParameter("damage", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT, required = False)], False), TemplateParameter("pausetime", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("guard.pausetime", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("sparkno", [TypeSpecifier(BUILTIN_SPRITE)], False), TemplateParameter("guard.sparkno", [TypeSpecifier(BUILTIN_SPRITE)], False), TemplateParameter("sparkxy", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("hitsound", [TypeSpecifier(BUILTIN_SOUND), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("guardsound", [TypeSpecifier(BUILTIN_SOUND), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("ground.type", [TypeSpecifier(BUILTIN_ATTACKTYPE)], False), TemplateParameter("air.type", [TypeSpecifier(BUILTIN_ATTACKTYPE)], False), TemplateParameter("ground.slidetime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("guard.slidetime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("ground.hittime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("guard.hittime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("air.hittime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("guard.ctrltime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("guard.dist", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("yaccel", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("ground.velocity", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("guard.velocity", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("air.velocity", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("airguard.velocity", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("ground.cornerpush.veloff", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("air.cornerpush.veloff", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("down.cornerpush.veloff", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("guard.cornerpush.veloff", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("airguard.cornerpush.veloff", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("airguard.ctrltime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("air.juggle", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("mindist", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("maxdist", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("snap", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("p1sprpriority", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("p2sprpriority", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("p1facing", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("p1getp2facing", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("p2facing", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("p1stateno", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("p2stateno", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("p2getp1state", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("forcestand", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("fall", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("fall.xvelocity", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("fall.yvelocity", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("fall.recover", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("fall.recovertime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("fall.damage", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("air.fall", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("forcenofall", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("down.velocity", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("down.hittime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("down.bounce", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("id", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("chainid", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("nochainid", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("hitonce", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("kill", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("guard.kill", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("fall.kill", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("numhits", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("getpower", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT, required = False)], False), TemplateParameter("givepower", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT, required = False)], False), TemplateParameter("palfx.time", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("palfx.mul", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("palfx.add", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("envshake.time", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("envshake.freq", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("envshake.ampl", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("envshake.phase", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("fall.envshake.time", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("fall.envshake.freq", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("fall.envshake.ampl", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("fall.envshake.phase", [TypeSpecifier(BUILTIN_FLOAT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("HitFallDamage", [], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("HitFallSet", [TemplateParameter("value", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("xvel", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("yvel", [TypeSpecifier(BUILTIN_FLOAT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("HitFallVel", [], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("HitOverride", [TemplateParameter("attr", [TypeSpecifier(BUILTIN_HITTYPE), TypeSpecifier(BUILTIN_HITATTR, False, True)], True), TemplateParameter("stateno", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("slot", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("time", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("forceair", [TypeSpecifier(BUILTIN_BOOL)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
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
        TemplateDefinition("ParentVarAdd", [TemplateParameter("v", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("fv", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("value", [TypeSpecifier(BUILTIN_NUMERIC)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("ParentVarSet", [TemplateParameter("v", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("fv", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("value", [TypeSpecifier(BUILTIN_NUMERIC)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("Pause", [TemplateParameter("time", [TypeSpecifier(BUILTIN_INT)], True), TemplateParameter("endcmdbuftime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("movetime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("pausebg", [TypeSpecifier(BUILTIN_BOOL)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("PlayerPush", [TemplateParameter("value", [TypeSpecifier(BUILTIN_BOOL)], True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("PlaySnd", [TemplateParameter("value", [TypeSpecifier(BUILTIN_SOUND), TypeSpecifier(BUILTIN_INT)], True), TemplateParameter("volumescale", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("channel", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("lowpriority", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("freqmul", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("loop", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("pan", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("abspan", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("PosAdd", [TemplateParameter("x", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("y", [TypeSpecifier(BUILTIN_FLOAT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("PosFreeze", [TemplateParameter("value", [TypeSpecifier(BUILTIN_BOOL)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("PosSet", [TemplateParameter("x", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("y", [TypeSpecifier(BUILTIN_FLOAT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("PowerAdd", [TemplateParameter("value", [TypeSpecifier(BUILTIN_INT)], True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("PowerSet", [TemplateParameter("value", [TypeSpecifier(BUILTIN_INT)], True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("Projectile", [TemplateParameter("projid", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("projint", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("projhitint", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("projremint", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("projscale", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("projremove", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("projremovetime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("velocity", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("remvelocity", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("accel", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("velmul", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("projhits", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("projmisstime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("projpriority", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("projsprpriority", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("projedgebound", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("projstagebound", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("projheightbound", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("offset", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("postype", [TypeSpecifier(BUILTIN_POSTYPE)], False), TemplateParameter("projshadow", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("supermovetime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("pausemovetime", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("afterimage.time", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("afterimage.length", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("afterimage.palcolor", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("afterimage.palinvertall", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("afterimage.palbright", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("afterimage.palcontrast", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("afterimage.palpostbright", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("afterimage.paladd", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("afterimage.palmul", [TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT), TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("afterimage.timegap", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("afterimage.framegap", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("afterimage.trans", [TypeSpecifier(BUILTIN_TRANSTYPE)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("RemapPal", [TemplateParameter("source", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], True), TemplateParameter("dest", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("RemoveExplod", [TemplateParameter("id", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("ReversalDef", [TemplateParameter("reversal.attr", [TypeSpecifier(BUILTIN_HITTYPE), TypeSpecifier(BUILTIN_HITATTR, False, True)], True), TemplateParameter("pausetime", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("sparkno", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("hitsound", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("p1stateno", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("p2stateno", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("p1sprpriority", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("p2sprpriority", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("sparkxy", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("ScreenBound", [TemplateParameter("value", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("movecamera", [TypeSpecifier(BUILTIN_BOOL), TypeSpecifier(BUILTIN_BOOL)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("SelfState", [TemplateParameter("value", [TypeSpecifier(BUILTIN_INT)], True), TemplateParameter("ctrl", [TypeSpecifier(BUILTIN_BOOL)], False), TemplateParameter("anim", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
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
        TemplateDefinition("TargetState", [TemplateParameter("value", [TypeSpecifier(BUILTIN_INT)], True), TemplateParameter("id", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("TargetVelAdd", [TemplateParameter("x", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("y", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("id", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("TargetVelSet", [TemplateParameter("x", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("y", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("id", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("Trans", [TemplateParameter("trans", [TypeSpecifier(BUILTIN_TRANSTYPE)], True), TemplateParameter("alpha", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("Turn", [], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("VarAdd", [TemplateParameter("v", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("fv", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("value", [TypeSpecifier(BUILTIN_NUMERIC)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("VarSet", [TemplateParameter("v", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("fv", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("value", [TypeSpecifier(BUILTIN_NUMERIC)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("VarRandom", [TemplateParameter("v", [TypeSpecifier(BUILTIN_INT)], True), TemplateParameter("range", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("VarRangeSet", [TemplateParameter("value", [TypeSpecifier(BUILTIN_INT)], True), TemplateParameter("fvalue", [TypeSpecifier(BUILTIN_FLOAT)], True), TemplateParameter("first", [TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("last", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("VelAdd", [TemplateParameter("x", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("y", [TypeSpecifier(BUILTIN_FLOAT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("VelMul", [TemplateParameter("x", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("y", [TypeSpecifier(BUILTIN_FLOAT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("VelSet", [TemplateParameter("x", [TypeSpecifier(BUILTIN_FLOAT)], False), TemplateParameter("y", [TypeSpecifier(BUILTIN_FLOAT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("VictoryQuote", [TemplateParameter("value", [TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("Width", [TemplateParameter("edge", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("player", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False), TemplateParameter("value", [TypeSpecifier(BUILTIN_INT), TypeSpecifier(BUILTIN_INT)], False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN)
    ]