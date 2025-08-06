from typing import Callable, Optional, Protocol
from mdk.types.context import Expression, IntExpression, FloatExpression, BoolExpression, StringExpression, IntVar, FloatVar, BoolVar

## use for a trigger function that accepts 1 argument of int/float, and produces the same type as output.
def TriggerExpression_Numeric_Numeric(name: str) -> Callable[[Expression], Expression]:
    def _numeric(exprn: Expression) -> Expression:
        if isinstance(exprn, FloatExpression) or isinstance(exprn, FloatVar):
            return FloatExpression(f"{name}({exprn.exprn})")
        if isinstance(exprn, IntExpression) or isinstance(exprn, IntVar):
            return IntExpression(f"{name}({exprn.exprn})")
        raise Exception(f"Argument to trigger {name} should be Int or Float, not {type(exprn)}.")
    return _numeric

## use for a trigger function that accepts 1 argument of int/float, and produces a float as output.
def TriggerExpression_Numeric_Float(name: str) -> Callable[[Expression], FloatExpression]:
    def _numeric(exprn: Expression) -> FloatExpression:
        if isinstance(exprn, FloatExpression) or isinstance(exprn, FloatVar) or isinstance(exprn, IntExpression) or isinstance(exprn, IntVar):
            return FloatExpression(f"{name}({exprn.exprn})")
        raise Exception(f"Argument to trigger {name} should be Int or Float, not {type(exprn)}.")
    return _numeric

## use for a trigger function that accepts 1 argument of int, and produces a int as output.
def TriggerExpression_Int_Int(name: str) -> Callable[[IntExpression], IntExpression]:
    def _numeric(exprn: IntExpression) -> IntExpression:
        if isinstance(exprn, IntExpression) or isinstance(exprn, IntVar):
            return IntExpression(f"{name}({exprn.exprn})")
        raise Exception(f"Argument to trigger {name} should be Int, not {type(exprn)}.")
    return _numeric

## use for a trigger function that accepts 1 argument of float, and produces a int as output.
def TriggerExpression_Float_Int(name: str) -> Callable[[FloatExpression], IntExpression]:
    def _numeric(exprn: FloatExpression) -> IntExpression:
        if isinstance(exprn, FloatExpression) or isinstance(exprn, FloatVar):
            return IntExpression(f"{name}({exprn.exprn})")
        raise Exception(f"Argument to trigger {name} should be Float, not {type(exprn)}.")
    return _numeric

## use for a trigger function that accepts 1 argument of int, and produces a bool as output.
def TriggerExpression_Int_Bool(name: str) -> Callable[[IntExpression], IntExpression]:
    def _numeric(exprn: IntExpression) -> IntExpression:
        if isinstance(exprn, IntExpression) or isinstance(exprn, IntVar):
            return IntExpression(f"{name}({exprn.exprn})")
        raise Exception(f"Argument to trigger {name} should be Int, not {type(exprn)}.")
    return _numeric

## use for a trigger function that accepts 1 argument of string, and produces a float as output.
def TriggerExpression_String_Float(name: str) -> Callable[[StringExpression], FloatExpression]:
    def _numeric(exprn: StringExpression) -> FloatExpression:
        if isinstance(exprn, StringExpression):
            return FloatExpression(f"{name}({exprn.exprn})")
        raise Exception(f"Argument to trigger {name} should be String, not {type(exprn)}.")
    return _numeric

def TriggerExpression_String_String(name: str) -> Callable[[StringExpression], StringExpression]:
    def _numeric(exprn: StringExpression) -> StringExpression:
        if isinstance(exprn, StringExpression):
            return StringExpression(f"{name}({exprn.exprn})")
        raise Exception(f"Argument to trigger {name} should be String, not {type(exprn)}.")
    return _numeric

class MaybeInt_Bool(Protocol):
    def __call__(self, x: IntExpression = ..., /) -> BoolExpression:
        ...

def TriggerExpression_MaybeInt_Bool(name: str) -> MaybeInt_Bool:
    def _numeric(exprn: Optional[IntExpression] = None) -> BoolExpression:
        if exprn == None:
            return BoolExpression(f"{name}")
        if isinstance(exprn, IntExpression):
            return BoolExpression(f"{name}({exprn.exprn})")
        raise Exception(f"Argument to trigger {name} should be Int, not {type(exprn)}.")
    return _numeric

class MaybeInt_Int(Protocol):
    def __call__(self, x: IntExpression = ..., /) -> IntExpression:
        ...

def TriggerExpression_MaybeInt_Int(name: str) -> MaybeInt_Int:
    def _numeric(exprn: Optional[IntExpression] = None) -> IntExpression:
        if exprn == None:
            return IntExpression(f"{name}")
        if isinstance(exprn, IntExpression):
            return IntExpression(f"{name}({exprn.exprn})")
        raise Exception(f"Argument to trigger {name} should be Int, not {type(exprn)}.")
    return _numeric

