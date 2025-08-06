from mdk.compiler import statedef, build
from mdk.utils.controllers import ChangeState

from mdk.types.builtins import IntVar

@statedef(stateno = 9)
def idle():
    pass

@statedef(stateno = 8)
def stand():
    myVar = IntVar()

    if not True and True:
        ChangeState(value = stand)
    elif True and False:
        idle()
    else:
        idle()
    idle()

if __name__ == "__main__":
    build()