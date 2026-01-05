;; inputs:
;; ECX - state controller index
;; EBP - player address

;; variables:
;; EAX - root address, then breakpoint detail ptr
;; EDX - player 1 address
;; EBX - current stateno
;; EDI - stateowner address

;; addresses:
;; 0x5040E8 - game address
;; 0x4DD970 - passpoint list
;; 0x4DDB94 - step character address

;; set origin for relative jumps...
bits 32
org 0x4DDA50

;; preserve registers
push eax
push ebx
push edx
push edi

;; if the current character address equals the step character address,
;; always break.
mov eax,[0x4DDB94]
cmp eax, ebp
je .breakpoint

;; need to do some work to check if the current player is eligible for BPs
;; fetch root address and p1 address and stateowner root address
;;; root
mov eax,ebp
mov eax,[eax+0x1650]
;;; stateowner root
xor edi,edi
mov edx,[ebp+0xCB8]
;; skip if the stateowner ID is -1 (not custom stated)
cmp edx,-1
je .readp1
sub edx,1
mov edi,[0x5040E8]
add edi,0x12278
mov edi,[edi + edx * 4]
mov edi,[edi+0x1650]
;;; p1
.readp1:
mov edx,[0x5040E8]
mov edx,[edx+0x12278]
;; if character address == p1 address, this is p1. check bps
cmp ebp,edx
je .check_breakpoints
;; if stateowner root address == p1 address, this is a custom stated enemy. check bps
cmp edi,edx
je .check_breakpoints
;; if character address == root address, this is a p1-owned Helper. check bps
cmp eax,edx
je .check_breakpoints
;; skip as the character is ineligible (p2 side running its own states)
jmp .reset

.check_breakpoints:
;; set up the BP list in EAX and the stateno in EBX
mov eax,0x4DD970
mov ebx,ebp
mov ebx,[ebx+0xCCC]

.loop_breaks:
;; EAX is a stateno and EAX+4 is a controller index.
;; iterate each BP pointed to by EAX until one is -1; if it's -1, quit, no BP matched.
cmp dword [eax],0xFFFFFFFF
je .reset
;; compare EAX to the current stateno
cmp [eax],ebx
jne .continue
;; retrieve the stored controller index
mov edx,[ebp+0x5C]
;; compare EAX+4 to the current controller index
cmp [eax+0x04],edx
jne .continue
.breakpoint:
nop ;; DO NOT REMOVE, THIS IS THE BREAKPOINT ADDRESS
;; after BP, reset to MUGEN processing
jmp .reset

.continue:
;; skip to next entry in BP list.
add eax,08
jmp .loop_breaks

.reset:
pop edi
pop edx
pop ebx
pop eax
;; this is a requirement on MUGEN end.
call 0x448A20
jmp 0x45BCE8