Abs = TriggerExpression_Numeric_Numeric("abs")
Acos = TriggerExpression_Numeric_Float("acos")
AiLevel = IntExpression("AiLevel")
Alive = BoolExpression("Alive")
Anim = IntExpression("Anim")
## AnimElem
AnimElemNo = TriggerExpression_Int_Int("AnimElemNo")
AnimElemTime = TriggerExpression_Int_Int("AnimElemTime")
AnimExist = TriggerExpression_Int_Bool("AnimExist")
AnimTime = IntExpression("AnimTime")
Asin = TriggerExpression_Numeric_Float("asin")
Atan = TriggerExpression_Numeric_Float("atan")
AuthorName = StringExpression("AuthorName")
BackEdgeBodyDist = FloatExpression("BackEdgeBodyDist")
BackEdgeDist = FloatExpression("BackEdgeDist")
CanRecover = BoolExpression("CanRecover")
Ceil = TriggerExpression_Float_Int("ceil")
Command = StringExpression("Command")
## Cond
Const = TriggerExpression_String_Float("Const")
Const240p = TriggerExpression_Numeric_Float("Const240p")
Const480p = TriggerExpression_Numeric_Float("Const480p")
Const720p = TriggerExpression_Numeric_Float("Const720p")
Cos = TriggerExpression_Numeric_Float("cos")
Ctrl = BoolExpression("Ctrl")
DrawGame = BoolExpression("DrawGame")
E = FloatExpression("E")
Exp = TriggerExpression_Numeric_Float("exp")
Facing = IntExpression("Facing")
Floor = TriggerExpression_Float_Int("floor")
FrontEdgeBodyDist = FloatExpression("FrontEdgeBodyDist")
FrontEdgeDist = FloatExpression("FrontEdgeDist")
## fvar
GameHeight = FloatExpression("GameHeight")
GameTime = IntExpression("GameTime")
GameWidth = IntExpression("GameWidth")
GetHitVar = TriggerExpression_String_Float("GetHitVar")
HitCount = IntExpression("HitCount")
## HitDefAttr
HitFall = BoolExpression("HitFall")
HitOver = BoolExpression("HitOver")
HitPauseTime = IntExpression("HitPauseTime")
HitShakeOver = BoolExpression("HitShakeOver")
## HitVel
ID = IntExpression("ID")
## ifelse
InGuardDist = BoolExpression("InGuardDist")
IsHelper = TriggerExpression_MaybeInt_Bool("IsHelper")
IsHomeTeam = BoolExpression("IsHomeTeam")
Life = IntExpression("Life")
LifeMax = IntExpression("LifeMax")
Ln = TriggerExpression_Numeric_Float("ln")
Log = TriggerExpression_Numeric_Float("log")
Lose = BoolExpression("Lose")
MatchNo = IntExpression("MatchNo")
MatchOver = BoolExpression("MatchOver")
MoveContact = IntExpression("MoveContact")
MoveGuarded = IntExpression("MoveGuarded")
MoveHit = IntExpression("MoveHit")
## MoveType
MoveReversed = IntExpression("MoveReversed")
Name = StringExpression("Name")
NumEnemy = IntExpression("NumEnemy")
NumExplod = TriggerExpression_MaybeInt_Int("NumExplod")
NumHelper = TriggerExpression_MaybeInt_Int("NumHelper")
NumPartner = IntExpression("NumPartner")
NumProj = IntExpression("NumProj")
NumProjID = TriggerExpression_Int_Int("NumProjID")
NumTarget = TriggerExpression_MaybeInt_Int("NumTarget")
P1Name = StringExpression("P1Name")
## P2BodyDist
## P2Dist
P2Life = IntExpression("P2Life")
## P2MoveType
P2StateNo = IntExpression("P2StateNo")
## P2StateType
P2Name = StringExpression("P2Name")
P3Name = StringExpression("P3Name")
P4Name = StringExpression("P4Name")
PalNo = IntExpression("PalNo")
## ParentDist
Pi = IntExpression("pi")
## Pos
Power = IntExpression("Power")
PowerMax = IntExpression("PowerMax")
PlayerIDExist = TriggerExpression_Int_Bool("PlayerIDExist")
PrevStateNo = IntExpression("PrevStateNo")
ProjCancelTime = TriggerExpression_Int_Int("ProjCancelTime")
ProjContactTime = TriggerExpression_Int_Int("ProjContactTime")
ProjGuardedTime = TriggerExpression_Int_Int("ProjGuardedTime")
ProjHitTime = TriggerExpression_Int_Int("ProjHitTime")
Random = IntExpression("Random")
## RootDist
RoundNo = IntExpression("RoundNo")
RoundsExisted = IntExpression("RoundsExisted")
RoundState = IntExpression("RoundState")
## ScreenPos
SelfAnimExist = TriggerExpression_Int_Bool("SelfAnimExist")
Sin = TriggerExpression_Numeric_Float("sin")
StateNo = TriggerExpression_Numeric_Float("StateNo")
## StateType
StageVar = TriggerExpression_String_String("StageVar")
## sysfvar
## sysvar
Tan = TriggerExpression_Numeric_Float("tan")
## TeamMode
TeamSide = IntExpression("TeamSide")
TicksPerSecond = IntExpression("TicksPerSecond")
Time = IntExpression("Time")
## TimeMod
## UniqHitCount
## var
## Vel
Win = BoolExpression("Win")
WinKO = BoolExpression("WinKO")
WinTime = BoolExpression("WinTime")
WinPerfect = BoolExpression("WinPerfect")