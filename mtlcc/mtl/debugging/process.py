from mtl.utils.func import generate_random_string
from mtl.types.debugging import DebuggerLaunchInfo

import ctypes
import shutil
import os
import subprocess

CREATE_SUSPENDED = 4

def launch(target: str, character: str) -> DebuggerLaunchInfo:
    result = DebuggerLaunchInfo(None, None)
    ## copy the character folder to the MUGEN chars folder.
    working = os.path.dirname(os.path.abspath(target))
    chara = os.path.dirname(os.path.abspath(character))
    if chara != f"{working}/chars":
        random_id = generate_random_string(8)
        shutil.copytree(chara, f"{working}/chars/{random_id}/")
        character = f"chars/{random_id}/{os.path.basename(character)}"
        print(f"Relocated character data to {character} for launch.")
        result.character_folder = os.path.dirname(f"{working}/{character}")

    ## prep the command-line arguments.
    args = [target, "-p1", character, "-p2", "kfm", "-p1.ai", "1", "-p2.ai", "1"]
    result.subprocess = subprocess.Popen(args, cwd=working)#, creationflags=CREATE_SUSPENDED)

    return result