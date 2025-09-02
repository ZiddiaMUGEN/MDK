from typing import Callable
from mdk.types.expressions import Expression
from mdk.types.specifier import TypeSpecifier
from mdk.types.builtins import IntType, BoolType, FloatType, UStringType, StringType, AnyType
from mdk.types.defined import HitStringType
import mdk.types.defined as defined

from mdk.utils.shared import convert
from mdk.utils.expressions import check_types_assignable

## helper function to take 1 argument and the types involved and produce an output.
def TriggerExpression(name: str, inputs: list[TypeSpecifier], output: TypeSpecifier) -> Callable[..., Expression]:
    def _callable(*args) -> Expression:
        if len(args) != len(inputs):
            raise Exception(f"Trigger expression {name} expected {len(inputs)} inputs, but got {len(args)} instead.")
        conv_args: list[Expression] = []
        for index in range(len(args)):
            next_arg = convert(args[index])
            if not isinstance(next_arg, Expression):
                raise Exception(f"Inputs to trigger expressions should always be Expressions, not {type(args[index])}.")
            if next_arg.type in [UStringType, StringType] and inputs[index] in [UStringType, StringType]:
                ## UString and String are considered matching.
                next_arg.type = UStringType
            elif next_arg.type == IntType and inputs[index] == FloatType:
                next_arg.type = FloatType
            elif next_arg.type != inputs[index]:
                raise Exception(f"Trigger expression {name} expected input at index {index + 1} to have type {inputs[index].name}, not {next_arg.type.name}")
            conv_args.append(next_arg)
        return Expression(f"{name}({', '.join([str(arg) for arg in conv_args])})", output)
    return _callable

## helper function to take an optional argument and the types involved and produce an output.
def TriggerExpressionWithOptional(name: str, inputs: list[TypeSpecifier], output: TypeSpecifier) -> Callable[..., Expression]:
    def _callable(*args) -> Expression:
        if len(args) == 0:
            return Expression(f"{name}", output)
        if len(args) != len(inputs):
            raise Exception(f"Trigger expression {name} expected {len(inputs)} or 0 inputs, but got {len(args)} instead.")
        conv_args: list[Expression] = []
        for index in range(len(args)):
            next_arg = convert(args[index])
            if not isinstance(next_arg, Expression):
                raise Exception(f"Inputs to trigger expressions should always be Expressions, not {type(args[index])}.")
            if next_arg.type in [UStringType, StringType] and inputs[index] in [UStringType, StringType]:
                ## UString and String are considered matching.
                next_arg.type = UStringType
            elif next_arg.type != inputs[index]:
                raise Exception(f"Trigger expression {name} expected input at index {index + 1} to have type {inputs[index].name}, not {next_arg.type.name}")
            conv_args.append(next_arg)
        return Expression(f"{name}({', '.join([str(arg) for arg in conv_args])})", output)
    return _callable

## helper function for cond/ifelse specifically.
def TriggerExpressionCond(name: str) -> Callable[..., Expression]:
    def _callable(*args) -> Expression:
        if len(args) != 3:
            raise Exception(f"Trigger expression {name} requires 3 inputs, but got {len(args)} instead.")
        conv_args: list[Expression] = []
        for index in range(len(args)):
            next_arg = convert(args[index])
            if not isinstance(next_arg, Expression):
                raise Exception(f"Inputs to trigger expressions should always be Expressions, not {type(args[index])}.")
            conv_args.append(next_arg)
        if conv_args[0].type != BoolType:
            raise Exception(f"First argument to Cond or ifelse must be a bool, not {conv_args[0].type.name}.")
        if (output := check_types_assignable(conv_args[1].type, conv_args[2].type)) == None:
            raise Exception(f"Second and third arguments to Cond or ifelse must have assignable types; got {conv_args[1].type.name} and {conv_args[2].type.name}.")
        return Expression(f"{name}({', '.join([str(arg) for arg in conv_args])})", output)
    return _callable

## this is used for built-in position/velocity structures (e.g. Vel, Pos)
## it avoids the need for custom structure types, which are still not
## fully implemented either here or in MTL.
class PositionExpression:
    x: Expression
    y: Expression
    _name: str
    def __init__(self, name: str, type: TypeSpecifier):
        self._name = name
        self.x = Expression(f"{name} X", type)
        self.y = Expression(f"{name} Y", type)

