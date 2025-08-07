from mdk.compiler import statedef, template, build, get_context
from mdk.stdlib import ChangeState, Alive, parent
from mdk.types import IntVar, Int

@statedef(stateno = 9)
def idle():
    pass

@template
def myTemplate(myParam: Int):
    idle()

@statedef(stateno = 8)
def stand():
    myVar = IntVar()

    if parent.AiLevel == 1:
        ChangeState(value = stand)
    elif True and False:
        myTemplate(myParam = myVar)
        myTemplate()
    else:
        idle()
    idle()

if __name__ == "__main__":
    build()
    print(get_context())