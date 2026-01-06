## this module provides addresses to triggers, breakpoint offsets, etc for each MUGEN version supported.

from mtl.debugging.asmbin.breakpoint_11b1 import BREAKPOINT_FUNC_11B1
from mtl.debugging.asmbin.passpoint_11b1 import PASSPOINT_FUNC_11B1

from mtl.debugging.asmbin.breakpoint_11a4 import BREAKPOINT_FUNC_11A4
from mtl.debugging.asmbin.passpoint_11a4 import PASSPOINT_FUNC_11A4

from mtl.debugging.asmbin.breakpoint_100 import BREAKPOINT_FUNC_100
from mtl.debugging.asmbin.passpoint_100 import PASSPOINT_FUNC_100

from mtl.debugging.asmbin.breakpoint_win import BREAKPOINT_FUNC_WIN
from mtl.debugging.asmbin.passpoint_win import PASSPOINT_FUNC_WIN

### read memory at this address to determine MUGEN version.
SELECT_VERSION_ADDRESS = 0x4405C0

### note: to find the SCTRL_BREAKPOINT_INSERT value search for `TrigArrayTest bug`.
### then look one function up to find where the controllers are looped through.

ADDRESS_MUGEN_WIN = {
    "SCTRL_BREAKPOINT_TABLE": 0x4A0600, # address of the breakpoints table, this is enough for 19 breakpoints.
    "SCTRL_BREAKPOINT_INSERT": 0x47F728, # address to insert a jump
    "SCTRL_PASSPOINT_INSERT": 0x47F775, # address to insert a jump
    "SCTRL_BREAKPOINT_INSERT_FUNC": [0xE9, 0x73, 0x0F, 0x02, 0x00], # patch to insert at SCTRL_BREAKPOINT_INSERT
    "SCTRL_PASSPOINT_INSERT_FUNC": [0xE9, 0xD6, 0x0F, 0x02, 0x00], # patch to insert at SCTRL_PASSPOINT_INSERT
    "SCTRL_BREAKPOINT_FUNC_ADDR": 0x4A06A0, # address to write the function to
    "SCTRL_PASSPOINT_FUNC_ADDR": 0x4A0750, # address to write the function to
    "SCTRL_BREAKPOINT_ADDR": 0x4A071D, # address inside the function to break at
    "SCTRL_PASSPOINT_ADDR": 0x4A07C3, # address inside the function to break at
    "SCTRL_STEP_ADDR": 0x4A0870, # address to write the step-into character pointers to
    ## the below are produced by assembling `breakpoint.asm` and `passpoint.asm` for the target version.
    "SCTRL_BREAKPOINT_FUNC": BREAKPOINT_FUNC_WIN,
    "SCTRL_PASSPOINT_FUNC": PASSPOINT_FUNC_WIN,
    "game": 0x4B5B4C,
    "player": 0xB754,
    "stateno": 0xBF4,
    "exist": 0x158,
    "var": 0xE40,
    "fvar": 0xF30,
    "sysvar": 0xFD0,
    "sysfvar": 0xFE4,
    "root_addr": 0x2624,
    "helperid": 0x2618,
    "state_owner": 0xBF0,
    "triggers": {},
    "game_triggers": {}
}

ADDRESS_MUGEN_100 = {
    "SCTRL_BREAKPOINT_TABLE": 0x49A700, # address of the breakpoints table, this is enough for 19 breakpoints.
    "SCTRL_BREAKPOINT_INSERT": 0x48B966, # address to insert a jump
    "SCTRL_PASSPOINT_INSERT": 0x48B9B4, # address to insert a jump
    "SCTRL_BREAKPOINT_INSERT_FUNC": [0xE9, 0x35, 0xEE, 0x00, 0x00], # patch to insert at SCTRL_BREAKPOINT_INSERT
    "SCTRL_PASSPOINT_INSERT_FUNC": [0xE9, 0x77, 0xEE, 0x00, 0x00], # patch to insert at SCTRL_PASSPOINT_INSERT
    "SCTRL_BREAKPOINT_FUNC_ADDR": 0x49A7A0, # address to write the function to
    "SCTRL_PASSPOINT_FUNC_ADDR": 0x49A830, # address to write the function to
    "SCTRL_BREAKPOINT_ADDR": 0x49A80F, # address inside the function to break at
    "SCTRL_PASSPOINT_ADDR": 0x49A8A2, # address inside the function to break at
    "SCTRL_STEP_ADDR": 0x49A970, # address to write the step-into character pointers to
    ## the below are produced by assembling `breakpoint.asm` and `passpoint.asm` for the target version.
    "SCTRL_BREAKPOINT_FUNC": BREAKPOINT_FUNC_100,
    "SCTRL_PASSPOINT_FUNC": PASSPOINT_FUNC_100,
    "game": 0x52B40C,
    "player": 0x11234,
    "stateno": 0xC4C,
    "exist": 0x1B0,
    "var": 0xE9C,
    "fvar": 0xF8C,
    "sysvar": 0x102C,
    "sysfvar": 0x1040,
    "root_addr": 0x1480,
    "helperid": 0x1474,
    "state_owner": 0xC38,
    "triggers": {},
    "game_triggers": {}
}

