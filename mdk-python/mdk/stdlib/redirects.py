from typing import Protocol, Optional
from mdk.types.context import Expression

class RedirectTarget:
    def __init__(self, target: str, expr: Optional[Expression] = None):
        self.target = target
        self.expr = expr
    def __repr__(self):
        if isinstance(self.expr, Expression):
            return f"{self.target}({self.expr})"
        return self.target

class RedirectID(Protocol):
    def __call__(self, x: Expression = ..., /) -> RedirectTarget:
        ...

def RedirectTargetBuilder(target: str) -> RedirectID:
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