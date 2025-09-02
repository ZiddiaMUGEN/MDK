from typing import Callable

from mdk.types.expressions import Expression
from mdk.types.specifier import TypeSpecifier

__all__ = ['Abs', 'Acos', 'AiLevel', 'Alive', 'Anim', 'AnimElemNo', 'AnimElemTime', 'AnimExist', 'AnimTime', 'Asin', 'Atan', 'AuthorName', 'BackEdgeBodyDist', 'BackEdgeDist', 'CanRecover', 'Ceil', 'Command', 'Const', 'Const240p', 'Const480p', 'Const720p', 'Cos', 'Ctrl', 'DrawGame', 'E', 'Exp', 'Facing', 'Floor', 'FrontEdgeBodyDist', 'FrontEdgeDist', 'GameHeight', 'GameTime', 'GameWidth', 'GetHitVar', 'HitCount', 'HitFall', 'HitOver', 'HitPauseTime', 'HitShakeOver', 'ID', 'InGuardDist', 'IsHelper', 'IsHomeTeam', 'Life', 'LifeMax', 'Ln', 'Log', 'Lose', 'MatchNo', 'MatchOver', 'MoveContact', 'MoveGuarded', 'MoveHit', 'MoveReversed', 'Name', 'NumEnemy', 'NumExplod', 'NumHelper', 'NumPartner', 'NumProj', 'NumProjID', 'NumTarget', 'P1Name', 'P2Life', 'P2StateNo', 'P2Name', 'P3Name', 'P4Name', 'PalNo', 'Pi', 'Power', 'PowerMax', 'PlayerIDExist', 'ProjCancelTime', 'ProjContactTime', 'ProjGuardedTime', 'ProjHitTime', 'Random', 'RoundNo', 'RoundsExisted', 'RoundState', 'SelfAnimExist', 'Sin', 'StateNo', 'StageVar', 'Tan', 'TeamSide', 'TicksPerSecond', 'Time', 'Win', 'WinKO', 'WinTime', 'WinPerfect', 'HitDefAttr', "StateType", "MoveType", "TeamMode", "P2MoveType", "P2StateType", "HitVel", "P2BodyDist", "P2Dist", "ParentDist", "Pos", "RootDist", "ScreenPos", "Vel", "ifelse", "Cond", "EmptyExpression", "EmptyTuple"]

class PositionExpression:
    x: Expression
    y: Expression
    def __init__(self, name: str, type: TypeSpecifier): ...

Abs: Callable[..., Expression]
Acos: Callable[..., Expression]
AiLevel: Expression
Alive: Expression
Anim: Expression
AnimElemNo: Callable[..., Expression]
AnimElemTime: Callable[..., Expression]
AnimExist: Callable[..., Expression]
AnimTime: Expression
Asin: Callable[..., Expression]
Atan: Callable[..., Expression]
AuthorName: Expression
BackEdgeBodyDist: Expression
BackEdgeDist: Expression
CanRecover: Expression
Ceil: Callable[..., Expression]
Command: Expression
Cond: Callable[..., Expression]
Const: Callable[..., Expression]
Const240p: Callable[..., Expression]
Const480p: Callable[..., Expression]
Const720p: Callable[..., Expression]
Cos: Callable[..., Expression]
Ctrl: Expression
DrawGame: Expression
E: Expression
Exp: Callable[..., Expression]
Facing: Expression
Floor: Callable[..., Expression]
FrontEdgeBodyDist: Expression
FrontEdgeDist: Expression
GameHeight: Expression
GameTime: Expression
GameWidth: Expression
GetHitVar: Callable[..., Expression]
HitCount: Expression
HitDefAttr: Expression
HitFall: Expression
HitOver: Expression
HitPauseTime: Expression
HitShakeOver: Expression
HitVel: PositionExpression
ID: Expression
ifelse: Callable[..., Expression]
InGuardDist: Expression
IsHelper: Callable[..., Expression]
IsHomeTeam: Expression
Life: Expression
LifeMax: Expression
Ln: Callable[..., Expression]
Log: Callable[..., Expression]
Lose: Expression
MatchNo: Expression
MatchOver: Expression
MoveContact: Expression
MoveGuarded: Expression
MoveHit: Expression
MoveReversed: Expression
Name: Expression
NumEnemy: Expression
NumExplod: Callable[..., Expression]
NumHelper: Callable[..., Expression]
NumPartner: Expression
NumProj: Expression
NumProjID: Callable[..., Expression]
NumTarget: Callable[..., Expression]
P1Name: Expression
P2BodyDist: PositionExpression
P2Dist: PositionExpression
P2Life: Expression
P2StateNo: Expression
P2Name: Expression
P3Name: Expression
P4Name: Expression
PalNo: Expression
ParentDist: PositionExpression
Pi: Expression
Pos: PositionExpression
Power: Expression
PowerMax: Expression
PlayerIDExist: Callable[..., Expression]
PrevStateNo: Expression
ProjCancelTime: Callable[..., Expression]
ProjContactTime: Callable[..., Expression]
ProjGuardedTime: Callable[..., Expression]
ProjHitTime: Callable[..., Expression]
Random: Expression
RoundNo: Expression
RoundsExisted: Expression
RoundState: Expression
RootDist: PositionExpression
ScreenPos: PositionExpression
SelfAnimExist: Callable[..., Expression]
Sin: Callable[..., Expression]
StateNo: Expression
StageVar: Callable[..., Expression]
Tan: Callable[..., Expression]
TeamSide: Expression
TicksPerSecond: Expression
Time: Expression
Vel: PositionExpression
Win: Expression
WinKO: Expression
WinTime: Expression
WinPerfect: Expression
StateType: Expression
MoveType: Expression
TeamMode: Expression
P2MoveType: Expression
P2StateType: Expression
HitVel: PositionExpression
P2BodyDist: PositionExpression
P2Dist: PositionExpression
ParentDist: PositionExpression
Pos: PositionExpression
RootDist: PositionExpression
ScreenPos: PositionExpression
Vel: PositionExpression

EmptyExpression: Expression
EmptyTuple: tuple[Expression]