from mdk.compiler import create_statedef, build
from mdk.stdlib import ChangeState

import copy

def StateTemplate():
    ChangeState(value = 12345678)

for i in range(10):
    fn = copy.deepcopy(StateTemplate)
    fn.__name__ = f"DevilsEye{i}"
    create_statedef(fn, stateno=i)

build()