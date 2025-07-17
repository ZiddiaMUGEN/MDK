from typing import List
from inspect import currentframe

from mtl.utils import find, typeConvertWidest
from mtl.shared import TranslationContext, TypeDefinition, TypeCategory, TriggerDefinition, TriggerParameter, TriggerCategory, Expression, TemplateDefinition, TemplateCategory, TemplateParameter
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
        TriggerDefinition("Const", "numeric", None, [TriggerParameter("param_name", "string")], "mtl/builtins.py", line_number()),
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
        TriggerDefinition("GetHitVar", "numeric", None, [TriggerParameter("param_name", "string")], "mtl/builtins.py", line_number()),
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
        TriggerDefinition("log", "float", None, [TriggerParameter("exp1", "numeric")], "mtl/builtins.py", line_number()),
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
        TriggerDefinition("StageVar", "string", None, [TriggerParameter("param_name", "string")], "mtl/builtins.py", line_number()),
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

def getBaseTemplates() -> List[TemplateDefinition]:
    return [
        TemplateDefinition("AfterImage", [TemplateParameter("time", "int", False), TemplateParameter("length", "int", False), TemplateParameter("palcolor", "int", False), TemplateParameter("palinvertall", "bool", False), TemplateParameter("palbright", "color", False), TemplateParameter("palcontrast", "color", False), TemplateParameter("palpostbright", "color", False), TemplateParameter("paladd", "color", False), TemplateParameter("palmul", "color[float]", False), TemplateParameter("timegap", "int", False), TemplateParameter("framegap", "int", False), TemplateParameter("trans", "string", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("AfterImageTime", [TemplateParameter("time", "int", True)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("AngleAdd", [TemplateParameter("value", "float", True)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("AngleDraw", [TemplateParameter("value", "float", False), TemplateParameter("scale", "vector", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("AngleMul", [TemplateParameter("value", "float", True)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("AngleSet", [TemplateParameter("value", "float", True)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("AssertSpecial", [TemplateParameter("flag", "string", True), TemplateParameter("flag2", "string", False), TemplateParameter("flag3", "string", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("AttackDist", [TemplateParameter("value", "int", True)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("AttackMulSet", [TemplateParameter("value", "float", True)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("BindToParent", [TemplateParameter("time", "int", False), TemplateParameter("facing", "int", False), TemplateParameter("pos", "vector", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("BindToRoot", [TemplateParameter("time", "int", False), TemplateParameter("facing", "int", False), TemplateParameter("pos", "vector", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("BindToTarget", [TemplateParameter("time", "int", False), TemplateParameter("id", "int", False), TemplateParameter("pos", "vector[float, float, string]", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("ChangeAnim", [TemplateParameter("value", "anim", True), TemplateParameter("elem", "int", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("ChangeAnim2", [TemplateParameter("value", "anim", True), TemplateParameter("elem", "int", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("ChangeState", [TemplateParameter("value", "statedef", True), TemplateParameter("ctrl", "bool", False), TemplateParameter("anim", "int", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("ClearClipboard", [], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("CtrlSet", [TemplateParameter("ctrl", "bool", False), TemplateParameter("value", "bool", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("DefenceMulSet", [TemplateParameter("value", "float", True)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("DestroySelf", [], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("DisplayToClipboard", [TemplateParameter("text", "string", True), TemplateParameter("params", "vector", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("EnvColor", [TemplateParameter("value", "color", False), TemplateParameter("time", "int", False), TemplateParameter("under", "bool", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("EnvShake", [TemplateParameter("time", "int", True), TemplateParameter("freq", "float", False), TemplateParameter("ampl", "int", False), TemplateParameter("phase", "float", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("Explod", [TemplateParameter("anim", "anim", True), TemplateParameter("id", "int", False), TemplateParameter("pos", "vector[int]", False), TemplateParameter("postype", "string", False), TemplateParameter("facing", "int", False), TemplateParameter("vfacing", "int", False), TemplateParameter("bindtime", "int", False), TemplateParameter("vel", "vector", False), TemplateParameter("accel", "vector", False), TemplateParameter("random", "vector[int]", False), TemplateParameter("removetime", "int", False), TemplateParameter("supermove", "bool", False), TemplateParameter("supermovetime", "int", False), TemplateParameter("pausemovetime", "int", False), TemplateParameter("scale", "vector", False), TemplateParameter("sprpriority", "int", False), TemplateParameter("ontop", "bool", False), TemplateParameter("shadow", "color", False), TemplateParameter("ownpal", "bool", False), TemplateParameter("removeongethit", "bool", False), TemplateParameter("ignorehitpause", "bool", False), TemplateParameter("trans", "string", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("ExplodBindTime", [TemplateParameter("id", "int", False), TemplateParameter("time", "int", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("ForceFeedback", [TemplateParameter("waveform", "string", False), TemplateParameter("time", "int", False), TemplateParameter("freq", "vector[int, float]", False), TemplateParameter("ampl", "vector[int, float]", False), TemplateParameter("self", "bool", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("FallEnvShake", [], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("GameMakeAnim", [TemplateParameter("value", "anim", False), TemplateParameter("under", "bool", False), TemplateParameter("pos", "vector", False), TemplateParameter("random", "int", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("Gravity", [], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("Helper", [TemplateParameter("helpertype", "string", False), TemplateParameter("name", "string", False), TemplateParameter("id", "int", False), TemplateParameter("pos", "vector[int]", False), TemplateParameter("postype", "string", False), TemplateParameter("facing", "int", False), TemplateParameter("stateno", "statedef", False), TemplateParameter("keyctrl", "bool", False), TemplateParameter("ownpal", "bool", False), TemplateParameter("supermovetime", "int", False), TemplateParameter("pausemovetime", "int", False), TemplateParameter("size.xscale", "float", False), TemplateParameter("size.yscale", "float", False), TemplateParameter("size.ground.back", "int", False), TemplateParameter("size.ground.front", "int", False), TemplateParameter("size.air.back", "int", False), TemplateParameter("size.ait.front", "int", False), TemplateParameter("size.height", "int", False), TemplateParameter("size.proj.doscale", "int", False), TemplateParameter("size.head.pos", "vector[int]", False), TemplateParameter("size.mid.pos", "vector[int]", False), TemplateParameter("size.shadowoffset", "int", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("HitAdd", [TemplateParameter("value", "int", True)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("HitBy", [TemplateParameter("value", "string", False), TemplateParameter("value2", "string", False), TemplateParameter("time", "int", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("HitDef", [TemplateParameter("attr", "vector[string]", True), TemplateParameter("hitflag", "string", False), TemplateParameter("guardflag", "string", False), TemplateParameter("affectteam", "string", False), TemplateParameter("animtype", "string", False), TemplateParameter("air.animtype", "string", False), TemplateParameter("fall.animtype", "string", False), TemplateParameter("priority", "vector[int, string]", False), TemplateParameter("damage", "vector[int]", False), TemplateParameter("pausetime", "vector[int]", False), TemplateParameter("guard.pausetime", "vector[int]", False), TemplateParameter("sparkno", "anim", False), TemplateParameter("guard.sparkno", "anim", False), TemplateParameter("sparkxy", "vector[int]", False), TemplateParameter("hitsound", "sound", False), TemplateParameter("guardsound", "sound", False), TemplateParameter("ground.type", "string", False), TemplateParameter("air.type", "string", False), TemplateParameter("ground.slidetime", "int", False), TemplateParameter("guard.slidetime", "int", False), TemplateParameter("ground.hittime", "int", False), TemplateParameter("guard.hittime", "int", False), TemplateParameter("air.hittime", "int", False), TemplateParameter("guard.ctrltime", "int", False), TemplateParameter("guard.dist", "int", False), TemplateParameter("yaccel", "float", False), TemplateParameter("ground.velocity", "vector", False), TemplateParameter("guard.velocity", "float", False), TemplateParameter("air.velocity", "vector", False), TemplateParameter("airguard.velocity", "vector", False), TemplateParameter("ground.cornerpush.veloff", "float", False), TemplateParameter("air.cornerpush.veloff", "float", False), TemplateParameter("down.cornerpush.veloff", "float", False), TemplateParameter("guard.cornerpush.veloff", "float", False), TemplateParameter("airguard.cornerpush.veloff", "float", False), TemplateParameter("airguard.ctrltime", "int", False), TemplateParameter("air.juggle", "int", False), TemplateParameter("mindist", "vector[int]", False), TemplateParameter("maxdist", "vector[int]", False), TemplateParameter("snap", "vector[int]", False), TemplateParameter("p1sprpriority", "int", False), TemplateParameter("p2sprpriority", "int", False), TemplateParameter("p1facing", "int", False), TemplateParameter("p1getp2facing", "int", False), TemplateParameter("p2facing", "int", False), TemplateParameter("p1stateno", "statedef", False), TemplateParameter("p2stateno", "statedef", False), TemplateParameter("p2getp1state", "bool", False), TemplateParameter("forcestand", "bool", False), TemplateParameter("fall", "bool", False), TemplateParameter("fall.xvelocity", "float", False), TemplateParameter("fall.yvelocity", "float", False), TemplateParameter("fall.recover", "bool", False), TemplateParameter("fall.recovertime", "int", False), TemplateParameter("fall.damage", "int", False), TemplateParameter("air.fall", "bool", False), TemplateParameter("forcenofall", "bool", False), TemplateParameter("down.velocity", "vector", False), TemplateParameter("down.hittime", "int", False), TemplateParameter("down.bounce", "bool", False), TemplateParameter("id", "int", False), TemplateParameter("chainid", "int", False), TemplateParameter("nochainid", "vector[int]", False), TemplateParameter("hitonce", "bool", False), TemplateParameter("kill", "bool", False), TemplateParameter("guard.kill", "bool", False), TemplateParameter("fall.kill", "bool", False), TemplateParameter("numhits", "int", False), TemplateParameter("getpower", "vector[int]", False), TemplateParameter("givepower", "vector[int]", False), TemplateParameter("palfx.time", "int", False), TemplateParameter("palfx.mul", "vector[int]", False), TemplateParameter("palfx.add", "vector[int]", False), TemplateParameter("envshake.time", "int", False), TemplateParameter("envshake.freq", "float", False), TemplateParameter("envshake.ampl", "int", False), TemplateParameter("envshake.phase", "float", False), TemplateParameter("fall.envshake.time", "int", False), TemplateParameter("fall.envshake.freq", "float", False), TemplateParameter("fall.envshake.ampl", "int", False), TemplateParameter("fall.envshake.phase", "float", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("HitFallDamage", [], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("HitFallSet", [TemplateParameter("value", "int", False), TemplateParameter("xvel", "float", False), TemplateParameter("yvel", "float", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("HitFallVel", [], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("HitOverride", [TemplateParameter("attr", "string", True), TemplateParameter("stateno", "statedef", True), TemplateParameter("slot", "int", False), TemplateParameter("time", "int", False), TemplateParameter("forceair", "bool", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("HitVelSet", [TemplateParameter("x", "bool", False), TemplateParameter("y", "bool", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("LifeAdd", [TemplateParameter("value", "int", True), TemplateParameter("kill", "bool", False), TemplateParameter("absolute", "bool", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("LifeSet", [TemplateParameter("value", "int", True)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("MakeDust", [TemplateParameter("pos", "vector[int]", False), TemplateParameter("pos2", "vector[int]", False), TemplateParameter("spacing", "int", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("ModifyExplod", [TemplateParameter("id", "int", True), TemplateParameter("anim", "anim", False), TemplateParameter("pos", "vector[int]", False), TemplateParameter("postype", "string", False), TemplateParameter("facing", "int", False), TemplateParameter("vfacing", "int", False), TemplateParameter("bindtime", "int", False), TemplateParameter("vel", "vector", False), TemplateParameter("accel", "vector", False), TemplateParameter("random", "vector[int]", False), TemplateParameter("removetime", "int", False), TemplateParameter("supermove", "bool", False), TemplateParameter("supermovetime", "int", False), TemplateParameter("pausemovetime", "int", False), TemplateParameter("scale", "vector", False), TemplateParameter("sprpriority", "int", False), TemplateParameter("ontop", "bool", False), TemplateParameter("shadow", "color", False), TemplateParameter("ownpal", "bool", False), TemplateParameter("removeongethit", "bool", False), TemplateParameter("ignorehitpause", "bool", False), TemplateParameter("trans", "string", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("MoveHitReset", [], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("NotHitBy", [TemplateParameter("value", "string", False), TemplateParameter("value2", "string", False), TemplateParameter("time", "int", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("Null", [], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("Offset", [TemplateParameter("x", "float", False), TemplateParameter("y", "float", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("PalFX", [TemplateParameter("time", "int", False), TemplateParameter("add", "color", False), TemplateParameter("mul", "color", False), TemplateParameter("sinadd", "vector[int]", False), TemplateParameter("invertall", "bool", False), TemplateParameter("color", "int", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("ParentVarAdd", [TemplateParameter("v", "int", True), TemplateParameter("fv", "int", True), TemplateParameter("sv", "int", True), TemplateParameter("sfv", "int", True), TemplateParameter("value", "float", True)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("ParentVarSet", [TemplateParameter("v", "int", True), TemplateParameter("fv", "int", True), TemplateParameter("sv", "int", True), TemplateParameter("sfv", "int", True), TemplateParameter("value", "float", True)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("Pause", [TemplateParameter("time", "int", True), TemplateParameter("endcmdbuftime", "int", False), TemplateParameter("movetime", "int", False), TemplateParameter("pausebg", "bool", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("PlayerPush", [TemplateParameter("value", "bool", True)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("PlaySnd", [TemplateParameter("value", "sound", True), TemplateParameter("volumescale", "float", False), TemplateParameter("channel", "int", False), TemplateParameter("lowpriority", "bool", False), TemplateParameter("freqmul", "float", False), TemplateParameter("loop", "bool", False), TemplateParameter("pan", "int", False), TemplateParameter("abspan", "int", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("PosAdd", [TemplateParameter("x", "float", False), TemplateParameter("y", "float", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("PosFreeze", [TemplateParameter("value", "bool", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("PosSet", [TemplateParameter("x", "float", False), TemplateParameter("y", "float", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("PowerAdd", [TemplateParameter("value", "int", True)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("PowerSet", [TemplateParameter("value", "int", True)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("Projectile", [TemplateParameter("projid", "int", False), TemplateParameter("projanim", "anim", False), TemplateParameter("projhitanim", "anim", False), TemplateParameter("projremanim", "anim", False), TemplateParameter("projscale", "vector", False), TemplateParameter("projremove", "bool", False), TemplateParameter("projremovetime", "int", False), TemplateParameter("velocity", "vector", False), TemplateParameter("remvelocity", "vector", False), TemplateParameter("accel", "vector", False), TemplateParameter("velmul", "vector", False), TemplateParameter("projhits", "int", False), TemplateParameter("projmisstime", "int", False), TemplateParameter("projpriority", "int", False), TemplateParameter("projsprpriority", "int", False), TemplateParameter("projedgebound", "int", False), TemplateParameter("projstagebound", "int", False), TemplateParameter("projheightbound", "vector[int]", False), TemplateParameter("offset", "vector[int]", False), TemplateParameter("postype", "string", False), TemplateParameter("projshadow", "color", False), TemplateParameter("supermovetime", "int", False), TemplateParameter("pausemovetime", "int", False), TemplateParameter("afterimage.time", "int", False), TemplateParameter("afterimage.length", "int", False), TemplateParameter("afterimage.palcolor", "int", False), TemplateParameter("afterimage.palinvertall", "bool", False), TemplateParameter("afterimage.palbright", "color", False), TemplateParameter("afterimage.palcontrast", "color", False), TemplateParameter("afterimage.palpostbright", "color", False), TemplateParameter("afterimage.paladd", "color", False), TemplateParameter("afterimage.palmul", "color[float]", False), TemplateParameter("afterimage.timegap", "int", False), TemplateParameter("afterimage.framegap", "int", False), TemplateParameter("afterimage.trans", "string", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("RemapPal", [TemplateParameter("source", "vector[int]", True), TemplateParameter("dest", "vector[int]", True)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("RemoveExplod", [TemplateParameter("id", "int", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("ReversalDef", [TemplateParameter("reversal.attr", "string", True), TemplateParameter("pausetime", "vector[int]", False), TemplateParameter("sparkno", "anim", False), TemplateParameter("hitsound", "sound", False), TemplateParameter("p1stateno", "statedef", False), TemplateParameter("p2stateno", "statedef", False), TemplateParameter("p1sprpriority", "int", False), TemplateParameter("p2sprpriority", "int", False), TemplateParameter("sparkxy", "vector[int]", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("ScreenBound", [TemplateParameter("value", "bool", False), TemplateParameter("movecamera", "vector[bool]", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("SelfState", [TemplateParameter("value", "statedef", True), TemplateParameter("ctrl", "bool", False), TemplateParameter("anim", "int", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("SprPriority", [TemplateParameter("value", "int", True)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("StateTypeSet", [TemplateParameter("statetype", "string", False), TemplateParameter("movetype", "string", False), TemplateParameter("physics", "string", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("SndPan", [TemplateParameter("channel", "int", True), TemplateParameter("pan", "int", True), TemplateParameter("abspan", "int", True)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("StopSnd", [TemplateParameter("channel", "int", True)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("SuperPause", [TemplateParameter("time", "int", False), TemplateParameter("anim", "anim", False), TemplateParameter("sound", "sound", False), TemplateParameter("pos", "vector", False), TemplateParameter("darken", "bool", False), TemplateParameter("p2defmul", "float", False), TemplateParameter("poweradd", "int", False), TemplateParameter("unhittable", "bool", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("TargetBind", [TemplateParameter("time", "int", False), TemplateParameter("id", "int", False), TemplateParameter("pos", "vector", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("TargetDrop", [TemplateParameter("excludeid", "int", False), TemplateParameter("keepone", "bool", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("TargetFacing", [TemplateParameter("value", "int", True), TemplateParameter("id", "int", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("TargetLifeAdd", [TemplateParameter("value", "int", True), TemplateParameter("id", "int", False), TemplateParameter("kill", "bool", False), TemplateParameter("absolute", "bool", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("TargetPowerAdd", [TemplateParameter("value", "int", True), TemplateParameter("id", "int", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("TargetState", [TemplateParameter("value", "int", True), TemplateParameter("id", "int", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("TargetVelAdd", [TemplateParameter("x", "float", False), TemplateParameter("y", "float", False), TemplateParameter("id", "int", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("TargetVelSet", [TemplateParameter("x", "float", False), TemplateParameter("y", "float", False), TemplateParameter("id", "int", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("Trans", [TemplateParameter("trans", "string", True), TemplateParameter("alpha", "vector[int]", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("Turn", [], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("VarAdd", [TemplateParameter("v", "int", True), TemplateParameter("fv", "int", True), TemplateParameter("sv", "int", True), TemplateParameter("sfv", "int", True), TemplateParameter("value", "float", True)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("VarSet", [TemplateParameter("v", "int", True), TemplateParameter("fv", "int", True), TemplateParameter("sv", "int", True), TemplateParameter("sfv", "int", True), TemplateParameter("value", "float", True)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("VarRandom", [TemplateParameter("v", "int", True), TemplateParameter("range", "vector[int]", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("VarRangeSet", [TemplateParameter("value", "int", True), TemplateParameter("fvalue", "float", True), TemplateParameter("first", "int", False), TemplateParameter("last", "int", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("VelAdd", [TemplateParameter("x", "float", False), TemplateParameter("y", "float", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("VelMul", [TemplateParameter("x", "float", False), TemplateParameter("y", "float", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("VelSet", [TemplateParameter("x", "float", False), TemplateParameter("y", "float", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("VictoryQuote", [TemplateParameter("value", "int", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN),
        TemplateDefinition("Width", [TemplateParameter("edge", "vector[int]", False), TemplateParameter("player", "vector[int]", False), TemplateParameter("value", "vector[int]", False)], [], [], "mtl/builtins.py", line_number(), TemplateCategory.BUILTIN)
    ]