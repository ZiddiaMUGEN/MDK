from typing import Union

from mdk.types import VarScope, VarType
from mdk.controllers import VarSet
from mdk.triggers import Trigger
from mdk.utils import short_uuid
from mdk import state

## special types for int/float variables.
class IntVar(Trigger):
    ## TODO: need to find a way to represent the variable by name. for now it will use a generic name.
    def __init__(self, val: Union[Trigger, int]):
        if not isinstance(val, Trigger) and not type(val) == int:
            raise Exception("Can't initialize an IntVar with a non-int or non-trigger input!")
        self.repr: str = f"unnamediVar_{short_uuid()}"
        if state.CURRENT_STATEDEF != None:
            ## insert a controller at the current location to initialize this variable.
            ## because this is in the context of user code, we can just initialize by calling VarSet (which is pretty weird!)
            VarSet(name = self.repr, value = val, scope = VarScope.Local)
        else:
            ## at the global scope, add a controller to initialize this variable.
            initializer = VarSet(name = self.repr, value = val, scope = VarScope.Global, type = VarType.Integer, append = False)
            state.GLOBAL_CONTROLLERS.append(initializer)

class FloatVar(Trigger):
    ## TODO: need to find a way to represent the variable by name. for now it will use a generic name.
    def __init__(self, val: Union[Trigger, float]):
        if not isinstance(val, Trigger) and not type(val) == float:
            raise Exception("Can't initialize an FloatVar with a non-float or non-trigger input!")
        self.repr: str = f"unnamedfVar_{short_uuid()}"
        if state.CURRENT_STATEDEF != None:
            ## insert a controller at the current location to initialize this variable.
            ## because this is in the context of user code, we can just initialize by calling VarSet (which is pretty weird!)
            VarSet(name = self.repr, value = val, scope = VarScope.Local)
        else:
            ## at the global scope, add a controller to initialize this variable.
            initializer = VarSet(name = self.repr, value = val, scope = VarScope.Global, type = VarType.Float, append = False)
            state.GLOBAL_CONTROLLERS.append(initializer)