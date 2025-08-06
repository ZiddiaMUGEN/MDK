## TODO: support the other MUGEN versions.

### read memory at this address to determine MUGEN version.
SELECT_VERSION_ADDRESS = 0x4405C0

### note: to find the SCTRL_BREAKPOINT_ADDR value search for `PlayerSCtrlApplyElem not recognised`.
### then look outward to find where the controllers are looped through.

ADDRESS_MUGEN_100 = {
    
}

ADDRESS_MUGEN_11A4 = {

}

## at SCTRL_BREAKPOINT_ADDR:
### ECX = controller index in state, EBP = player pointer
### if ECX = 0, EAX = state data pointer
### otherwise, EDX = state data pointer
ADDRESS_MUGEN_11B1 = {
    "SCTRL_BREAKPOINT_ADDR": 0x45C1F5,
    "SCTRL_PASSPOINT_ADDR": 0x45C243,
    "game": 0x5040E8,
    "player": 0x12278,
    "stateno": 0xCCC,
    "var": 0xF1C,
    "fvar": 0x100C,
    "triggers": {
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
        "ailevel": [0x2424, int]
    }
}

ADDRESS_DATABASE = {
    0xC483FFFF: ADDRESS_MUGEN_100,
    0x89003983: ADDRESS_MUGEN_11A4,
    0x0094EC81: ADDRESS_MUGEN_11B1
}