from mdk.types.expressions import Expression, ConvertibleExpression
from mdk.stdlib.triggers import PositionExpression
from typing import Callable, Optional, Protocol

__all__ = ['parent', 'root', 'partner', 'helper', 'target', 'enemy', 'enemynear', 'helperID', 'targetID', 'enemyID', 'enemynearID', 'playerID']

class RedirectTarget:
    target: Expression
    expr: Expression
    AiLevel: Expression
    Alive: Expression
    Anim: Expression
    AnimElemNo: Callable[..., Expression]
    AnimElemTime: Callable[..., Expression]
    AnimExist: Callable[..., Expression]
    AnimTime: Expression
    AuthorName: Expression
    BackEdgeBodyDist: Expression
    BackEdgeDist: Expression
    CanRecover: Expression
    Command: Expression
    Const: Callable[..., Expression]
    Ctrl: Expression
    DrawGame: Expression
    Facing: Expression
    FrontEdgeBodyDist: Expression
    FrontEdgeDist: Expression
    HitCount: Expression
    HitDefAttr: Expression
    HitFall: Expression
    HitOver: Expression
    HitPauseTime: Expression
    HitShakeOver: Expression
    HitVel: PositionExpression
    ID: Expression
    InGuardDist: Expression
    IsHelper: Callable[..., Expression]
    IsHomeTeam: Expression
    Life: Expression
    LifeMax: Expression
    Lose: Expression
    MoveContact: Expression
    MoveGuarded: Expression
    MoveHit: Expression
    MoveReversed: Expression
    MoveType: Expression
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
    P2MoveType: Expression
    P2Name: Expression
    P2StateNo: Expression
    P2StateType: Expression
    P3Name: Expression
    P4Name: Expression
    PalNo: Expression
    ParentDist: PositionExpression
    Pos: PositionExpression
    Power: Expression
    PowerMax: Expression
    PrevStateNo: Expression
    ProjCancelTime: Callable[..., Expression]
    ProjContactTime: Callable[..., Expression]
    ProjGuardedTime: Callable[..., Expression]
    ProjHitTime: Callable[..., Expression]
    RootDist: PositionExpression
    ScreenPos: PositionExpression
    SelfAnimExist: Callable[..., Expression]
    StateNo: Expression
    StateType: Expression
    StageVar: Callable[..., Expression]
    TeamMode: Expression
    TeamSide: Expression
    Time: Expression
    Vel: PositionExpression
    Win: Expression
    WinKO: Expression
    WinPerfect: Expression
    WinTime: Expression
    def __init__(self, target: str, expr: Expression | None = None) -> None: ...
    def __getattr__(self, name: str) -> Expression: ...

class RedirectFunction(Protocol):
    def __call__(self, id: Optional[ConvertibleExpression] = ..., /) -> RedirectTarget:
        ...


parent: RedirectTarget
root: RedirectTarget
partner: RedirectTarget
helper: RedirectTarget
target: RedirectTarget
enemy: RedirectTarget
enemynear: RedirectTarget

helperID: RedirectFunction
targetID: RedirectFunction
enemyID: RedirectFunction
enemynearID: RedirectFunction
playerID: RedirectFunction
