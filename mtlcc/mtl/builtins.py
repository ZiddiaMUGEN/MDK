from typing import List
from inspect import currentframe

from mtl.utils import find, typeConvertWidest
from mtl.shared import TranslationContext, TypeDefinition, TypeCategory, TriggerDefinition, TriggerParameter, TriggerCategory, Expression
from mtl.error import TranslationError

def line_number() -> int:
    cf = currentframe()
    if cf != None and cf.f_back != None:
        return cf.f_back.f_lineno
    else:
        return 0

def getBaseTypes() -> List[TypeDefinition]:
    return [
        TypeDefinition("int", TypeCategory.BUILTIN, 32, [], "mtl/builtins.py", line_number()),
        TypeDefinition("float", TypeCategory.BUILTIN, 32, [], "mtl/builtins.py", line_number()),
        TypeDefinition("short", TypeCategory.BUILTIN, 16, [], "mtl/builtins.py", line_number()),
        TypeDefinition("byte", TypeCategory.BUILTIN, 8, [], "mtl/builtins.py", line_number()),
        TypeDefinition("char", TypeCategory.BUILTIN, 8, [], "mtl/builtins.py", line_number()),
        TypeDefinition("bool", TypeCategory.BUILTIN, 1, [], "mtl/builtins.py", line_number()),
        TypeDefinition("StateType", TypeCategory.STRING_ENUM, 32, ["S", "C", "A", "L", "U"], "mtl/builtins.py", line_number()),
        TypeDefinition("MoveType", TypeCategory.STRING_ENUM, 32, ["A", "I", "H", "U"], "mtl/builtins.py", line_number()),
        TypeDefinition("PhysicsType", TypeCategory.STRING_ENUM, 32, ["S", "C", "A", "N", "U"], "mtl/builtins.py", line_number()),
        TypeDefinition("HitType", TypeCategory.STRING_FLAG, 32, ["S", "C", "A"], "mtl/builtins.py", line_number()),
        TypeDefinition("HitAttr", TypeCategory.STRING_FLAG, 32, ["N", "S", "H", "A", "T"], "mtl/builtins.py", line_number()),
    ]

