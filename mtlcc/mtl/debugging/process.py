from mtl.types.context import DebuggingContext

import ctypes
import os
import subprocess

CREATE_SUSPENDED = 4

def launch(target: str, character: str) -> subprocess.Popen:
    ## prep the command-line arguments.
    working = os.path.dirname(os.path.abspath(target))
    args = [target, "-p1", os.path.abspath(character), "-p2", "kfm", "-p1.ai", "1", "-p2.ai", "1"]
    result = subprocess.Popen(args, cwd=working)#, creationflags=CREATE_SUSPENDED)

    return result