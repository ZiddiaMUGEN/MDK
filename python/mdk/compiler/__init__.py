from collections.abc import Callable
from typing import TextIO

from mdk.utils import debug
from mdk import state

## builds the CNS file from the importing module.
## this will iterate through all registered Statedefs and produce CNS (technically tMUGEN) as output.
def build(target: str):
    print(f"Building MDK character states to CNS target {target}")

    # iterate through each statedef function registered by the decorator.
    for state_name in state.ALL_STATEDEF_IMPLS:
        impl: state.StatedefImpl = state.ALL_STATEDEF_IMPLS[state_name]
        fn: Callable = impl.fn
        
        # prep a new statedef to store controllers
        state.CURRENT_STATEDEF = state.Statedef(state_name)

        # call the statedef function directly to build CNS. the controllers called by `fn` will directly register their controllers to CURRENT_STATEDEF
        fn()

        # save any output if needed
        if state.CURRENT_STATEDEF != None:
            state.CURRENT_STATEDEF.params = impl.params
            state.ALL_STATEDEF_CNS[state.CURRENT_STATEDEF.name] = state.CURRENT_STATEDEF

    print(f"Done building {len(state.ALL_STATEDEF_CNS)} state definitions. Executing conversion to templated CNS.")

    with open(target, mode='w') as f:
        # top-level statements - tMUGEN will convert these for us into -2-scoped and explod-guarded declarations.
        for controller in state.GLOBAL_CONTROLLERS:
            create_controller(f, controller, "Global")
            f.write('\n')
        f.write('\n')

        for state_name in state.ALL_STATEDEF_CNS:
            definition: state.Statedef = state.ALL_STATEDEF_CNS[state_name]

            f.write(f"[Statedef {state_name}]\n")
            for param in definition.params:
                f.write(f"{param} = {definition.params[param]}\n")
            f.write('\n')
            for controller in definition.controllers:
                create_controller(f, controller, state_name)
                f.write('\n')
            f.write('\n')
    
    print(f"MDK execution completed, output CNS is available at {target}")

def create_controller(f: TextIO, controller: state.Controller, header: str):
    if controller.comment != None:
        f.write(f";; {controller.comment}\n")
    f.write(f"[State {header}]\n")
    f.write(f"type = {controller.type}\n")
    for trigger_group in controller.triggers:
        for trigger in controller.triggers[trigger_group]:
            f.write(f"trigger{trigger_group} = {trigger}\n")
    if len(controller.triggers) == 0: f.write("trigger1 = 1\n")
    for param in controller.params:
        f.write(f"{param} = {controller.params[param]}\n")