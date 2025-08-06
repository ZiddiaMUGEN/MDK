from mdk.compiler import statedef, build, get_context
from mdk.stdlib import ChangeState, Alive
from mdk.types import IntVar

@statedef(stateno = 9)
def idle():
    pass

@statedef(stateno = 8)
def stand():
    myVar = IntVar()

    if Alive:
        ChangeState(value = stand)
    elif True and False:
        idle()
    else:
        idle()
    idle()

if __name__ == "__main__":
    build()
    print(get_context())