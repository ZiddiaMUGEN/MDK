from mdk.compiler import create_statedef, build
from mdk.utils.controllers import ChangeState
from mdk.utils.shared import get_context

import copy

def StateTemplate():
    ChangeState(value = 12345678)

for i in range(10):
    fn = copy.deepcopy(StateTemplate)
    fn.__name__ = f"DevilsEye{i}"
    create_statedef(fn, stateno=i)

build()
print(get_context())