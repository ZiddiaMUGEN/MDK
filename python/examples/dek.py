## this is a sample of Devil's Eye Killer using MDK-python.
from mdk import statedef, build, create_statedef
from mdk.types import StateType, PhysicsType

from mdk.triggers import *
from mdk.controllers import *

from copy import deepcopy

#from mdk.vars import IntVar

def StateTemplate():
    ChangeState(value = 12345678)

for i in range(10):
    fn = deepcopy(StateTemplate)
    fn.__name__ = f"DevilsEye{i}"
    create_statedef(fn, stateno=i)

build(target = "dek.cns")