Abs = TriggerExpression("abs", [FloatType], FloatType)
Acos = TriggerExpression("acos", [FloatType], FloatType)
AiLevel = Expression("AiLevel", IntType)
Alive = Expression("Alive", BoolType)
Anim = Expression("Anim", IntType)
## AnimElem
AnimElemNo = TriggerExpression("AnimElemNo", [IntType], IntType)
AnimElemTime = TriggerExpression("AnimElemTime", [IntType], IntType)
AnimExist = TriggerExpression("AnimExist", [IntType], BoolType)
AnimTime = Expression("AnimTime", IntType)
Asin = TriggerExpression("asin", [FloatType], FloatType)
Atan = TriggerExpression("atan", [FloatType], FloatType)
AuthorName = Expression("AuthorName", UStringType)
BackEdgeBodyDist = Expression("BackEdgeBodyDist", FloatType)
BackEdgeDist = Expression("BackEdgeDist", FloatType)
CanRecover = Expression("CanRecover", BoolType)
Ceil = TriggerExpression("ceil", [FloatType], IntType)
Command = Expression("Command", UStringType)
Cond = TriggerExpressionCond("Cond")
Const = TriggerExpression("Const", [UStringType], FloatType)
Const240p = TriggerExpression("Const240p", [FloatType], FloatType)
Const480p = TriggerExpression("Const480p", [FloatType], FloatType)
Const720p = TriggerExpression("Const720p", [FloatType], FloatType)
Cos = TriggerExpression("cos", [FloatType], FloatType)
Ctrl = Expression("Ctrl", BoolType)
DrawGame = Expression("DrawGame", BoolType)
E = Expression("E", FloatType)
Exp = TriggerExpression("exp", [FloatType], FloatType)
Facing = Expression("Facing", IntType)
Floor = TriggerExpression("floor", [FloatType], IntType)
FrontEdgeBodyDist = Expression("FrontEdgeBodyDist", FloatType)
FrontEdgeDist = Expression("FrontEdgeDist", FloatType)
## fvar
GameHeight = Expression("GameHeight", FloatType)
GameTime = Expression("GameTime", IntType)
GameWidth = Expression("GameWidth", IntType)
GetHitVar = TriggerExpression("GetHitVar", [UStringType], FloatType)
HitCount = Expression("HitCount", IntType)
HitDefAttr = Expression("HitDefAttr", HitStringType)
HitFall = Expression("HitFall", BoolType)
HitOver = Expression("HitOver", BoolType)
HitPauseTime = Expression("HitPauseTime", IntType)
HitShakeOver = Expression("HitShakeOver", BoolType)
HitVel = PositionExpression("HitVel", FloatType)
ID = Expression("ID", IntType)
ifelse = TriggerExpressionCond("ifelse")
InGuardDist = Expression("InGuardDist", BoolType)
IsHelper = TriggerExpressionWithOptional("IsHelper", [IntType], BoolType)
IsHomeTeam = Expression("IsHomeTeam", BoolType)
Life = Expression("Life", IntType)
LifeMax = Expression("LifeMax", IntType)
Ln = TriggerExpression("ln", [FloatType], FloatType)
Log = TriggerExpression("log", [FloatType], FloatType)
Lose = Expression("Lose", BoolType)
MatchNo = Expression("MatchNo", IntType)
MatchOver = Expression("MatchOver", BoolType)
MoveContact = Expression("MoveContact", IntType)
MoveGuarded = Expression("MoveGuarded", IntType)
MoveHit = Expression("MoveHit", IntType)
MoveType = Expression("MoveType", defined.MoveTypeT)
MoveReversed = Expression("MoveReversed", IntType)
Name = Expression("Name", UStringType)
NumEnemy = Expression("NumEnemy", IntType)
NumExplod = TriggerExpressionWithOptional("NumExplod", [IntType], IntType)
NumHelper = TriggerExpressionWithOptional("NumHelper", [IntType], IntType)
NumPartner = Expression("NumPartner", IntType)
NumProj = Expression("NumProj", IntType)
NumProjID = TriggerExpression("NumProjID", [IntType], IntType)
NumTarget = TriggerExpressionWithOptional("NumTarget", [IntType], IntType)
P1Name = Expression("P1Name", UStringType)
P2BodyDist = PositionExpression("P2BodyDist", FloatType)
P2Dist = PositionExpression("P2Dist", FloatType)
P2Life = Expression("P2Life", IntType)
P2MoveType = Expression("P2MoveType", defined.MoveTypeT)
P2StateNo = Expression("P2StateNo", IntType)
P2StateType = Expression("P2StateType", defined.StateTypeT)
P2Name = Expression("P2Name", UStringType)
P3Name = Expression("P3Name", UStringType)
P4Name = Expression("P4Name", UStringType)
PalNo = Expression("PalNo", IntType)
ParentDist = PositionExpression("ParentDist", FloatType)
Pi = Expression("pi", IntType)
Pos = PositionExpression("Pos", FloatType)
Power = Expression("Power", IntType)
PowerMax = Expression("PowerMax", IntType)
PlayerIDExist = TriggerExpression("PlayerIDExist", [IntType], IntType)
PrevStateNo = Expression("PrevStateNo", IntType)
ProjCancelTime = TriggerExpression("ProjCancelTime", [IntType], IntType)
ProjContactTime = TriggerExpression("ProjContactTime", [IntType], IntType)
ProjGuardedTime = TriggerExpression("ProjGuardedTime", [IntType], IntType)
ProjHitTime = TriggerExpression("ProjHitTime", [IntType], IntType)
Random = Expression("Random", IntType)
RootDist = PositionExpression("RootDist", FloatType)
RoundNo = Expression("RoundNo", IntType)
RoundsExisted = Expression("RoundsExisted", IntType)
RoundState = Expression("RoundState", IntType)
ScreenPos = PositionExpression("ScreenPos", FloatType)
SelfAnimExist = TriggerExpression("SelfAnimExist", [IntType], BoolType)
Sin = TriggerExpression("sin", [FloatType], FloatType)
StateNo = Expression("StateNo", IntType)
StateType = Expression("StateType", defined.StateTypeT)
StageVar = TriggerExpression("StageVar", [UStringType], UStringType)
## sysfvar
## sysvar
Tan = TriggerExpression("tan", [FloatType], FloatType)
TeamMode = Expression("TeamMode", defined.TeamModeTypeT)
TeamSide = Expression("TeamSide", IntType)
TicksPerSecond = Expression("TicksPerSecond", IntType)
Time = Expression("Time", IntType)
## TimeMod
## UniqHitCount
## var
Vel = PositionExpression("Vel", FloatType)
Win = Expression("Win", BoolType)
WinKO = Expression("WinKO", BoolType)
WinTime = Expression("WinTime", BoolType)
WinPerfect = Expression("WinPerfect", BoolType)

