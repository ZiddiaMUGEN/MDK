## this is an implementation of `common1.cns` using MDK-python.
from mdk import statedef, build
from mdk.types import StateType, PhysicsType

from mdk.triggers import *
from mdk.controllers import *

from mdk.vars import IntVar

myVar = IntVar(0)

@statedef(type = StateType.S, physics = PhysicsType.S, sprpriority = 0, stateno = 0)
def Stand():
    if Anim != 0 and Anim != 5 or Anim == 5 and AnimTime == 0:
        ChangeAnim(value = 0)
    if Time == 0:
        VelSet(y = 0)

@statedef()
def Walk():
    print("parsing Walk")

build(target = "common1.cns")