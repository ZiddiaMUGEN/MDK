from typing import List
from inspect import currentframe

from mtl.utils import find, typeConvertWidest
from mtl.shared import TranslationContext, TypeDefinition, TypeCategory, TriggerDefinition, TriggerParameter, TriggerCategory, Expression, TemplateDefinition, TemplateCategory, TemplateParameter, Location
from mtl.error import TranslationError

def line_number() -> int:
    cf = currentframe()
    if cf != None and cf.f_back != None:
        return cf.f_back.f_lineno
    else:
        return 0

def getBaseTypes() -> List[TypeDefinition]:
    return [
        TypeDefinition("int", TypeCategory.BUILTIN, 32, [], Location("mtl/builtins.py", line_number())),
        TypeDefinition("float", TypeCategory.BUILTIN, 32, [], Location("mtl/builtins.py", line_number())),
        TypeDefinition("short", TypeCategory.BUILTIN, 16, [], Location("mtl/builtins.py", line_number())),
        TypeDefinition("byte", TypeCategory.BUILTIN, 8, [], Location("mtl/builtins.py", line_number())),
        TypeDefinition("char", TypeCategory.BUILTIN, 8, [], Location("mtl/builtins.py", line_number())),
        TypeDefinition("bool", TypeCategory.BUILTIN, 1, [], Location("mtl/builtins.py", line_number())),
        ## this is a special int type which can support character prefixes. it's used for things like sounds and anims.
        ## it's not legal to create a variable with this type.
        TypeDefinition("cint", TypeCategory.BUILTIN_DENY, 32, [], Location("mtl/builtins.py", line_number())),
        TypeDefinition("StateType", TypeCategory.STRING_ENUM, 32, ["S", "C", "A", "L", "U"], Location("mtl/builtins.py", line_number())),
        TypeDefinition("MoveType", TypeCategory.STRING_ENUM, 32, ["A", "I", "H", "U"], Location("mtl/builtins.py", line_number())),
        TypeDefinition("PhysicsType", TypeCategory.STRING_ENUM, 32, ["S", "C", "A", "N", "U"], Location("mtl/builtins.py", line_number())),
        TypeDefinition("HitType", TypeCategory.STRING_FLAG, 32, ["S", "C", "A"], Location("mtl/builtins.py", line_number())),
        TypeDefinition("HitAttr", TypeCategory.STRING_FLAG, 32, ["N", "S", "H", "A", "T"], Location("mtl/builtins.py", line_number())),
        TypeDefinition("TransType", TypeCategory.STRING_ENUM, 32, ["add", "add1", "sub", "none"], Location("mtl/builtins.py", line_number())),
        TypeDefinition("AssertType", TypeCategory.STRING_ENUM, 32, ["Intro", "Invisible", "RoundNotOver", "NoBarDisplay", "NoBG", "NoFG", "NoStandGuard", "NoCrouchGuard", "NoAirGuard", "NoAutoTurn", "NoJuggleCheck", "NoKOSnd", "NoKOSlow", "NoKO", "NoShadow", "GlobalNoShadow", "NoMusic", "NoWalk", "TimerFreeze", "Unguardable"], Location("mtl/builtins.py", line_number())),
        TypeDefinition("BindType", TypeCategory.STRING_ENUM, 32, ["Foot", "Mid", "Head"], Location("mtl/builtins.py", line_number())),
        TypeDefinition("PosType", TypeCategory.STRING_ENUM, 32, ["P1", "P2", "Front", "Back", "Left", "Right", "None"], Location("mtl/builtins.py", line_number())),
        TypeDefinition("WaveType", TypeCategory.STRING_ENUM, 32, ["Sine", "Square", "SineSquare", "Off"], Location("mtl/builtins.py", line_number())),
        TypeDefinition("HelperType", TypeCategory.STRING_ENUM, 32, ["Normal", "Player", "Proj"], Location("mtl/builtins.py", line_number())),
        TypeDefinition("HitFlag", TypeCategory.STRING_FLAG, 32, ["H", "L", "A", "M", "F", "D", "+", "-"], Location("mtl/builtins.py", line_number())),
        TypeDefinition("GuardFlag", TypeCategory.STRING_FLAG, 32, ["H", "L", "A", "M"], Location("mtl/builtins.py", line_number())),
        TypeDefinition("TeamType", TypeCategory.STRING_ENUM, 32, ["E", "B", "F"], Location("mtl/builtins.py", line_number())),
        TypeDefinition("HitAnimType", TypeCategory.STRING_ENUM, 32, ["Light", "Medium", "Hard", "Back", "Up", "DiagUp"], Location("mtl/builtins.py", line_number())),
        TypeDefinition("AttackType", TypeCategory.STRING_ENUM, 32, ["High", "Low", "Trip", "None"], Location("mtl/builtins.py", line_number())),
    ]

