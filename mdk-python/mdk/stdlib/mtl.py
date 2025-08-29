## contains stdlib functions which are exposed by MTL (non-CNS stdlib)
__all__ = ["rescope"]

from mdk.types import StateScope

from mdk.stdlib.redirects import RedirectTarget

def rescope(source: RedirectTarget, target: StateScope) -> RedirectTarget:
    new_target = str(target)
    if new_target == "player": new_target = "root"
    if new_target == "shared": raise Exception(f"target parameter to rescope should not be SHARED.")
    return RedirectTarget(f"rescope({source.__repr__()}, {new_target})")