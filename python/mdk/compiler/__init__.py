from collections.abc import Callable

from mdk.utils import debug
from mdk import state

## builds the CNS file from the importing module.
## this will iterate through all registered Statedefs and produce CNS (technically tMUGEN) as output.
def build(target: str):
    debug(f"Building to target {target}")

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

    print(f"Done building {len(state.ALL_STATEDEF_CNS)} state definitions. Now executing conversion to templated CNS.")

    for state_name in state.ALL_STATEDEF_CNS:
        definition: state.Statedef = state.ALL_STATEDEF_CNS[state_name]

        ## printing for now.
        print(f"[Statedef {state_name}]")
        for param in definition.params:
            print(f"{param} = {definition.params[param]}")
        print()
        for controller in definition.controllers:
            if controller.comment != None:
                print(f";; {controller.comment}")
            print(f"[State {state_name}]")
            print(f"type = {controller.type}")
            for trigger_group in controller.triggers:
                for trigger in controller.triggers[trigger_group]:
                    print(f"trigger{trigger_group} = {trigger}")
            if len(controller.triggers) == 0: print("trigger1 = 1")
            for param in controller.params:
                print(f"{param} = {controller.params[param]}")
            print()
        print()