def getBaseTriggers() -> List[TriggerDefinition]:
    return [
        ## MUGEN trigger functions
        TriggerDefinition("abs", "numeric", None, [TriggerParameter("exprn", "numeric")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("acos", "float", None, [TriggerParameter("exprn", "numeric")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("AiLevel", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Alive", "bool", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Anim", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("AnimElem", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("AnimElemNo", "int", None, [TriggerParameter("exprn", "int")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("AnimElemTime", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("AnimElemTime", "int", None, [TriggerParameter("exprn", "int")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("AnimExist", "bool", None, [TriggerParameter("exprn", "int")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("AnimExist", "bool", None, [TriggerParameter("exprn", "int")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("AnimTime", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("asin", "float", None, [TriggerParameter("exprn", "numeric")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("atan", "float", None, [TriggerParameter("exprn", "numeric")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("AuthorName", "string", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("BackEdgeBodyDist", "float", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("BackEdgeDist", "float", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("CanRecover", "bool", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("ceil", "int", None, [TriggerParameter("exprn", "numeric")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Command", "string", None, [], None, Location("mtl/builtins.py", line_number())),
        #TriggerDefinition("cond", "T", None, [TriggerParameter("exp_cond", "bool, exp_true")], Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Const", "numeric", None, [TriggerParameter("param_name", "ConstType")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Const240p", "float", None, [TriggerParameter("exprn", "numeric")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Const480p", "float", None, [TriggerParameter("exprn", "numeric")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Const720p", "float", None, [TriggerParameter("exprn", "numeric")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("cos", "float", None, [TriggerParameter("exprn", "numeric")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Ctrl", "bool", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("DrawGame", "bool", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("e", "float", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("exp", "float", None, [TriggerParameter("exprn", "numeric")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Facing", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("floor", "int", None, [TriggerParameter("exprn", "float")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("FrontEdgeBodyDist", "float", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("FrontEdgeDist", "float", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("fvar", "float", None, [TriggerParameter("exprn", "int")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("GameHeight", "float", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("GameTime", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("GameWidth", "float", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("GetHitVar", "numeric", None, [TriggerParameter("param_name", "HitVarType")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("HitCount", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("HitFall", "bool", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("HitOver", "bool", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("HitPauseTime", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("HitShakeOver", "bool", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("HitVel", "float,float", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("ID", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        #TriggerDefinition("ifelse", "T", None, [TriggerParameter("exp_cond", "bool, exp_true")], Location("mtl/builtins.py", line_number())),
        TriggerDefinition("InGuardDist", "bool", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("IsHelper", "bool", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("IsHelper", "bool", None, [TriggerParameter("exprn", "int")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("IsHomeTeam", "bool", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Life", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("LifeMax", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("ln", "float", None, [TriggerParameter("exprn", "numeric")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("log", "float", None, [TriggerParameter("exp1", "numeric")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Lose", "bool", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("LoseKO", "bool", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("LoseTime", "bool", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("MatchNo", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("MatchOver", "bool", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("MoveContact", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("MoveGuarded", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("MoveHit", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("MoveReversed", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Name", "string", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("NumEnemy", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("NumExplod", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("NumExplod", "int", None, [TriggerParameter("exprn", "int")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("NumPartner", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("NumProj", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("NumProjID", "int", None, [TriggerParameter("exprn", "int")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("NumTarget", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("NumTarget", "int", None, [TriggerParameter("exprn", "int")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("P1Name", "string", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("P2BodyDist", "float,float", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("P2Dist", "float,float", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("P2Life", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("P2Name", "string", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("P2StateNo", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("P3Name", "string", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("P4Name", "string", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("PalNo", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("ParentDist", "float,float", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("pi", "float", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Pos", "float,float", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Power", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("PowerMax", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("PlayerIDExist", "bool", None, [TriggerParameter("ID_number", "int")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("PrevStateNo", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("ProjCancelTime", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("ProjCancelTime", "int", None, [TriggerParameter("exprn", "int")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("ProjContactTime", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("ProjContactTime", "int", None, [TriggerParameter("exprn", "int")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("ProjGuardedTime", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("ProjGuardedTime", "int", None, [TriggerParameter("exprn", "int")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("ProjHitTime", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("ProjHitTime", "int", None, [TriggerParameter("exprn", "int")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Random", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("RootDist", "float,float", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("RoundNo", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("RoundsExisted", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("RoundState", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("ScreenPos", "float,float", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("SelfAnimExist", "bool", None, [TriggerParameter("exprn", "int")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("SelfAnimExist", "bool", None, [TriggerParameter("exprn", "int")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("sin", "float", None, [TriggerParameter("exprn", "numeric")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("StateNo", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("StageVar", "string", None, [TriggerParameter("param_name", "StageVarType")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("sysfvar", "float", None, [TriggerParameter("exprn", "int")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("sysvar", "int", None, [TriggerParameter("exprn", "int")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("tan", "float", None, [TriggerParameter("exprn", "numeric")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("TeamSide", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("TicksPerSecond", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Time", "int", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("var", "int", None, [TriggerParameter("exprn", "int")], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Vel", "float,float", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("Win", "bool", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("WinKO", "bool", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("WinTime", "bool", None, [], None, Location("mtl/builtins.py", line_number())),
        TriggerDefinition("WinPerfect", "bool", None, [], None, Location("mtl/builtins.py", line_number())),

        ## builtin operator functions
        TriggerDefinition("operator!", "bool", builtin_not, [TriggerParameter("expr", "bool")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator!", "bool", builtin_not, [TriggerParameter("expr", "int")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator!", "bool", builtin_not, [TriggerParameter("expr", "float")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),

        TriggerDefinition("operator-", "int", builtin_negate, [TriggerParameter("expr", "int")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator-", "float", builtin_negate, [TriggerParameter("expr", "float")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),

        TriggerDefinition("operator~", "int", builtin_bitnot, [TriggerParameter("expr", "int")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),

        TriggerDefinition("operator+", "int", builtin_add, [TriggerParameter("expr1", "int"), TriggerParameter("expr2", "int")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator+", "float", builtin_add, [TriggerParameter("expr1", "float"), TriggerParameter("expr2", "float")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator-", "int", builtin_sub, [TriggerParameter("expr1", "int"), TriggerParameter("expr2", "int")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator-", "float", builtin_sub, [TriggerParameter("expr1", "float"), TriggerParameter("expr2", "float")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator*", "int", builtin_mult, [TriggerParameter("expr1", "int"), TriggerParameter("expr2", "int")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator*", "float", builtin_mult, [TriggerParameter("expr1", "float"), TriggerParameter("expr2", "float")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator/", "int", builtin_div, [TriggerParameter("expr1", "int"), TriggerParameter("expr2", "int")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator/", "float", builtin_div, [TriggerParameter("expr1", "float"), TriggerParameter("expr2", "float")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator%", "int", builtin_div, [TriggerParameter("expr1", "int"), TriggerParameter("expr2", "int")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator**", "int", builtin_exp, [TriggerParameter("expr1", "int"), TriggerParameter("expr2", "int")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator**", "float", builtin_exp, [TriggerParameter("expr1", "float"), TriggerParameter("expr2", "float")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),

        TriggerDefinition("operator=", "bool", builtin_eq, [TriggerParameter("expr1", "int"), TriggerParameter("expr2", "int")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator=", "bool", builtin_eq, [TriggerParameter("expr1", "float"), TriggerParameter("expr2", "float")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator!=", "bool", builtin_neq, [TriggerParameter("expr1", "int"), TriggerParameter("expr2", "int")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator!=", "bool", builtin_neq, [TriggerParameter("expr1", "float"), TriggerParameter("expr2", "float")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),

        TriggerDefinition("operator&", "int", builtin_bitand, [TriggerParameter("expr1", "int"), TriggerParameter("expr2", "int")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator|", "int", builtin_bitor, [TriggerParameter("expr1", "int"), TriggerParameter("expr2", "int")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator^", "int", builtin_bitxor, [TriggerParameter("expr1", "int"), TriggerParameter("expr2", "int")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),

        TriggerDefinition("operator:=", "int", builtin_assign, [TriggerParameter("expr1", "int"), TriggerParameter("expr2", "int")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),

        TriggerDefinition("operator<", "bool", builtin_lt, [TriggerParameter("expr1", "int"), TriggerParameter("expr2", "int")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator<=", "bool", builtin_lte, [TriggerParameter("expr1", "int"), TriggerParameter("expr2", "int")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator>", "bool", builtin_gt, [TriggerParameter("expr1", "int"), TriggerParameter("expr2", "int")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator>=", "bool", builtin_gte, [TriggerParameter("expr1", "int"), TriggerParameter("expr2", "int")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),

        TriggerDefinition("operator<", "bool", builtin_lt, [TriggerParameter("expr1", "float"), TriggerParameter("expr2", "float")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator<=", "bool", builtin_lte, [TriggerParameter("expr1", "float"), TriggerParameter("expr2", "float")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator>", "bool", builtin_gt, [TriggerParameter("expr1", "float"), TriggerParameter("expr2", "float")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator>=", "bool", builtin_gte, [TriggerParameter("expr1", "float"), TriggerParameter("expr2", "float")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),

        TriggerDefinition("operator&&", "bool", builtin_and, [TriggerParameter("expr1", "bool"), TriggerParameter("expr2", "bool...?")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator||", "bool", builtin_or, [TriggerParameter("expr1", "bool"), TriggerParameter("expr2", "bool...?")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
        TriggerDefinition("operator^^", "bool", builtin_xor, [TriggerParameter("expr1", "bool"), TriggerParameter("expr2", "bool")], None, Location("mtl/builtins.py", line_number()), TriggerCategory.OPERATOR),
    ]

def builtin_not(exprs: List[Expression], ctx: TranslationContext) -> Expression:
    if (result := find(ctx.types, lambda k: k.name == "bool")) != None:
        return Expression(result, f"(!{exprs[0].value})")
    raise TranslationError("Failed to find the `bool` type in project, check if builtins are broken.", Location("mtl/builtins.py", line_number()))

def builtin_negate(exprs: List[Expression], ctx: TranslationContext) -> Expression:
    return Expression(exprs[0].type, f"(-{exprs[0].value})")

def builtin_bitnot(exprs: List[Expression], ctx: TranslationContext) -> Expression:
    return Expression(exprs[0].type, f"(~{exprs[0].value})")

def builtin_binary(exprs: List[Expression], ctx: TranslationContext, op: str) -> Expression:
    if (result := typeConvertWidest(exprs[0].type, exprs[1].type, ctx, Location("mtl/builtins.py", line_number()))) != None:
        return Expression(result, f"({exprs[0].value} {op} {exprs[1].value})")
    raise TranslationError(f"Failed to convert an expression of type {exprs[0].type.name} to type {exprs[1].type.name} for operator {op}.", Location("mtl/builtins.py", line_number()))

def builtin_add(exprs: List[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "+")
def builtin_sub(exprs: List[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "-")
def builtin_mult(exprs: List[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "*")
def builtin_div(exprs: List[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "/")
def builtin_mod(exprs: List[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "%")
def builtin_exp(exprs: List[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "**")
def builtin_xor(exprs: List[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "^^")
def builtin_eq(exprs: List[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "=")
def builtin_neq(exprs: List[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "!=")
def builtin_bitand(exprs: List[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "&")
def builtin_bitor(exprs: List[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "|")
def builtin_bitxor(exprs: List[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "^")
def builtin_assign(exprs: List[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, ":=")
def builtin_lt(exprs: List[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "<")
def builtin_lte(exprs: List[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "<=")
def builtin_gt(exprs: List[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, ">")
def builtin_gte(exprs: List[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, ">=")

# special cases. these accept variable inputs to support trigger collapsing.
## TODO: support variable inputs properly...
def builtin_and(exprs: List[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "&&")
def builtin_or(exprs: List[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "||")

def getBaseTemplates() -> List[TemplateDefinition]:
    return [
        TemplateDefinition("AfterImage", [TemplateParameter("time", "int", False), TemplateParameter("length", "int", False), TemplateParameter("palcolor", "int", False), TemplateParameter("palinvertall", "bool", False), TemplateParameter("palbright", "int,int,int", False), TemplateParameter("palcontrast", "int,int,int", False), TemplateParameter("palpostbright", "int,int,int", False), TemplateParameter("paladd", "int,int,int", False), TemplateParameter("palmul", "float,float,float", False), TemplateParameter("timegap", "int", False), TemplateParameter("framegap", "int", False), TemplateParameter("trans", "TransType", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("AfterImageTime", [TemplateParameter("time", "int", True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("AngleAdd", [TemplateParameter("value", "float", True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("AngleDraw", [TemplateParameter("value", "float", False), TemplateParameter("scale", "float,float", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("AngleMul", [TemplateParameter("value", "float", True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("AngleSet", [TemplateParameter("value", "float", True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("AssertSpecial", [TemplateParameter("flag", "AssertType", True), TemplateParameter("flag2", "AssertType", False), TemplateParameter("flag3", "AssertType", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("AttackDist", [TemplateParameter("value", "int", True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("AttackMulSet", [TemplateParameter("value", "float", True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("BindToParent", [TemplateParameter("time", "int", False), TemplateParameter("facing", "int", False), TemplateParameter("pos", "float,float", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("BindToRoot", [TemplateParameter("time", "int", False), TemplateParameter("facing", "int", False), TemplateParameter("pos", "float,float", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("BindToTarget", [TemplateParameter("time", "int", False), TemplateParameter("id", "int", False), TemplateParameter("pos", "float,float,BindType", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("ChangeAnim", [TemplateParameter("value", "int", True), TemplateParameter("elem", "int", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("ChangeAnim2", [TemplateParameter("value", "int", True), TemplateParameter("elem", "int", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("ChangeState", [TemplateParameter("value", "int", True), TemplateParameter("ctrl", "bool", False), TemplateParameter("anim", "int", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("ClearClipboard", [], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("CtrlSet", [TemplateParameter("ctrl", "bool", False), TemplateParameter("value", "bool", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("DefenceMulSet", [TemplateParameter("value", "float", True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("DestroySelf", [], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("DisplayToClipboard", [TemplateParameter("text", "string", True), TemplateParameter("params", "vector", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("EnvColor", [TemplateParameter("value", "int,int,int", False), TemplateParameter("time", "int", False), TemplateParameter("under", "bool", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("EnvShake", [TemplateParameter("time", "int", True), TemplateParameter("freq", "float", False), TemplateParameter("ampl", "int", False), TemplateParameter("phase", "float", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("Explod", [TemplateParameter("anim", "int", True), TemplateParameter("id", "int", False), TemplateParameter("pos", "float,float", False), TemplateParameter("postype", "PosType", False), TemplateParameter("facing", "int", False), TemplateParameter("vfacing", "int", False), TemplateParameter("bindtime", "int", False), TemplateParameter("vel", "float,float", False), TemplateParameter("accel", "float,float", False), TemplateParameter("random", "int,int", False), TemplateParameter("removetime", "int", False), TemplateParameter("supermove", "bool", False), TemplateParameter("supermovetime", "int", False), TemplateParameter("pausemovetime", "int", False), TemplateParameter("scale", "float,float", False), TemplateParameter("sprpriority", "int", False), TemplateParameter("ontop", "bool", False), TemplateParameter("shadow", "bool", False), TemplateParameter("ownpal", "bool", False), TemplateParameter("removeongethit", "bool", False), TemplateParameter("ignorehitpause", "bool", False), TemplateParameter("trans", "TransType", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("ExplodBindTime", [TemplateParameter("id", "int", False), TemplateParameter("time", "int", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("ForceFeedback", [TemplateParameter("waveform", "WaveType", False), TemplateParameter("time", "int", False), TemplateParameter("freq", "int,float,float,float", False), TemplateParameter("ampl", "int,float,float,float", False), TemplateParameter("self", "bool", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("FallEnvShake", [], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("GameMakeint", [TemplateParameter("value", "int", False), TemplateParameter("under", "bool", False), TemplateParameter("pos", "float,float", False), TemplateParameter("random", "int", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("Gravity", [], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("Helper", [TemplateParameter("helpertype", "HelperType", False), TemplateParameter("name", "string", False), TemplateParameter("id", "int", False), TemplateParameter("pos", "float,float", False), TemplateParameter("postype", "PosType", False), TemplateParameter("facing", "int", False), TemplateParameter("stateno", "int", False), TemplateParameter("keyctrl", "bool", False), TemplateParameter("ownpal", "bool", False), TemplateParameter("supermovetime", "int", False), TemplateParameter("pausemovetime", "int", False), TemplateParameter("size.xscale", "float", False), TemplateParameter("size.yscale", "float", False), TemplateParameter("size.ground.back", "int", False), TemplateParameter("size.ground.front", "int", False), TemplateParameter("size.air.back", "int", False), TemplateParameter("size.ait.front", "int", False), TemplateParameter("size.height", "int", False), TemplateParameter("size.proj.doscale", "int", False), TemplateParameter("size.head.pos", "int,int", False), TemplateParameter("size.mid.pos", "int,int", False), TemplateParameter("size.shadowoffset", "int", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("HitAdd", [TemplateParameter("value", "int", True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("HitBy", [TemplateParameter("value", "HitType,HitAttr", False), TemplateParameter("value2", "HitType,HitAttr", False), TemplateParameter("time", "int", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("HitDef", [TemplateParameter("attr", "HitType,HitAttr", True), TemplateParameter("hitflag", "HitFlag", False), TemplateParameter("guardflag", "GuardFlag", False), TemplateParameter("affectteam", "TeamType", False), TemplateParameter("animtype", "HitAnimType", False), TemplateParameter("air.animtype", "HitAnimType", False), TemplateParameter("fall.animtype", "HitAnimType", False), TemplateParameter("priority", "int,PriorityType", False), TemplateParameter("damage", "int,int", False), TemplateParameter("pausetime", "int,int", False), TemplateParameter("guard.pausetime", "int,int", False), TemplateParameter("sparkno", "cint", False), TemplateParameter("guard.sparkno", "cint", False), TemplateParameter("sparkxy", "int,int", False), TemplateParameter("hitsound", "cint,int", False), TemplateParameter("guardsound", "cint,int", False), TemplateParameter("ground.type", "AttackType", False), TemplateParameter("air.type", "AttackType", False), TemplateParameter("ground.slidetime", "int", False), TemplateParameter("guard.slidetime", "int", False), TemplateParameter("ground.hittime", "int", False), TemplateParameter("guard.hittime", "int", False), TemplateParameter("air.hittime", "int", False), TemplateParameter("guard.ctrltime", "int", False), TemplateParameter("guard.dist", "int", False), TemplateParameter("yaccel", "float", False), TemplateParameter("ground.velocity", "float,float", False), TemplateParameter("guard.velocity", "float", False), TemplateParameter("air.velocity", "float,float", False), TemplateParameter("airguard.velocity", "float,float", False), TemplateParameter("ground.cornerpush.veloff", "float", False), TemplateParameter("air.cornerpush.veloff", "float", False), TemplateParameter("down.cornerpush.veloff", "float", False), TemplateParameter("guard.cornerpush.veloff", "float", False), TemplateParameter("airguard.cornerpush.veloff", "float", False), TemplateParameter("airguard.ctrltime", "int", False), TemplateParameter("air.juggle", "int", False), TemplateParameter("mindist", "int,int", False), TemplateParameter("maxdist", "int,int", False), TemplateParameter("snap", "int,int", False), TemplateParameter("p1sprpriority", "int", False), TemplateParameter("p2sprpriority", "int", False), TemplateParameter("p1facing", "int", False), TemplateParameter("p1getp2facing", "int", False), TemplateParameter("p2facing", "int", False), TemplateParameter("p1stateno", "int", False), TemplateParameter("p2stateno", "int", False), TemplateParameter("p2getp1state", "bool", False), TemplateParameter("forcestand", "bool", False), TemplateParameter("fall", "bool", False), TemplateParameter("fall.xvelocity", "float", False), TemplateParameter("fall.yvelocity", "float", False), TemplateParameter("fall.recover", "bool", False), TemplateParameter("fall.recovertime", "int", False), TemplateParameter("fall.damage", "int", False), TemplateParameter("air.fall", "bool", False), TemplateParameter("forcenofall", "bool", False), TemplateParameter("down.velocity", "float,float", False), TemplateParameter("down.hittime", "int", False), TemplateParameter("down.bounce", "bool", False), TemplateParameter("id", "int", False), TemplateParameter("chainid", "int", False), TemplateParameter("nochainid", "int,int", False), TemplateParameter("hitonce", "bool", False), TemplateParameter("kill", "bool", False), TemplateParameter("guard.kill", "bool", False), TemplateParameter("fall.kill", "bool", False), TemplateParameter("numhits", "int", False), TemplateParameter("getpower", "int,int", False), TemplateParameter("givepower", "int,int", False), TemplateParameter("palfx.time", "int", False), TemplateParameter("palfx.mul", "int,int,int", False), TemplateParameter("palfx.add", "int,int,int", False), TemplateParameter("envshake.time", "int", False), TemplateParameter("envshake.freq", "float", False), TemplateParameter("envshake.ampl", "int", False), TemplateParameter("envshake.phase", "float", False), TemplateParameter("fall.envshake.time", "int", False), TemplateParameter("fall.envshake.freq", "float", False), TemplateParameter("fall.envshake.ampl", "int", False), TemplateParameter("fall.envshake.phase", "float", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("HitFallDamage", [], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("HitFallSet", [TemplateParameter("value", "int", False), TemplateParameter("xvel", "float", False), TemplateParameter("yvel", "float", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("HitFallVel", [], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("HitOverride", [TemplateParameter("attr", "HitType,HitAttr", True), TemplateParameter("stateno", "int", True), TemplateParameter("slot", "int", False), TemplateParameter("time", "int", False), TemplateParameter("forceair", "bool", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("HitVelSet", [TemplateParameter("x", "bool", False), TemplateParameter("y", "bool", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("LifeAdd", [TemplateParameter("value", "int", True), TemplateParameter("kill", "bool", False), TemplateParameter("absolute", "bool", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("LifeSet", [TemplateParameter("value", "int", True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("MakeDust", [TemplateParameter("pos", "int,int", False), TemplateParameter("pos2", "float,float", False), TemplateParameter("spacing", "int", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("ModifyExplod", [TemplateParameter("id", "int", True), TemplateParameter("int", "int", False), TemplateParameter("pos", "float,float", False), TemplateParameter("postype", "PosType", False), TemplateParameter("facing", "int", False), TemplateParameter("vfacing", "int", False), TemplateParameter("bindtime", "int", False), TemplateParameter("vel", "float,float", False), TemplateParameter("accel", "float,float", False), TemplateParameter("random", "int,int", False), TemplateParameter("removetime", "int", False), TemplateParameter("supermove", "bool", False), TemplateParameter("supermovetime", "int", False), TemplateParameter("pausemovetime", "int", False), TemplateParameter("scale", "float,float", False), TemplateParameter("sprpriority", "int", False), TemplateParameter("ontop", "bool", False), TemplateParameter("shadow", "bool", False), TemplateParameter("ownpal", "bool", False), TemplateParameter("removeongethit", "bool", False), TemplateParameter("ignorehitpause", "bool", False), TemplateParameter("trans", "TransType", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("MoveHitReset", [], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("NotHitBy", [TemplateParameter("value", "HitType,HitAttr...?", False), TemplateParameter("value2", "HitType,HitAttr...?", False), TemplateParameter("time", "int", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("Null", [], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("Offset", [TemplateParameter("x", "float", False), TemplateParameter("y", "float", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("PalFX", [TemplateParameter("time", "int", False), TemplateParameter("add", "int,int,int", False), TemplateParameter("mul", "int,int,int", False), TemplateParameter("sinadd", "int,int,int,int", False), TemplateParameter("invertall", "bool", False), TemplateParameter("color", "int", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("ParentVarAdd", [TemplateParameter("v", "int", True), TemplateParameter("fv", "int", True), TemplateParameter("value", "float", True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("ParentVarSet", [TemplateParameter("v", "int", True), TemplateParameter("fv", "int", True), TemplateParameter("value", "float", True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("Pause", [TemplateParameter("time", "int", True), TemplateParameter("endcmdbuftime", "int", False), TemplateParameter("movetime", "int", False), TemplateParameter("pausebg", "bool", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("PlayerPush", [TemplateParameter("value", "bool", True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("PlaySnd", [TemplateParameter("value", "cint,int", True), TemplateParameter("volumescale", "float", False), TemplateParameter("channel", "int", False), TemplateParameter("lowpriority", "bool", False), TemplateParameter("freqmul", "float", False), TemplateParameter("loop", "bool", False), TemplateParameter("pan", "int", False), TemplateParameter("abspan", "int", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("PosAdd", [TemplateParameter("x", "float", False), TemplateParameter("y", "float", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("PosFreeze", [TemplateParameter("value", "bool", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("PosSet", [TemplateParameter("x", "float", False), TemplateParameter("y", "float", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("PowerAdd", [TemplateParameter("value", "int", True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("PowerSet", [TemplateParameter("value", "int", True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("Projectile", [TemplateParameter("projid", "int", False), TemplateParameter("projint", "int", False), TemplateParameter("projhitint", "int", False), TemplateParameter("projremint", "int", False), TemplateParameter("projscale", "float,float", False), TemplateParameter("projremove", "bool", False), TemplateParameter("projremovetime", "int", False), TemplateParameter("velocity", "float,float", False), TemplateParameter("remvelocity", "float,float", False), TemplateParameter("accel", "float,float", False), TemplateParameter("velmul", "float,float", False), TemplateParameter("projhits", "int", False), TemplateParameter("projmisstime", "int", False), TemplateParameter("projpriority", "int", False), TemplateParameter("projsprpriority", "int", False), TemplateParameter("projedgebound", "int", False), TemplateParameter("projstagebound", "int", False), TemplateParameter("projheightbound", "int,int", False), TemplateParameter("offset", "int,int", False), TemplateParameter("postype", "PosType", False), TemplateParameter("projshadow", "bool", False), TemplateParameter("supermovetime", "int", False), TemplateParameter("pausemovetime", "int", False), TemplateParameter("afterimage.time", "int", False), TemplateParameter("afterimage.length", "int", False), TemplateParameter("afterimage.palcolor", "int", False), TemplateParameter("afterimage.palinvertall", "bool", False), TemplateParameter("afterimage.palbright", "int,int,int", False), TemplateParameter("afterimage.palcontrast", "int,int,int", False), TemplateParameter("afterimage.palpostbright", "int,int,int", False), TemplateParameter("afterimage.paladd", "int,int,int", False), TemplateParameter("afterimage.palmul", "float,float,float", False), TemplateParameter("afterimage.timegap", "int", False), TemplateParameter("afterimage.framegap", "int", False), TemplateParameter("afterimage.trans", "TransType", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("RemapPal", [TemplateParameter("source", "int,int", True), TemplateParameter("dest", "int,int", True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("RemoveExplod", [TemplateParameter("id", "int", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("ReversalDef", [TemplateParameter("reversal.attr", "HitType,HitAttr", True), TemplateParameter("pausetime", "int,int", False), TemplateParameter("sparkno", "int", False), TemplateParameter("hitsound", "int,int", False), TemplateParameter("p1stateno", "int", False), TemplateParameter("p2stateno", "int", False), TemplateParameter("p1sprpriority", "int", False), TemplateParameter("p2sprpriority", "int", False), TemplateParameter("sparkxy", "int,int", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("ScreenBound", [TemplateParameter("value", "bool", False), TemplateParameter("movecamera", "bool,bool", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("SelfState", [TemplateParameter("value", "int", True), TemplateParameter("ctrl", "bool", False), TemplateParameter("anim", "int", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("SprPriority", [TemplateParameter("value", "int", True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("StateTypeSet", [TemplateParameter("statetype", "StateType", False), TemplateParameter("movetype", "MoveType", False), TemplateParameter("physics", "PhysicsType", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("SndPan", [TemplateParameter("channel", "int", True), TemplateParameter("pan", "int", True), TemplateParameter("abspan", "int", True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("StopSnd", [TemplateParameter("channel", "int", True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("SuperPause", [TemplateParameter("time", "int", False), TemplateParameter("anim", "int", False), TemplateParameter("sound", "int,int", False), TemplateParameter("pos", "float,float", False), TemplateParameter("darken", "bool", False), TemplateParameter("p2defmul", "float", False), TemplateParameter("poweradd", "int", False), TemplateParameter("unhittable", "bool", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("TargetBind", [TemplateParameter("time", "int", False), TemplateParameter("id", "int", False), TemplateParameter("pos", "float,float", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("TargetDrop", [TemplateParameter("excludeid", "int", False), TemplateParameter("keepone", "bool", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("TargetFacing", [TemplateParameter("value", "int", True), TemplateParameter("id", "int", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("TargetLifeAdd", [TemplateParameter("value", "int", True), TemplateParameter("id", "int", False), TemplateParameter("kill", "bool", False), TemplateParameter("absolute", "bool", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("TargetPowerAdd", [TemplateParameter("value", "int", True), TemplateParameter("id", "int", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("TargetState", [TemplateParameter("value", "int", True), TemplateParameter("id", "int", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("TargetVelAdd", [TemplateParameter("x", "float", False), TemplateParameter("y", "float", False), TemplateParameter("id", "int", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("TargetVelSet", [TemplateParameter("x", "float", False), TemplateParameter("y", "float", False), TemplateParameter("id", "int", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("Trans", [TemplateParameter("trans", "TransType", True), TemplateParameter("alpha", "int,int", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("Turn", [], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("VarAdd", [TemplateParameter("v", "int", True), TemplateParameter("fv", "int", True), TemplateParameter("value", "float", True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("VarSet", [TemplateParameter("v", "int", True), TemplateParameter("fv", "int", True), TemplateParameter("value", "float", True)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("VarRandom", [TemplateParameter("v", "int", True), TemplateParameter("range", "int,int", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("VarRangeSet", [TemplateParameter("value", "int", True), TemplateParameter("fvalue", "float", True), TemplateParameter("first", "int", False), TemplateParameter("last", "int", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("VelAdd", [TemplateParameter("x", "float", False), TemplateParameter("y", "float", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("VelMul", [TemplateParameter("x", "float", False), TemplateParameter("y", "float", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("VelSet", [TemplateParameter("x", "float", False), TemplateParameter("y", "float", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("VictoryQuote", [TemplateParameter("value", "int", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN),
        TemplateDefinition("Width", [TemplateParameter("edge", "int,int", False), TemplateParameter("player", "int,int", False), TemplateParameter("value", "int,int", False)], [], [], Location("mtl/builtins.py", line_number()), TemplateCategory.BUILTIN)
    ]