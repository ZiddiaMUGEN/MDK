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
    "game": 0x5040E8,
    "player": 0x12278
}

ADDRESS_DATABASE = {
    0xC483FFFF: ADDRESS_MUGEN_100,
    0x89003983: ADDRESS_MUGEN_11A4,
    0x0094EC81: ADDRESS_MUGEN_11B1
}