ADDRESS_MUGEN_11A4 = {
    "SCTRL_BREAKPOINT_TABLE": 0x4DD920, # address of the breakpoints table, this is enough for 19 breakpoints.
    "SCTRL_BREAKPOINT_INSERT": 0x45BC95, # address to insert a jump
    "SCTRL_PASSPOINT_INSERT": 0x45BCE3, # address to insert a jump
    "SCTRL_BREAKPOINT_INSERT_FUNC": [0xE9, 0x26, 0x1D, 0x08, 0x00], # patch to insert at SCTRL_BREAKPOINT_INSERT
    "SCTRL_PASSPOINT_INSERT_FUNC": [0xE9, 0x68, 0x1D, 0x08, 0x00], # patch to insert at SCTRL_PASSPOINT_INSERT
    "SCTRL_BREAKPOINT_FUNC_ADDR": 0x4DD9C0, # address to write the function to
    "SCTRL_PASSPOINT_FUNC_ADDR": 0x4DDA50, # address to write the function to
    "SCTRL_BREAKPOINT_ADDR": 0x4DDA2F, # address inside the function to break at
    "SCTRL_PASSPOINT_ADDR": 0x4DDAC2, # address inside the function to break at
    "SCTRL_STEP_ADDR": 0x4DDB90, # address to write the step-into character pointers to
    ## the below are produced by assembling `breakpoint.asm` and `passpoint.asm` for the target version.
    "SCTRL_BREAKPOINT_FUNC": BREAKPOINT_FUNC_11A4,
    "SCTRL_PASSPOINT_FUNC": PASSPOINT_FUNC_11A4,
    "game": 0x5040E8,
    "player": 0x12278,
    "stateno": 0xCCC,
    "exist": 0x1B0,
    "var": 0xF1C,
    "fvar": 0x100C,
    "sysvar": 0x10AC,
    "sysfvar": 0x10C0,
    "root_addr": 0x1650,
    "helperid": 0x1644,
    "state_owner": 0xCB8,
    "triggers": {
        "id": [0x04, int],
        "time": [0xED4, int],
        "helperid": [0x1644, int],
        "parent": [0x1648, int],
        "prevstateno": [0xCD0, int],
        "facing": [0x1E8, int],
        "movecontact": [0xF0C, int],
        "palno": [0x153C, int],
        "stateno": [0xCCC, int],
        "life": [0x1B8, int],
        "power": [0x1D0, int],
        "alive": [0xF00, bool],
        "ctrl": [0xEE4, bool],
        "pausemovetime": [0x228, int],
        "supermovetime": [0x22C, int],
        "ailevel": [0x2424, int],
        "projhit": [0x2C0, int],
        "prevstateno": [0xCD0, int],
        "statetype": [0xED8, "statetype"],
        "movetype": [0xEDC, "movetype"],
        "hitpausetime": [0xEF4, int],
        "movecontact": [0xF0C, int],
        "movehit": [0xF10, int],
        "ailevel": [0x2424, int],
    },
    "game_triggers": {
        "gametime": [0x11E98, int],
        "roundstate": [0x12754, int],
        "roundno": [0x12728, int],
        "win": [0x12758, bool],
        "winko": [0x12758, bool],
    }
}