def getBaseTriggers() -> List[TriggerDefinition]:
    return [
        ## MUGEN trigger functions
        TriggerDefinition("abs", "numeric", None, [TriggerParameter("exprn", "numeric")], "mtl/builtins.py", line_number()),
        TriggerDefinition("acos", "float", None, [TriggerParameter("exprn", "numeric")], "mtl/builtins.py", line_number()),
        TriggerDefinition("AiLevel", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("Alive", "bool", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("Anim", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("AnimElem", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("AnimElemNo", "int", None, [TriggerParameter("exprn", "int")], "mtl/builtins.py", line_number()),
        TriggerDefinition("AnimElemTime", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("AnimElemTime", "int", None, [TriggerParameter("exprn", "int")], "mtl/builtins.py", line_number()),
        TriggerDefinition("AnimExist", "bool", None, [TriggerParameter("exprn", "anim")], "mtl/builtins.py", line_number()),
        TriggerDefinition("AnimExist", "bool", None, [TriggerParameter("exprn", "int")], "mtl/builtins.py", line_number()),
        TriggerDefinition("AnimTime", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("asin", "float", None, [TriggerParameter("exprn", "numeric")], "mtl/builtins.py", line_number()),
        TriggerDefinition("atan", "float", None, [TriggerParameter("exprn", "numeric")], "mtl/builtins.py", line_number()),
        TriggerDefinition("AuthorName", "string", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("BackEdgeBodyDist", "float", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("BackEdgeDist", "float", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("CanRecover", "bool", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("ceil", "int", None, [TriggerParameter("exprn", "numeric")], "mtl/builtins.py", line_number()),
        TriggerDefinition("Command", "string", None, [], "mtl/builtins.py", line_number()),
        #TriggerDefinition("cond", "T", None, [TriggerParameter("exp_cond", "bool, exp_true")], "mtl/builtins.py", line_number()),
        TriggerDefinition("Const", "numeric", None, [TriggerParameter("const param_name", "string")], "mtl/builtins.py", line_number()),
        TriggerDefinition("Const240p", "float", None, [TriggerParameter("exprn", "numeric")], "mtl/builtins.py", line_number()),
        TriggerDefinition("Const480p", "float", None, [TriggerParameter("exprn", "numeric")], "mtl/builtins.py", line_number()),
        TriggerDefinition("Const720p", "float", None, [TriggerParameter("exprn", "numeric")], "mtl/builtins.py", line_number()),
        TriggerDefinition("cos", "float", None, [TriggerParameter("exprn", "numeric")], "mtl/builtins.py", line_number()),
        TriggerDefinition("Ctrl", "bool", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("DrawGame", "bool", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("e", "float", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("exp", "float", None, [TriggerParameter("exprn", "numeric")], "mtl/builtins.py", line_number()),
        TriggerDefinition("Facing", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("floor", "int", None, [TriggerParameter("exprn", "float")], "mtl/builtins.py", line_number()),
        TriggerDefinition("FrontEdgeBodyDist", "float", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("FrontEdgeDist", "float", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("fvar", "float", None, [TriggerParameter("exprn", "int")], "mtl/builtins.py", line_number()),
        TriggerDefinition("GameHeight", "float", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("GameTime", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("GameWidth", "float", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("GetHitVar", "numeric", None, [TriggerParameter("const param_name", "string")], "mtl/builtins.py", line_number()),
        TriggerDefinition("HitCount", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("HitFall", "bool", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("HitOver", "bool", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("HitPauseTime", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("HitShakeOver", "bool", None, [], "mtl/builtins.py", line_number()),
        #TriggerDefinition("HitVel", "vector2", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("ID", "int", None, [], "mtl/builtins.py", line_number()),
        #TriggerDefinition("ifelse", "T", None, [TriggerParameter("exp_cond", "bool, exp_true")], "mtl/builtins.py", line_number()),
        TriggerDefinition("InGuardDist", "bool", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("IsHelper", "bool", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("IsHelper", "bool", None, [TriggerParameter("exprn", "int")], "mtl/builtins.py", line_number()),
        TriggerDefinition("IsHomeTeam", "bool", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("Life", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("LifeMax", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("ln", "float", None, [TriggerParameter("exprn", "numeric")], "mtl/builtins.py", line_number()),
        TriggerDefinition("log", "float", None, [TriggerParameter("exp1", "number, exp2")], "mtl/builtins.py", line_number()),
        TriggerDefinition("Lose", "bool", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("LoseKO", "bool", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("LoseTime", "bool", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("MatchNo", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("MatchOver", "bool", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("MoveContact", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("MoveGuarded", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("MoveHit", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("MoveReversed", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("Name", "string", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("NumEnemy", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("NumExplod", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("NumExplod", "int", None, [TriggerParameter("exprn", "int")], "mtl/builtins.py", line_number()),
        TriggerDefinition("NumPartner", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("NumProj", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("NumProjID", "int", None, [TriggerParameter("exprn", "int")], "mtl/builtins.py", line_number()),
        TriggerDefinition("NumTarget", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("NumTarget", "int", None, [TriggerParameter("exprn", "int")], "mtl/builtins.py", line_number()),
        TriggerDefinition("P1Name", "string", None, [], "mtl/builtins.py", line_number()),
        #TriggerDefinition("P2BodyDist", "vector2", None, [], "mtl/builtins.py", line_number()),
        #TriggerDefinition("P2Dist", "vector2", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("P2Life", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("P2Name", "string", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("P2StateNo", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("P3Name", "string", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("P4Name", "string", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("PalNo", "int", None, [], "mtl/builtins.py", line_number()),
        #TriggerDefinition("ParentDist", "vector2", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("pi", "float", None, [], "mtl/builtins.py", line_number()),
        #TriggerDefinition("Pos", "vector2", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("Power", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("PowerMax", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("PlayerIDExist", "bool", None, [TriggerParameter("ID_number", "int")], "mtl/builtins.py", line_number()),
        TriggerDefinition("PrevStateNo", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("ProjCancelTime", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("ProjCancelTime", "int", None, [TriggerParameter("exprn", "int")], "mtl/builtins.py", line_number()),
        TriggerDefinition("ProjContactTime", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("ProjContactTime", "int", None, [TriggerParameter("exprn", "int")], "mtl/builtins.py", line_number()),
        TriggerDefinition("ProjGuardedTime", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("ProjGuardedTime", "int", None, [TriggerParameter("exprn", "int")], "mtl/builtins.py", line_number()),
        TriggerDefinition("ProjHitTime", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("ProjHitTime", "int", None, [TriggerParameter("exprn", "int")], "mtl/builtins.py", line_number()),
        TriggerDefinition("Random", "int", None, [], "mtl/builtins.py", line_number()),
        #TriggerDefinition("RootDist", "vector2", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("RoundNo", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("RoundsExisted", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("RoundState", "int", None, [], "mtl/builtins.py", line_number()),
        #TriggerDefinition("ScreenPos", "vector2", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("SelfAnimExist", "bool", None, [TriggerParameter("exprn", "anim")], "mtl/builtins.py", line_number()),
        TriggerDefinition("SelfAnimExist", "bool", None, [TriggerParameter("exprn", "int")], "mtl/builtins.py", line_number()),
        TriggerDefinition("sin", "float", None, [TriggerParameter("exprn", "numeric")], "mtl/builtins.py", line_number()),
        TriggerDefinition("StateNo", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("StageVar", "string", None, [TriggerParameter("const param_name", "string")], "mtl/builtins.py", line_number()),
        TriggerDefinition("sysfvar", "float", None, [TriggerParameter("exprn", "int")], "mtl/builtins.py", line_number()),
        TriggerDefinition("sysvar", "int", None, [TriggerParameter("exprn", "int")], "mtl/builtins.py", line_number()),
        TriggerDefinition("tan", "float", None, [TriggerParameter("exprn", "numeric")], "mtl/builtins.py", line_number()),
        TriggerDefinition("TeamSide", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("TicksPerSecond", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("Time", "int", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("var", "int", None, [TriggerParameter("exprn", "int")], "mtl/builtins.py", line_number()),
        #TriggerDefinition("Vel", "vector2", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("Win", "bool", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("WinKO", "bool", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("WinTime", "bool", None, [], "mtl/builtins.py", line_number()),
        TriggerDefinition("WinPerfect", "bool", None, [], "mtl/builtins.py", line_number()),

        ## builtin operator functions
        TriggerDefinition("operator!", "bool", builtin_not, [TriggerParameter("expr", "bool")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),
        TriggerDefinition("operator!", "bool", builtin_not, [TriggerParameter("expr", "int")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),
        TriggerDefinition("operator!", "bool", builtin_not, [TriggerParameter("expr", "float")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),

        TriggerDefinition("operator-", "int", builtin_negate, [TriggerParameter("expr", "int")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),
        TriggerDefinition("operator-", "float", builtin_negate, [TriggerParameter("expr", "float")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),

        TriggerDefinition("operator~", "int", builtin_bitnot, [TriggerParameter("expr", "int")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),

        TriggerDefinition("operator+", "int", builtin_add, [TriggerParameter("expr1", "int"), TriggerParameter("expr2", "int")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),
        TriggerDefinition("operator+", "float", builtin_add, [TriggerParameter("expr1", "float"), TriggerParameter("expr2", "float")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),
        TriggerDefinition("operator-", "int", builtin_sub, [TriggerParameter("expr1", "int"), TriggerParameter("expr2", "int")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),
        TriggerDefinition("operator-", "float", builtin_sub, [TriggerParameter("expr1", "float"), TriggerParameter("expr2", "float")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),
        TriggerDefinition("operator*", "int", builtin_mult, [TriggerParameter("expr1", "int"), TriggerParameter("expr2", "int")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),
        TriggerDefinition("operator*", "float", builtin_mult, [TriggerParameter("expr1", "float"), TriggerParameter("expr2", "float")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),
        TriggerDefinition("operator/", "int", builtin_div, [TriggerParameter("expr1", "int"), TriggerParameter("expr2", "int")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),
        TriggerDefinition("operator/", "float", builtin_div, [TriggerParameter("expr1", "float"), TriggerParameter("expr2", "float")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),
        TriggerDefinition("operator%", "int", builtin_div, [TriggerParameter("expr1", "int"), TriggerParameter("expr2", "int")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),
        TriggerDefinition("operator**", "int", builtin_exp, [TriggerParameter("expr1", "int"), TriggerParameter("expr2", "int")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),
        TriggerDefinition("operator**", "float", builtin_exp, [TriggerParameter("expr1", "float"), TriggerParameter("expr2", "float")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),

        TriggerDefinition("operator&&", "bool", builtin_and, [TriggerParameter("expr1", "bool"), TriggerParameter("expr2", "bool")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),
        TriggerDefinition("operator||", "bool", builtin_or, [TriggerParameter("expr1", "bool"), TriggerParameter("expr2", "bool")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),
        TriggerDefinition("operator^^", "bool", builtin_xor, [TriggerParameter("expr1", "bool"), TriggerParameter("expr2", "bool")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),

        TriggerDefinition("operator=", "bool", builtin_eq, [TriggerParameter("expr1", "int"), TriggerParameter("expr2", "int")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),
        TriggerDefinition("operator=", "bool", builtin_eq, [TriggerParameter("expr1", "float"), TriggerParameter("expr2", "float")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),
        TriggerDefinition("operator!=", "bool", builtin_neq, [TriggerParameter("expr1", "int"), TriggerParameter("expr2", "int")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),
        TriggerDefinition("operator!=", "bool", builtin_neq, [TriggerParameter("expr1", "float"), TriggerParameter("expr2", "float")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),

        TriggerDefinition("operator&", "int", builtin_bitand, [TriggerParameter("expr1", "int"), TriggerParameter("expr2", "int")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),
        TriggerDefinition("operator|", "int", builtin_bitor, [TriggerParameter("expr1", "int"), TriggerParameter("expr2", "int")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),
        TriggerDefinition("operator^", "int", builtin_bitxor, [TriggerParameter("expr1", "int"), TriggerParameter("expr2", "int")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),

        TriggerDefinition("operator:=", "int", builtin_assign, [TriggerParameter("expr1", "int"), TriggerParameter("expr2", "int")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),

        TriggerDefinition("operator<", "bool", builtin_lt, [TriggerParameter("expr1", "int"), TriggerParameter("expr2", "int")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),
        TriggerDefinition("operator<=", "bool", builtin_lte, [TriggerParameter("expr1", "int"), TriggerParameter("expr2", "int")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),
        TriggerDefinition("operator>", "bool", builtin_gt, [TriggerParameter("expr1", "int"), TriggerParameter("expr2", "int")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),
        TriggerDefinition("operator>=", "bool", builtin_gte, [TriggerParameter("expr1", "int"), TriggerParameter("expr2", "int")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),

        TriggerDefinition("operator<", "bool", builtin_lt, [TriggerParameter("expr1", "float"), TriggerParameter("expr2", "float")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),
        TriggerDefinition("operator<=", "bool", builtin_lte, [TriggerParameter("expr1", "float"), TriggerParameter("expr2", "float")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),
        TriggerDefinition("operator>", "bool", builtin_gt, [TriggerParameter("expr1", "float"), TriggerParameter("expr2", "float")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),
        TriggerDefinition("operator>=", "bool", builtin_gte, [TriggerParameter("expr1", "float"), TriggerParameter("expr2", "float")], "mtl/builtins.py", line_number(), TriggerCategory.OPERATOR),
    ]

def builtin_not(exprs: List[Expression], ctx: TranslationContext) -> Expression:
    if (result := find(ctx.types, lambda k: k.name == "bool")) != None:
        return Expression(result, f"(!{exprs[0].value})")
    raise TranslationError("Failed to find the `bool` type in project, check if builtins are broken.", "mtl/builtins.py", line_number())

def builtin_negate(exprs: List[Expression], ctx: TranslationContext) -> Expression:
    return Expression(exprs[0].type, f"(-{exprs[0].value})")

def builtin_bitnot(exprs: List[Expression], ctx: TranslationContext) -> Expression:
    return Expression(exprs[0].type, f"(~{exprs[0].value})")

def builtin_binary(exprs: List[Expression], ctx: TranslationContext, op: str) -> Expression:
    if (result := typeConvertWidest(exprs[0].type, exprs[1].type, ctx, "mtl/builtins.py", line_number())) != None:
        return Expression(result, f"({exprs[0].value} {op} {exprs[1].value})")
    raise TranslationError(f"Failed to convert an expression of type {exprs[0].type.name} to type {exprs[1].type.name} for operator {op}.", "mtl/builtins.py", line_number())

def builtin_add(exprs: List[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "+")
def builtin_sub(exprs: List[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "-")
def builtin_mult(exprs: List[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "*")
def builtin_div(exprs: List[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "/")
def builtin_mod(exprs: List[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "%")
def builtin_exp(exprs: List[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "**")
def builtin_and(exprs: List[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "&&")
def builtin_or(exprs: List[Expression], ctx: TranslationContext) -> Expression: return builtin_binary(exprs, ctx, "||")
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