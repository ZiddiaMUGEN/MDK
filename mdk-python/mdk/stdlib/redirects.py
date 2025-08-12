from typing import Protocol, Optional, Callable

from mdk.types.expressions import Expression
import mdk.stdlib.triggers as triggers

class RedirectTarget:
    def __init__(self, target: str, expr: Optional[Expression] = None):
        self.target = target
        self.expr = expr

        ## create redirected trigger expressions.
        ## this is littered with type-check failures, they are safe to ignore.
        self.AiLevel = self._redirect_atom(triggers.AiLevel)
        self.Alive = self._redirect_atom(triggers.Alive)
        self.Anim = self._redirect_atom(triggers.Anim)
        self.AnimElemNo: Callable[..., Expression] = self._redirect_function(triggers.AnimElemNo)  # type: ignore
        self.AnimElemTime: Callable[..., Expression] = self._redirect_function(triggers.AnimElemTime)  # type: ignore
        self.AnimExist: Callable[..., Expression] = self._redirect_function(triggers.AnimExist)  # type: ignore
        self.AnimTime = self._redirect_atom(triggers.AnimTime)
        self.AuthorName = self._redirect_atom(triggers.AuthorName)
        self.BackEdgeBodyDist = self._redirect_atom(triggers.BackEdgeBodyDist)
        self.BackEdgeDist = self._redirect_atom(triggers.BackEdgeDist)
        self.CanRecover = self._redirect_atom(triggers.CanRecover)
        self.Command = self._redirect_atom(triggers.Command)
        self.Const: Callable[..., Expression] = self._redirect_function(triggers.Const)  # type: ignore
        self.Ctrl = self._redirect_atom(triggers.Ctrl)
        self.DrawGame = self._redirect_atom(triggers.DrawGame)
        self.Facing = self._redirect_atom(triggers.Facing)
        self.FrontEdgeBodyDist = self._redirect_atom(triggers.FrontEdgeBodyDist)
        self.FrontEdgeDist = self._redirect_atom(triggers.FrontEdgeDist)
        self.HitCount = self._redirect_atom(triggers.HitCount)
        self.HitDefAttr = self._redirect_atom(triggers.HitDefAttr)
        self.HitFall = self._redirect_atom(triggers.HitFall)
        self.HitOver = self._redirect_atom(triggers.HitOver)
        self.HitPauseTime = self._redirect_atom(triggers.HitPauseTime)
        self.HitShakeOver = self._redirect_atom(triggers.HitShakeOver)
        self.ID = self._redirect_atom(triggers.ID)
        self.InGuardDist = self._redirect_atom(triggers.InGuardDist)
        self.IsHelper: Callable[..., Expression] = self._redirect_function(triggers.IsHelper) # type: ignore
        self.IsHomeTeam = self._redirect_atom(triggers.IsHomeTeam)
        self.Life = self._redirect_atom(triggers.Life)
        self.LifeMax = self._redirect_atom(triggers.LifeMax)
        self.Lose = self._redirect_atom(triggers.Lose)
        self.MoveContact = self._redirect_atom(triggers.MoveContact)
        self.MoveGuarded = self._redirect_atom(triggers.MoveGuarded)
        self.MoveHit = self._redirect_atom(triggers.MoveHit)
        self.MoveReversed = self._redirect_atom(triggers.MoveReversed)
        self.MoveType = self._redirect_atom(triggers.MoveType)
        self.Name = self._redirect_atom(triggers.Name)
        self.NumEnemy = self._redirect_atom(triggers.NumEnemy)
        self.NumExplod: Callable[..., Expression] = self._redirect_function(triggers.NumExplod) # type: ignore
        self.NumHelper: Callable[..., Expression] = self._redirect_function(triggers.NumHelper) # type: ignore
        self.NumPartner = self._redirect_atom(triggers.NumPartner)
        self.NumProj = self._redirect_atom(triggers.NumProj)
        self.NumProjID: Callable[..., Expression] = self._redirect_function(triggers.NumProjID)  # type: ignore
        self.NumTarget: Callable[..., Expression] = self._redirect_function(triggers.NumTarget) # type: ignore
        self.P1Name = self._redirect_atom(triggers.P1Name)
        self.P2Life = self._redirect_atom(triggers.P2Life)
        self.P2MoveType = self._redirect_atom(triggers.P2MoveType)
        self.P2Name = self._redirect_atom(triggers.P2Name)
        self.P2StateNo = self._redirect_atom(triggers.P2StateNo)
        self.P2StateType = self._redirect_atom(triggers.P2StateType)
        self.P3Name = self._redirect_atom(triggers.P3Name)
        self.P4Name = self._redirect_atom(triggers.P4Name)
        self.PalNo = self._redirect_atom(triggers.PalNo)
        self.Power = self._redirect_atom(triggers.Power)
        self.PowerMax = self._redirect_atom(triggers.PowerMax)
        self.PrevStateNo = self._redirect_atom(triggers.PrevStateNo)
        self.ProjCancelTime: Callable[..., Expression] = self._redirect_function(triggers.ProjCancelTime)  # type: ignore
        self.ProjContactTime: Callable[..., Expression] = self._redirect_function(triggers.ProjContactTime)  # type: ignore
        self.ProjGuardedTime: Callable[..., Expression] = self._redirect_function(triggers.ProjGuardedTime)  # type: ignore
        self.ProjHitTime: Callable[..., Expression] = self._redirect_function(triggers.ProjHitTime)  # type: ignore
        self.SelfAnimExist: Callable[..., Expression] = self._redirect_function(triggers.SelfAnimExist)  # type: ignore
        self.StateNo = self._redirect_atom(triggers.StateNo)
        self.StateType = self._redirect_atom(triggers.StateType)
        self.SelfAnimExist = self._redirect_function(triggers.StageVar)  # type: ignore
        self.TeamMode = self._redirect_atom(triggers.TeamMode)
        self.TeamSide = self._redirect_atom(triggers.TeamSide)
        self.Time = self._redirect_atom(triggers.Time)
        self.Win = self._redirect_atom(triggers.Win)
        self.WinKO = self._redirect_atom(triggers.WinKO)
        self.WinPerfect = self._redirect_atom(triggers.WinPerfect)
        self.WinTime = self._redirect_atom(triggers.WinTime)

    def _redirect_atom(self, expr: Expression) -> Expression:
        return expr.make_expression(f"{self.__repr__()},{expr.exprn}")

    def _redirect_function(self, fn: Callable[..., Expression]) -> Callable[..., Expression]:
        def _call(*args, **kwargs) -> Expression:
            result = fn(*args, **kwargs)
            return result.make_expression(f"{self.__repr__()},{result.exprn}")
        return _call

    def __repr__(self):
        if isinstance(self.expr, Expression):
            return f"{self.target}({self.expr})"
        return self.target

def RedirectTargetBuilder(target: str) -> Callable[[Optional[Expression]], RedirectTarget]:
    def _redirect(id: Optional[Expression] = None) -> RedirectTarget:
        return RedirectTarget(target, id)
    return _redirect

parent = RedirectTarget("parent")
root = RedirectTarget("root")
partner = RedirectTarget("partner")

helper = RedirectTargetBuilder("helper")
target = RedirectTargetBuilder("target")
enemy = RedirectTargetBuilder("enemy")
enemynear = RedirectTargetBuilder("enemynear")
playerID = RedirectTargetBuilder("playerID")

__all__ = ["parent", "root", "partner", "helper", "target", "enemy", "enemynear", "playerID"]