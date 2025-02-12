from typing import Union

from mdk.triggers import Trigger
from mdk.utils import short_uuid
from mdk import state

## special types for int/float variables.
class IntVar(Trigger):
    ## TODO: need to find a way to represent the variable by name. for now it will use a generic name.
    def __init__(self, val: Union[Trigger, int]):
        self.repr: str = f"unnamedVar_{short_uuid()}"
        self.val: str = repr(val)
        ## perform initialization of this variable in MUGEN
        initializer: state.Controller = self.create()
        if state.CURRENT_STATEDEF != None:
            ## at the start of the current statedef, append a controller to initialize this variable.
            state.CURRENT_STATEDEF.controllers.insert(0, initializer)
        else:
            ## at the global scope, add a controller to initialize this variable.
            initializer.params["scope"] = "global"
            state.GLOBAL_CONTROLLERS.append(initializer)
            
    def create(self) -> state.Controller:
        ctrl: state.Controller = state.Controller()
        ctrl.type = "VarSet"
        ctrl.comment = f"assigning default value for {self.repr}"
        ctrl.add_trigger(1, "Time = 0")
        ctrl.params[self.repr] = self.val
        ctrl.params["ignorehitpause"] = "1"
        ctrl.params["persistent"] = "256"
        return ctrl