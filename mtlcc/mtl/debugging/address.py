## TODO: support the other MUGEN versions.

### read memory at this address to determine MUGEN version.
SELECT_VERSION_ADDRESS = 0x4405C0

### note: to find the SCTRL_BREAKPOINT_INSERT value search for `PlayerSCtrlApplyElem not recognised`.
### then look outward to find where the controllers are looped through.

ADDRESS_MUGEN_100 = {
    
}

ADDRESS_MUGEN_11A4 = {

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
    "SCTRL_BREAKPOINT_ADDR": 0x4DD9FF, # address inside the function to break at
    "SCTRL_PASSPOINT_ADDR": 0x4DDA92, # address inside the function to break at
    "SCTRL_BREAKPOINT_FUNC": [
        0x50, 0x53, 0x52, # pushes
        0x8B, 0xC5, 0x90, # mov eax, ebp; nop
        0x8B, 0x80, 0x50, 0x16, 0x00, 0x00, # mov eax, [eax + 1650]
        0x8B, 0x15, 0xE8, 0x40, 0x50, 0x00, # mov edx, [0x5040e8]
        0x8B, 0x92, 0x78, 0x22, 0x01, 0x00, # mov edx, [edx+12278]
        0x39, 0xD5, # cmp ebp, edx
        0x74, 0x04, # je .check_breakpoints
        0x39, 0xD0, # cmp eax, edx
        0x75, 0x27, # jne .reset
        0xB8, 0x20, 0xD9, 0x4D, 0x00, # mov eax, 0x4dd920
        0x8B, 0xDD, 0x90, # mov ebx, ebp; nop
        0x8B, 0x9B, 0xCC, 0x0C, 0x00, 0x00, # mov ebx, [ebx+ccc]
        0x81, 0x38, 0xFF, 0xFF, 0xFF, 0xFF, # cmp [eax], ffffffff
        0x74, 0x11, # je .reset
        0x39, 0x18, # cmp [eax], ebx
        0x75, 0x08, # jne .continue
        0x39, 0x48, 0x04, # cmp [eax+4], ecx
        0x75, 0x03, # jne .continue
        0x90, # nop <-- THIS IS WHERE THE BP IS PLACED
        0xEB, 0x05, # jmp .reset
        0x83, 0xC0, 0x08, # add eax,8
        0xEB, 0xE7, # jmp .loop_breaks
        0x5A, 0x5B, 0x58, # pops
        0x89, 0x4D, 0x5C, ## put ECX somewhere safe (player + 0x5c, const(player.attack.z.width.front))
        0x83, 0x3E, 0x00, # cmp [esi], 0
        0x0F, 0x85, 0x49, 0xE8, 0xF7, 0xFF, # jne 45C25F
        0xE9, 0xDF, 0xE7, 0xF7, 0xFF # jmp 45c1fa
    ],
    "SCTRL_PASSPOINT_FUNC": [
        0x50, 0x53, 0x52, # pushes
        0x8B, 0xC5, 0x90, # mov eax, ebp; nop
        0x8B, 0x80, 0x50, 0x16, 0x00, 0x00, # mov eax, [eax + 1650]
        0x8B, 0x15, 0xE8, 0x40, 0x50, 0x00, # mov edx, [0x5040e8]
        0x8B, 0x92, 0x78, 0x22, 0x01, 0x00, # mov edx, [edx+12278]
        0x39, 0xD5, # cmp ebp, edx
        0x74, 0x04, # je .check_breakpoints
        0x39, 0xD0, # cmp eax, edx
        0x75, 0x2A, # jne .reset
        0xB8, 0x70, 0xD9, 0x4D, 0x00, # mov eax, 0x4dd970
        0x8B, 0xDD, 0x90, # mov ebx, ebp; nop
        0x8B, 0x9B, 0xCC, 0x0C, 0x00, 0x00, # mov ebx, [ebx+ccc]
        0x81, 0x38, 0xFF, 0xFF, 0xFF, 0xFF, # cmp [eax], ffffffff
        0x74, 0x14, # je .reset
        0x39, 0x18, # cmp [eax], ebx
        0x75, 0x0B, # jne .continue
        0x8B, 0x5D, 0x5C, # mov ebx,[ebp+5c]
        0x39, 0x58, 0x04, # cmp [eax+4], ebx
        0x75, 0x03, # jne .continue
        0x90, # nop <-- THIS IS WHERE THE BP IS PLACED
        0xEB, 0x05, # jmp .reset
        0x83, 0xC0, 0x08, # add eax,8
        0xEB, 0xE4, # jmp .loop_breaks
        0x5A, 0x5B, 0x58, # pops
        0xE8, 0xAE, 0xB4, 0xF6, 0xFF, # call 0x448f50
        0xE9, 0xA1, 0xE7, 0xF7, 0xFF # jmp 45c248
    ],
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