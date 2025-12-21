import sys

from mtl.types.debugging import DebuggerRequest, DebuggerRequestIPC, DebuggerResponseIPC, DebuggerCommand
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

def processDebugIPC() -> DebuggerRequestIPC:
    ## we receive debug request messages over stdin.
    ## the structure of a debug request message is:
    ## 36 bytes for message ID (uuid string as UTF-8)
    ## 4 bytes for command (int)
    ## 4 bytes for parameter size (int)
    ## n bytes for parameters (bytes)

    message = sys.stdin.buffer.read(36)
    command = int.from_bytes(sys.stdin.buffer.read(4), 'little')
    param_size = int.from_bytes(sys.stdin.buffer.read(4), 'little')

    if param_size > 0:
        params = sys.stdin.buffer.read(param_size)
    else:
        params = b''

    return DebuggerRequestIPC(message, DebuggerCommand(command), params)

def sendResponseIPC(response: DebuggerResponseIPC):
    ## we receive debug request messages over stdout.
    ## the structure of a debug response message is:
    ## 36 bytes for message ID (uuid string as UTF-8)
    ## 4 bytes for command (int)
    ## 4 bytes for response type (int)
    ## 4 bytes for parameter size (int)
    ## n bytes for parameters (bytes)

    sys.stdout.buffer.write(response.message_id)
    sys.stdout.buffer.write(int(response.command_type).to_bytes(4, 'little'))
    sys.stdout.buffer.write(int(response.response_type).to_bytes(4, 'little'))
    sys.stdout.buffer.write(len(response.response_detail).to_bytes(4, 'little'))
    sys.stdout.buffer.write(response.response_detail)