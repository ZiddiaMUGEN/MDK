from mtl.types.debugging import DebuggerRequest, DebuggerCommand
from mtl.utils.func import equals_insensitive

def processDebugCommand(input: str) -> DebuggerRequest:
    if equals_insensitive(input, "exit"):
        return DebuggerRequest(DebuggerCommand.EXIT, [])
    elif equals_insensitive(input, "help"):
        components = input.split(" ")[1:] if " " in input else []
        return DebuggerRequest(DebuggerCommand.HELP, components)
    elif equals_insensitive(input, "launch"):
        return DebuggerRequest(DebuggerCommand.LAUNCH, [])
    elif equals_insensitive(input, "continue"):
        return DebuggerRequest(DebuggerCommand.CONTINUE, [])
    elif equals_insensitive(input, "stop"):
        return DebuggerRequest(DebuggerCommand.STOP, [])
    elif equals_insensitive(input, "step"):
        return DebuggerRequest(DebuggerCommand.STEP, [])
    elif input.lower().startswith("load "):
        return DebuggerRequest(DebuggerCommand.LOAD, input.split(" ")[1:])
    elif input.lower().startswith("delete "):
        return DebuggerRequest(DebuggerCommand.DELETE, input.split(" ")[1:])
    elif input.lower().startswith("deletep "):
        return DebuggerRequest(DebuggerCommand.DELETEP, input.split(" ")[1:])
    elif input.lower().startswith("info "):
        return DebuggerRequest(DebuggerCommand.INFO, input.split(" ")[1:])
    elif input.lower().startswith("break "):
        return DebuggerRequest(DebuggerCommand.BREAK, input.split(" ")[1:])
    elif input.lower().startswith("breakp "):
        return DebuggerRequest(DebuggerCommand.BREAKP, input.split(" ")[1:])
    
    print(f"Unrecognized debugger command: {input}")
    return DebuggerRequest(DebuggerCommand.NONE, [])