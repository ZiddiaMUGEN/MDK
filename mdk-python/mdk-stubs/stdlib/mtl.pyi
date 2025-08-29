__all__ = ["rescope"]

from mdk.types import StateScope
from mdk.stdlib.redirects import RedirectTarget

def rescope(source: RedirectTarget, target: StateScope) -> RedirectTarget: ...