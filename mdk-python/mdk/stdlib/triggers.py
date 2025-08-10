from typing import Callable
from mdk.types.context import Expression
from mdk.types.specifier import TypeSpecifier, IntType, BoolType, FloatType, StringType

## helper function to take 1 argument and the types involved and produce an output.
def TriggerExpression(name: str, inputs: list[TypeSpecifier], output: TypeSpecifier) -> Callable:
    def _callable(*args) -> Expression:
        if len(args) != len(inputs):
            raise Exception(f"Trigger expression {name} expected {len(inputs)} inputs, but got {len(args)} instead.")
        for index in range(len(args)):
            if not isinstance(args[index], Expression):
                raise Exception(f"Inputs to trigger expressions should always be Expressions, not {type(args[index])}.")
            if args[index].type != inputs[index]:
                raise Exception(f"Trigger expression {name} expected input at index {index + 1} to have type {inputs[index].name}, not {args[index].type.name}")
        return Expression(f"{name}({', '.join([str(arg) for arg in args])})", output)
    return _callable

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
AuthorName = Expression("AuthorName", StringType)
BackEdgeBodyDist = Expression("BackEdgeBodyDist", FloatType)
BackEdgeDist = Expression("BackEdgeDist", FloatType)
CanRecover = Expression("CanRecover", BoolType)
Ceil = TriggerExpression("ceil", [FloatType], IntType)
Command = Expression("Command", StringType)
## Cond
Const = TriggerExpression("Const", [StringType], FloatType)
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
GetHitVar = TriggerExpression("GetHitVar", [StringType], FloatType)
HitCount = Expression("HitCount", IntType)
## HitDefAttr
HitFall = Expression("HitFall", BoolType)
HitOver = Expression("HitOver", BoolType)
HitPauseTime = Expression("HitPauseTime", IntType)
HitShakeOver = Expression("HitShakeOver", BoolType)
## HitVel
ID = Expression("ID", IntType)
## ifelse
InGuardDist = Expression("InGuardDist", BoolType)
IsHelper = TriggerExpression("IsHelper", [IntType], BoolType)
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
## MoveType
MoveReversed = Expression("MoveReversed", IntType)
Name = Expression("Name", StringType)
NumEnemy = Expression("NumEnemy", IntType)
NumExplod = TriggerExpression("NumExplod", [IntType], IntType)
NumHelper = TriggerExpression("NumHelper", [IntType], IntType)
NumPartner = Expression("NumPartner", IntType)
NumProj = Expression("NumProj", IntType)
NumProjID = TriggerExpression("NumProjID", [IntType], IntType)
NumTarget = TriggerExpression("NumTarget", [IntType], IntType)
P1Name = Expression("P1Name", StringType)
## P2BodyDist
## P2Dist
P2Life = Expression("P2Life", IntType)
## P2MoveType
P2StateNo = Expression("P2StateNo", IntType)
## P2StateType
P2Name = Expression("P2Name", StringType)
P3Name = Expression("P3Name", StringType)
P4Name = Expression("P4Name", StringType)
PalNo = Expression("PalNo", IntType)
## ParentDist
Pi = Expression("pi", IntType)
## Pos
Power = Expression("Power", IntType)
PowerMax = Expression("PowerMax", IntType)
PlayerIDExist = TriggerExpression("PlayerIDExist", [IntType], IntType)
PrevStateNo = Expression("PrevStateNo", IntType)
ProjCancelTime = TriggerExpression("ProjCancelTime", [IntType], IntType)
ProjContactTime = TriggerExpression("ProjContactTime", [IntType], IntType)
ProjGuardedTime = TriggerExpression("ProjGuardedTime", [IntType], IntType)
ProjHitTime = TriggerExpression("ProjHitTime", [IntType], IntType)
Random = Expression("Random", IntType)
## RootDist
RoundNo = Expression("RoundNo", IntType)
RoundsExisted = Expression("RoundsExisted", IntType)
RoundState = Expression("RoundState", IntType)
## ScreenPos
SelfAnimExist = TriggerExpression("SelfAnimExist", [IntType], BoolType)
Sin = TriggerExpression("sin", [FloatType], FloatType)
StateNo = Expression("StateNo", IntType)
## StateType
StageVar = TriggerExpression("StageVar", [StringType], StringType)
## sysfvar
## sysvar
Tan = TriggerExpression("tan", [FloatType], FloatType)
## TeamMode
TeamSide = Expression("TeamSide", IntType)
TicksPerSecond = Expression("TicksPerSecond", IntType)
Time = Expression("Time", IntType)
## TimeMod
## UniqHitCount
## var
## Vel
Win = Expression("Win", BoolType)
WinKO = Expression("WinKO", BoolType)
WinTime = Expression("WinTime", BoolType)
WinPerfect = Expression("WinPerfect", BoolType)