EmptyExpression = Expression("", AnyType)
EmptyTuple = (EmptyExpression, )

__all__ = [
    "Abs", "Acos", "AiLevel", "Alive", "Anim", "AnimElemNo", "AnimElemTime", "AnimExist", "AnimTime", "Asin", "Atan",
    "AuthorName", "BackEdgeBodyDist", "BackEdgeDist", "CanRecover", "Ceil", "Command", "Const", "Const240p", "Const480p",
    "Const720p", "Cos", "Ctrl", "DrawGame", "E", "Exp", "Facing", "Floor", "FrontEdgeBodyDist", "FrontEdgeDist", "GameHeight",
    "GameTime", "GameWidth", "GetHitVar", "HitCount", "HitFall", "HitOver", "HitPauseTime", "HitShakeOver", "ID", "InGuardDist",
    "IsHelper", "IsHomeTeam", "Life", "LifeMax", "Ln", "Log", "Lose", "MatchNo", "MatchOver", "MoveContact", "MoveGuarded",
    "MoveHit", "MoveReversed", "Name", "NumEnemy", "NumExplod", "NumHelper", "NumPartner", "NumProj", "NumProjID", "NumTarget",
    "P1Name", "P2Life", "P2StateNo", "P2Name", "P3Name", "P4Name", "PalNo", "Pi", "Power", "PowerMax", "PlayerIDExist",
    "ProjCancelTime", "ProjContactTime", "ProjGuardedTime", "ProjHitTime", "Random", "RoundNo", "RoundsExisted", "RoundState",
    "SelfAnimExist", "Sin", "StateNo", "StageVar", "Tan", "TeamSide", "TicksPerSecond", "Time", "Win", "WinKO", "WinTime", "WinPerfect",
    "HitDefAttr", "StateType", "MoveType", "TeamMode", "P2MoveType", "P2StateType",
    "HitVel", "P2BodyDist", "P2Dist", "ParentDist", "Pos", "RootDist", "ScreenPos", "Vel",
    "ifelse", "Cond", "EmptyExpression", "EmptyTuple"
]