## at SCTRL_BREAKPOINT_INSERT:
### ECX = controller index in state, EBP = player pointer
## breakpoints are complicated because trying to set breakpoints on a specific controller would mean breaking hundreds of times per frame.
## to avoid the laggy mess this results in, i inject code into MUGEN to handle breakpoint checking itself.
## basically this looks like this:
### - at SCTRL_BREAKPOINT_INSERT, set a JUMP to SCTRL_BREAKPOINT_FUNC_ADDR
### - at SCTRL_BREAKPOINT_TABLE, insert a table with all the known breakpoints
### - at SCTRL_BREAKPOINT_FUNC, insert code to scan the breakpoint table and trigger a breakpoint if a stateno/index pair matches
### - whenever a breakpoint gets set or deleted, updated the table at SCTRL_BREAKPOINT_TABLE.
ADDRESS_MUGEN_11B1 = {
    "SCTRL_BREAKPOINT_TABLE": 0x4DD920, # address of the breakpoints table, this is enough for 19 breakpoints.
    "SCTRL_BREAKPOINT_INSERT": 0x45C1F5, # address to insert a jump
    "SCTRL_PASSPOINT_INSERT": 0x45C243, # address to insert a jump
    "SCTRL_BREAKPOINT_INSERT_FUNC": [0xE9, 0xC6, 0x17, 0x08, 0x00], # patch to insert at SCTRL_BREAKPOINT_INSERT
    "SCTRL_PASSPOINT_INSERT_FUNC": [0xE9, 0x08, 0x18, 0x08, 0x00], # patch to insert at SCTRL_PASSPOINT_INSERT
    "SCTRL_BREAKPOINT_FUNC_ADDR": 0x4DD9C0, # address to write the function to
    "SCTRL_PASSPOINT_FUNC_ADDR": 0x4DDA50, # address to write the function to
    "SCTRL_BREAKPOINT_ADDR": 0x4DDA2F, # address inside the function to break at
    "SCTRL_PASSPOINT_ADDR": 0x4DDAC2, # address inside the function to break at
    "SCTRL_STEP_ADDR": 0x4DDB90, # address to write the step-into character pointers to
    ## the below are produced by assembling `breakpoint.asm` and `passpoint.asm` for the target version.
    "SCTRL_BREAKPOINT_FUNC": BREAKPOINT_FUNC_11B1,
    "SCTRL_PASSPOINT_FUNC": PASSPOINT_FUNC_11B1,
    "game": 0x5040E8,
    "player": 0x12278,
    "stateno": 0xCCC,
    "exist": 0x1B0,
    "var": 0xF1C,
    "fvar": 0x100C,
    "sysvar": 0x10AC,
    "sysfvar": 0x10C0,
    "root_addr": 0x1650,
    "helperid": 0x1644,
    "state_owner": 0xCB8,
    "triggers": {
        "id": [0x04, int],
        "time": [0xED4, int],
        "helperid": [0x1644, int],
        "parent": [0x1648, int],
        "prevstateno": [0xCD0, int],
        "facing": [0x1E8, int],
        "movecontact": [0xF0C, int],
        "palno": [0x153C, int],
        "stateno": [0xCCC, int],
        "life": [0x1B8, int],
        "power": [0x1D0, int],
        "alive": [0xF00, bool],
        "ctrl": [0xEE4, bool],
        "pausemovetime": [0x228, int],
        "supermovetime": [0x22C, int],
        "ailevel": [0x2424, int],
        "projhit": [0x2C0, int],
        "prevstateno": [0xCD0, int],
        "statetype": [0xED8, "statetype"],
        "movetype": [0xEDC, "movetype"],
        "hitpausetime": [0xEF4, int],
        "movecontact": [0xF0C, int],
        "movehit": [0xF10, int],
        "ailevel": [0x2424, int],
    },
    "game_triggers": {
        "gametime": [0x11E98, int],
        "roundstate": [0x12754, int],
        "roundno": [0x12728, int],
        "win": [0x12758, bool],
        "winko": [0x12758, bool],
    }
}

ADDRESS_DATABASE = {
    0x5002E0C1: ADDRESS_MUGEN_WIN,
    0xC483FFFF: ADDRESS_MUGEN_100,
    0x89003983: ADDRESS_MUGEN_11A4,
    0x0094EC81: ADDRESS_MUGEN_11B1
}