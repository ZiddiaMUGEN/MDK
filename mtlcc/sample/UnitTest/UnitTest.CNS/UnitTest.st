;!mtl-debug VERSION_HEADER 20250729.01

;!mtl-debug TYPE_DEFINITION vector BUILTIN_STRUCTURE 32 /home/jsmith/MDK/mtlcc/mtl/builtins.py:23
;!mtl-debug-next X:float
;!mtl-debug-next Y:float
;!mtl-debug TYPE_DEFINITION prefixed_int UNION 32 /home/jsmith/MDK/mtlcc/mtl/builtins.py:93
;!mtl-debug-next cint
;!mtl-debug-next int
;!mtl-debug TYPE_DEFINITION sprite ALIAS 32 /home/jsmith/MDK/mtlcc/mtl/builtins.py:94
;!mtl-debug-next prefixed_int
;!mtl-debug TYPE_DEFINITION sound ALIAS 32 /home/jsmith/MDK/mtlcc/mtl/builtins.py:95
;!mtl-debug-next prefixed_int
;!mtl-debug TYPE_DEFINITION anim ALIAS 32 /home/jsmith/MDK/mtlcc/mtl/builtins.py:96
;!mtl-debug-next prefixed_int
;!mtl-debug TYPE_DEFINITION StateNo UNION 32 /home/jsmith/MDK/mtlcc/mtl/builtins.py:98
;!mtl-debug-next int
;!mtl-debug-next state

;!mtl-debug VARIABLE_TABLE StateScopeType.SHARED None 60
;!mtl-debug-next 0 1
;!mtl-debug VARIABLE_ALLOCATION myGlobal bool /home/jsmith/MDK/mtlcc/sample/UnitTest/UnitTest.states0.mtl:6
;!mtl-debug-next 0 0 var(0) & 1
;!mtl-debug VARIABLE_TABLE StateScopeType.SHARED None 40
;!mtl-debug VARIABLE_TABLE StateScopeType.PLAYER None 60
;!mtl-debug-next 0 1
;!mtl-debug VARIABLE_ALLOCATION myGlobal bool /home/jsmith/MDK/mtlcc/sample/UnitTest/UnitTest.states0.mtl:6
;!mtl-debug-next 0 0 var(0) & 1
;!mtl-debug VARIABLE_TABLE StateScopeType.PLAYER None 40
;!mtl-debug VARIABLE_TABLE StateScopeType.HELPER None 60
;!mtl-debug-next 0 1
;!mtl-debug VARIABLE_ALLOCATION myGlobal bool /home/jsmith/MDK/mtlcc/sample/UnitTest/UnitTest.states0.mtl:6
;!mtl-debug-next 0 0 var(0) & 1
;!mtl-debug VARIABLE_TABLE StateScopeType.HELPER None 40
;!mtl-debug VARIABLE_TABLE StateScopeType.TARGET None 60
;!mtl-debug VARIABLE_TABLE StateScopeType.TARGET None 40

;!mtl-debug STATEDEF STAND 0
[Statedef 0];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:21
type = S
physics = S
sprpriority = 0

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:27
type = ChangeAnim
trigger1 = ((Anim != 0) && (Anim != 5));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:29
trigger2 = ((Anim = 5) && (AnimTime = 0));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:30
value = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:31

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:33
type = VelSet
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:35
y = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:36

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:38
type = VelSet
trigger1 = ((abs(Vel x)) < (Const(movement.stand.friction.threshold)));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:40
trigger2 = (Time = 4);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:41
x = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:42

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:44
type = ChangeState
trigger1 = (!Alive);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:46
value = 5050;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:47
ctrl = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:48


;!mtl-debug STATEDEF STAND_TO_CROUCH 10
[Statedef 10];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:52
type = C
physics = C
anim = 10

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:58
type = VelMul
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:60
x = .75;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:61

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:63
type = VelSet
trigger1 = ((abs(Vel x)) < (Const(movement.crouch.friction.threshold)));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:65
x = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:66

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:68
type = ChangeState
trigger1 = (AnimTime = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:70
value = 11;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:71


;!mtl-debug STATEDEF CROUCH 11
[Statedef 11];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:75
type = C
physics = C
anim = 11
sprpriority = 0

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:82
type = ChangeAnim
trigger1 = ((Anim = 6) && (AnimTime = 0));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:84
value = 11;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:85

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:87
type = VelSet
trigger1 = ((abs(Vel x)) < (Const(movement.crouch.friction.threshold)));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:89
x = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:90


;!mtl-debug STATEDEF CROUCH_TO_STAND 12
[Statedef 12];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:94
type = S
physics = S
anim = 12

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:100
type = ChangeState
trigger1 = (AnimTime = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:102
value = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:103


;!mtl-debug STATEDEF WALK 20
[Statedef 20];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:107
type = S
physics = S
sprpriority = 0

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:113
type = VelSet
trigger1 = (Command = "holdfwd");!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:115
x = (Const(velocity.walk.fwd.x));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:116

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:118
type = VelSet
trigger1 = (Command = "holdback");!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:120
x = (Const(velocity.walk.back.x));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:121

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:123
type = ChangeAnim
triggerall = (Vel x > 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:125
trigger1 = ((Anim != 20) && (Anim != 5));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:126
trigger2 = ((Anim = 5) && (AnimTime = 0));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:127
value = 20;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:128

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:130
type = ChangeAnim
triggerall = (Vel x < 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:132
trigger1 = ((Anim != 21) && (Anim != 5));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:133
trigger2 = ((Anim = 5) && (AnimTime = 0));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:134
value = 21;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:135


;!mtl-debug STATEDEF JUMP 40
[Statedef 40];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:139
;!mtl-debug VARIABLE_ALLOCATION jumpDirection byte /home/jsmith/MDK/mtlcc:0
;!mtl-debug-next 0 8 var(0) & 65280
type = S
physics = S
anim = 40
ctrl = 0
facep2 = 1
sprpriority = 1

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:149
type = VarSet
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:151
var(0) = ((((0) & 255) * 256) + (var(0) & -65281));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:152

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:154
type = VarSet
trigger1 = (Command = "holdfwd");!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:156
var(0) = ((((1) & 255) * 256) + (var(0) & -65281));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:157

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:159
type = VarSet
trigger1 = (Command = "holdback");!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:161
var(0) = (((((-1)) & 255) * 256) + (var(0) & -65281));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:162

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:164
type = VelSet
trigger1 = (AnimTime = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:166
x = cond(((var(0) & 65280) = 0), (Const(velocity.jump.neu.x)), cond(((var(0) & 65280) = 1), (Const(velocity.jump.fwd.x)), (Const(velocity.jump.back.x))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:167
y = (Const(velocity.jump.y));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:168

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:170
type = VelSet
trigger1 = (AnimTime = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:172
trigger1 = (PrevStateNo = 100);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:173
trigger1 = ((var(0) & 65280) = 1);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:174
x = (Const(velocity.runjump.fwd.x));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:175

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:177
type = ChangeState
trigger1 = (AnimTime = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:179
value = 50;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:180
ctrl = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:181


;!mtl-debug STATEDEF JUMP_AIR 45
[Statedef 45];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:185
;!mtl-debug VARIABLE_ALLOCATION jumpDirection byte /home/jsmith/MDK/mtlcc:0
;!mtl-debug-next 0 8 var(0) & 65280
type = A
physics = N
ctrl = 0
velset = 0, 0

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:193
type = ChangeAnim
trigger1 = (SelfAnimExist(44));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:195
value = 44;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:196

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:198
type = ChangeAnim
trigger1 = (!(SelfAnimExist(44)));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:200
value = 41;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:201

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:203
type = VarSet
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:205
var(0) = ((((0) & 255) * 256) + (var(0) & -65281));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:206

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:208
type = VarSet
trigger1 = (Command = "holdfwd");!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:210
var(0) = ((((1) & 255) * 256) + (var(0) & -65281));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:211

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:213
type = VarSet
trigger1 = (Command = "holdback");!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:215
var(0) = (((((-1)) & 255) * 256) + (var(0) & -65281));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:216

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:218
type = VelSet
trigger1 = (Time = 2);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:220
x = cond(((var(0) & 65280) = 0), (Const(velocity.airjump.neu.x)), cond(((var(0) & 65280) = 1), (Const(velocity.airjump.fwd.x)), (Const(velocity.airjump.back.x))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:221
y = (Const(velocity.airjump.y));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:222

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:224
type = ChangeState
trigger1 = (Time = 2);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:226
value = 50;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:227
ctrl = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:228


;!mtl-debug STATEDEF JUMP_UP 50
[Statedef 50];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:232
type = A
physics = A

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:238
type = Null
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:240
jumpDirection = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:241

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:243
type = ChangeAnim
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:245
value = cond((Vel x = 0), 41, cond((Vel x > 0), 42, 43));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:246

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:248
type = ChangeAnim
trigger1 = (Vel y > (Const720p((-8))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:250
trigger1 = (SelfAnimExist((Anim + 3)));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:251
trigger1 = ((Anim >= 41) && (Anim <= 43));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:252
value = (Anim + 3);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:253
persistent = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:254


;!mtl-debug STATEDEF JUMP_DOWN 51
[Statedef 51];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:258
type = A
physics = A

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:263
type = Null
trigger1 = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:265


;!mtl-debug STATEDEF JUMP_LAND 52
[Statedef 52];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:269
type = S
physics = S
anim = 47
ctrl = 0

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:276
type = VelSet
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:278
y = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:279

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:281
type = PosSet
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:283
y = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:284

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:286
type = CtrlSet
trigger1 = (Time = 3);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:288
value = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:289

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:291
type = VelSet
trigger1 = ((abs(Vel x)) < (Const(movement.stand.friction.threshold)));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:293
x = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:294

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:296
type = ChangeState
trigger1 = (AnimTime = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:298
value = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:299
ctrl = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:300


;!mtl-debug STATEDEF RUN_FORWARD 100
[Statedef 100];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:304
type = S
physics = S
anim = 100
sprpriority = 1

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:311
type = VelSet
trigger1 = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:313
x = (Const(velocity.run.fwd.x));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:314

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:316
type = AssertSpecial
trigger1 = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:318
flag = NoWalk;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:319

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:321
type = AssertSpecial
trigger1 = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:323
flag = NoAutoTurn;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:324

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:326
type = ChangeState
trigger1 = (Command != "holdfwd");!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:328
value = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:329


;!mtl-debug STATEDEF HOP_BACK 105
[Statedef 105];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:333
type = A
physics = A
anim = 105
ctrl = 0
sprpriority = 1

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:341
type = VelSet
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:343
x = (Const(velocity.run.back.x));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:344
y = (Const(velocity.run.back.y));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:345

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:347
type = CtrlSet
trigger1 = (Time = 2);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:349
value = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:350

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:352
type = ChangeState
trigger1 = (Vel Y > 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:354
trigger1 = (Pos Y >= 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:355
value = 106;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:356


;!mtl-debug STATEDEF HOP_BACK_LAND 106
[Statedef 106];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:360
type = S
physics = S
anim = 47
ctrl = 0

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:367
type = VelSet
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:369
y = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:370

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:372
type = PosSet
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:374
y = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:375

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:377
type = MakeDust
trigger1 = (Time = 2);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:379
pos = 0, 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:380
spacing = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:381

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:383
type = VelSet
trigger1 = ((abs(Vel x)) < (Const(movement.stand.friction.threshold)));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:385
x = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:386

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:388
type = ChangeState
trigger1 = (Time = 7);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:390
value = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:391
ctrl = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:392


;!mtl-debug STATEDEF GUARD 120
[Statedef 120];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:396
type = U
physics = U

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:401
type = ChangeAnim
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:403
value = cond((StateType = C), 121, cond((StateType = A), 122, 120));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:404

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:406
type = StateTypeSet
trigger1 = ((Time = 0) && (StateType = S));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:408
physics = S;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:409

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:411
type = StateTypeSet
trigger1 = ((Time = 0) && (StateType = C));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:413
physics = C;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:414

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:416
type = StateTypeSet
trigger1 = ((Time = 0) && (StateType = A));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:418
physics = A;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:419

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:421
type = StateTypeSet
trigger1 = ((StateType = S) && (Command = "holddown"));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:423
statetype = C;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:424
physics = C;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:425

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:427
type = StateTypeSet
trigger1 = ((StateType = C) && (Command != "holddown"));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:429
statetype = S;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:430
physics = S;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:431

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:433
type = ChangeState
trigger1 = (AnimTime = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:435
trigger1 = (StateType = C);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:436
value = 131;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:437

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:439
type = ChangeState
trigger1 = (AnimTime = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:441
trigger1 = (StateType = A);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:442
value = 132;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:443

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:445
type = ChangeState
trigger1 = (AnimTime = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:447
value = 130;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:448

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:450
type = ChangeState
trigger1 = (Command != "holdback");!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:452
trigger2 = (!InGuardDist);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:453
value = 140;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:454


;!mtl-debug STATEDEF GUARD_STAND 130
[Statedef 130];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:458
type = S
physics = S

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:463
type = ChangeAnim
trigger1 = (Anim != 130);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:465
value = 130;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:466

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:468
type = ChangeState
trigger1 = (Command = "holddown");!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:470
value = 131;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:471

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:473
type = ChangeState
trigger1 = (Command != "holdback");!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:475
trigger2 = (!InGuardDist);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:476
value = 140;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:477


;!mtl-debug STATEDEF GUARD_CROUCH 131
[Statedef 131];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:481
type = C
physics = C

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:486
type = ChangeAnim
trigger1 = (Anim != 131);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:488
value = 131;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:489

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:491
type = ChangeState
trigger1 = (Command != "holddown");!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:493
value = 130;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:494

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:496
type = ChangeState
trigger1 = (Command != "holdback");!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:498
trigger2 = (!InGuardDist);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:499
value = 140;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:500


;!mtl-debug STATEDEF GUARD_AIR 132
[Statedef 132];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:504
;!mtl-debug VARIABLE_ALLOCATION hasHitGround bool /home/jsmith/MDK/mtlcc:0
;!mtl-debug-next 0 8 var(0) & 256
type = A
physics = N

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:510
type = ChangeAnim
trigger1 = (Anim != 132);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:512
value = 132;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:513

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:515
type = VelAdd
trigger1 = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:517
y = (Const(movement.yaccel));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:518

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:520
type = VarSet
trigger1 = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:522
var(0) = ((((((pos y >= 0) && (vel y > 0))) & 1) * 256) + (var(0) & -257));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:523

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:525
type = VelSet
trigger1 = (var(0) & 256);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:527
y = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:528

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:530
type = PosSet
trigger1 = (var(0) & 256);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:532
y = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:533

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:535
type = ChangeState
trigger1 = (var(0) & 256);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:537
trigger1 = (Command = "holdback");!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:538
trigger1 = InGuardDist;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:539
value = 130;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:540

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:542
type = ChangeState
trigger1 = (var(0) & 256);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:544
value = 52;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:545

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:547
type = ChangeState
trigger1 = (Command != "holdback");!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:549
trigger2 = (!InGuardDist);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:550
value = 140;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:551


;!mtl-debug STATEDEF GUARD_STOP 140
[Statedef 140];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:555
type = U
physics = U
ctrl = 1

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:561
type = ChangeAnim
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:563
value = cond((StateType = C), 141, cond((StateType = A), 142, 140));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:564

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:566
type = StateTypeSet
trigger1 = ((Time = 0) && (StateType = S));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:568
physics = S;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:569

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:571
type = StateTypeSet
trigger1 = ((Time = 0) && (StateType = C));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:573
physics = C;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:574

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:576
type = StateTypeSet
trigger1 = ((Time = 0) && (StateType = A));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:578
physics = A;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:579

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:581
type = StateTypeSet
trigger1 = ((StateType = S) && (Command = "holddown"));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:583
statetype = C;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:584
physics = C;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:585

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:587
type = StateTypeSet
trigger1 = ((StateType = C) && (Command != "holddown"));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:589
statetype = S;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:590
physics = S;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:591


;!mtl-debug STATEDEF GUARD_STAND_SHAKE 150
[Statedef 150];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:600
type = S
movetype = H
physics = N
velset = 0, 0

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:607
type = ChangeAnim
trigger1 = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:609
value = 150;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:610

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:612
type = ChangeState
trigger1 = HitShakeOver;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:614
trigger1 = (Command = "holddown");!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:615
value = 153;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:616

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:618
type = ChangeState
trigger1 = HitShakeOver;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:620
value = 151;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:621

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:623
type = StateTypeSet
trigger1 = ((StateType = S) && (Command = "holddown"));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:625
statetype = C;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:626
physics = C;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:627

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:629
type = StateTypeSet
trigger1 = ((StateType = C) && (Command != "holddown"));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:631
statetype = S;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:632
physics = S;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:633

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:635
type = ForceFeedback
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:637
waveform = square;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:638
time = 3;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:639


;!mtl-debug STATEDEF GUARD_STAND_KNOCKBACK 151
[Statedef 151];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:643
type = S
movetype = H
physics = S
anim = 150

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:650
type = HitVelSet
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:652
x = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:653

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:655
type = VelSet
trigger1 = (Time = (GetHitVar(slidetime)));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:657
trigger2 = HitOver;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:658
x = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:659

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:661
type = CtrlSet
trigger1 = (Time = (GetHitVar(ctrltime)));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:663
value = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:664

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:666
type = StateTypeSet
trigger1 = ((StateType = S) && (Command = "holddown"));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:668
statetype = C;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:669
physics = C;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:670

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:672
type = StateTypeSet
trigger1 = ((StateType = C) && (Command != "holddown"));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:674
statetype = S;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:675
physics = S;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:676

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:678
type = ChangeState
trigger1 = HitOver;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:680
value = 130;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:681
ctrl = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:682


;!mtl-debug STATEDEF GUARD_CROUCH_SHAKE 152
[Statedef 152];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:686
type = C
movetype = H
physics = N
velset = 0, 0

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:693
type = ChangeAnim
trigger1 = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:695
value = 151;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:696

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:698
type = ChangeState
trigger1 = HitShakeOver;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:700
trigger1 = (Command = "holddown");!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:701
value = 153;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:702

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:704
type = ChangeState
trigger1 = HitShakeOver;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:706
value = 151;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:707

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:709
type = StateTypeSet
trigger1 = ((StateType = S) && (Command = "holddown"));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:711
statetype = C;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:712
physics = C;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:713

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:715
type = StateTypeSet
trigger1 = ((StateType = C) && (Command != "holddown"));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:717
statetype = S;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:718
physics = S;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:719

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:721
type = ForceFeedback
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:723
waveform = square;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:724
time = 4;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:725


;!mtl-debug STATEDEF GUARD_CROUCH_KNOCKBACK 153
[Statedef 153];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:729
type = C
movetype = H
physics = C
anim = 151

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:736
type = HitVelSet
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:738
x = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:739

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:741
type = VelSet
trigger1 = (Time = (GetHitVar(slidetime)));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:743
trigger2 = HitOver;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:744
x = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:745

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:747
type = CtrlSet
trigger1 = (Time = (GetHitVar(ctrltime)));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:749
value = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:750

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:752
type = StateTypeSet
trigger1 = ((StateType = S) && (Command = "holddown"));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:754
statetype = C;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:755
physics = C;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:756

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:758
type = StateTypeSet
trigger1 = ((StateType = C) && (Command != "holddown"));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:760
statetype = S;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:761
physics = S;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:762

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:764
type = ChangeState
trigger1 = HitOver;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:766
value = 131;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:767
ctrl = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:768


;!mtl-debug STATEDEF GUARD_AIR_SHAKE 154
[Statedef 154];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:772
type = A
movetype = H
physics = N
velset = 0, 0

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:779
type = ChangeAnim
trigger1 = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:781
value = 152;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:782

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:784
type = ChangeState
trigger1 = HitShakeOver;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:786
value = 155;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:787

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:789
type = ForceFeedback
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:791
waveform = square;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:792
time = 4;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:793


;!mtl-debug STATEDEF GUARD_AIR_KNOCKBACK 155
[Statedef 155];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:797
;!mtl-debug VARIABLE_ALLOCATION hasHitGround bool /home/jsmith/MDK/mtlcc:0
;!mtl-debug-next 0 8 var(0) & 256
type = A
movetype = H
physics = N
anim = 152

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:805
type = HitVelSet
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:807
x = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:808
y = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:809

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:811
type = VelAdd
trigger1 = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:813
y = (Const(movement.yaccel));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:814

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:816
type = CtrlSet
trigger1 = (Time = (GetHitVar(ctrltime)));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:818
value = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:819

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:821
type = VarSet
trigger1 = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:823
var(0) = ((((((pos y >= 0) && (vel y > 0))) & 1) * 256) + (var(0) & -257));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:824

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:826
type = VelSet
trigger1 = (var(0) & 256);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:828
y = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:829

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:831
type = PosSet
trigger1 = (var(0) & 256);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:833
y = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:834

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:836
type = ChangeState
trigger1 = (var(0) & 256);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:838
trigger1 = (Command = "holdback");!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:839
trigger1 = InGuardDist;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:840
value = 130;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:841

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:843
type = ChangeState
trigger1 = (var(0) & 256);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:845
value = 52;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:846


;!mtl-debug STATEDEF LOSE_TIME 170
[Statedef 170];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:850
type = S
anim = 170
ctrl = 0
velset = 0, 0

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:857
type = NotHitBy
trigger1 = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:859
value = SCA;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:860
time = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:861


;!mtl-debug STATEDEF DRAW_TIME 175
[Statedef 175];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:865
type = S
ctrl = 0
velset = 0, 0

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:871
type = ChangeState
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:873
trigger1 = (!(SelfAnimExist(175)));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:874
value = 170;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:875

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:877
type = ChangeAnim
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:879
value = 175;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:880

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:882
type = NotHitBy
trigger1 = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:884
value = SCA;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:885
time = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:886


;!mtl-debug STATEDEF STAND_HIT_SHAKE 5000
[Statedef 5000];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:920
type = S
movetype = H
physics = N
velset = 0, 0

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:927
type = ChangeAnim
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:929
trigger1 = ((GetHitVar(animtype)) != [3, 5]);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:930
value = (cond(((GetHitVar(groundtype)) = 1), 5000, 5010) + (floor((GetHitVar(animtype)))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:931

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:933
type = ChangeAnim
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:935
trigger1 = ((GetHitVar(animtype)) = [3, 5]);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:936
value = 5030;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:937

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:939
type = ChangeAnim
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:941
trigger1 = (((GetHitVar(animtype)) = [4, 5]) && (SelfAnimExist((5047 + (floor((GetHitVar(animtype))))))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:942
value = (5047 + (floor((GetHitVar(animtype)))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:943

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:945
type = ChangeAnim
trigger1 = (Time > 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:947
value = Anim;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:948

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:950
type = StateTypeSet
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:952
trigger1 = (((GetHitVar(yvel)) != 0) || (GetHitVar(fall)));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:953
trigger2 = (Pos Y != 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:954
statetype = A;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:955

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:957
type = ForceFeedback
trigger1 = (Anim = 5000);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:959
trigger2 = (Anim = 5010);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:960
persistent = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:961
time = 6;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:962
waveform = square;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:963

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:965
type = ForceFeedback
trigger1 = (Anim = 5001);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:967
trigger2 = (Anim = 5011);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:968
persistent = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:969
time = 8;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:970
waveform = sinesquare;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:971
ampl = 110, (-1), (-.3);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:972

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:974
type = ForceFeedback
trigger1 = (Anim = 5012);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:976
trigger2 = (Anim = 5002);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:977
trigger3 = (Anim = 5030);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:978
persistent = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:979
time = 15;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:980
waveform = sinesquare;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:981
ampl = 140;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:982

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:984
type = ChangeState
trigger1 = HitShakeOver;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:986
trigger1 = (((GetHitVar(yvel)) = 0) && (!(GetHitVar(fall))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:987
value = 5001;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:988

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:990
type = ChangeState
trigger1 = HitShakeOver;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:992
value = 5030;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:993


;!mtl-debug STATEDEF STAND_HIT_KNOCKBACK 5001
[Statedef 5001];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:997
type = S
movetype = H
physics = S

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1003
type = HitVelSet
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1005
x = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1006

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1008
type = ChangeAnim
trigger1 = (AnimTime = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1010
value = ((5005 + (floor((GetHitVar(animtype))))) + cond(((GetHitVar(groundtype)) = 2), 10, 0));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1011

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1013
type = VelMul
trigger1 = (Time >= (GetHitVar(slidetime)));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1015
x = .6;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1016

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1018
type = VelSet
trigger1 = HitOver;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1020
x = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1021

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1023
type = DefenceMulSet
trigger1 = HitOver;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1025
value = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1026

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1028
type = ChangeState
trigger1 = HitOver;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1030
value = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1031
ctrl = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1032


;!mtl-debug STATEDEF CROUCH_HIT_SHAKE 5010
[Statedef 5010];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1036
type = C
movetype = H
physics = N
velset = 0, 0

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1043
type = ChangeAnim
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1045
trigger1 = ((GetHitVar(animtype)) != [3, 5]);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1046
value = (5020 + (floor((GetHitVar(animtype)))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1047

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1049
type = ChangeAnim
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1051
trigger1 = ((GetHitVar(animtype)) = [3, 5]);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1052
value = 5030;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1053

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1055
type = ChangeAnim
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1057
trigger1 = (((GetHitVar(animtype)) = [4, 5]) && (SelfAnimExist((5047 + (floor((GetHitVar(animtype))))))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1058
value = (5047 + (floor((GetHitVar(animtype)))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1059

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1061
type = ChangeAnim
trigger1 = (Time > 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1063
value = Anim;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1064

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1066
type = StateTypeSet
triggerall = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1068
trigger1 = (((GetHitVar(yvel)) != 0) || (GetHitVar(fall)));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1069
trigger2 = (Pos Y != 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1070
statetype = A;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1071

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1073
type = ChangeState
trigger1 = HitShakeOver;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1075
trigger1 = (((GetHitVar(yvel)) = 0) && (!(GetHitVar(fall))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1076
value = 5011;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1077

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1079
type = ChangeState
trigger1 = HitShakeOver;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1081
value = 5030;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1082

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1084
type = ForceFeedback
trigger1 = (Anim = 5020);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1086
persistent = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1087
time = 6;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1088
waveform = square;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1089

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1091
type = ForceFeedback
trigger1 = (Anim = 5021);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1093
persistent = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1094
time = 8;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1095
waveform = sinesquare;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1096
ampl = 110, (-1), (-.3);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1097

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1099
type = ForceFeedback
trigger1 = (Anim = 5022);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1101
persistent = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1102
time = 15;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1103
waveform = sinesquare;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1104
ampl = 140;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1105


;!mtl-debug STATEDEF CROUCH_HIT_KNOCKBACK 5011
[Statedef 5011];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1109
type = C
movetype = H
physics = C

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1115
type = HitVelSet
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1117
x = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1118

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1120
type = ChangeAnim
trigger1 = (AnimTime = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1122
value = (5025 + (floor((GetHitVar(animtype)))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1123

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1125
type = VelMul
trigger1 = (Time >= (GetHitVar(slidetime)));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1127
x = .6;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1128

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1130
type = VelSet
trigger1 = HitOver;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1132
x = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1133

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1135
type = DefenceMulSet
trigger1 = HitOver;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1137
value = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1138

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1140
type = ChangeState
trigger1 = HitOver;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1142
value = 11;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1143
ctrl = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1144


;!mtl-debug STATEDEF AIR_HIT_SHAKE 5020
[Statedef 5020];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1148
type = A
movetype = H
physics = N
velset = 0, 0

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1155
type = ChangeAnim
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1157
trigger1 = ((GetHitVar(animtype)) != [3, 5]);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1158
value = (cond(((GetHitVar(airtype)) = 1), 5000, 5010) + (floor((GetHitVar(animtype)))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1159

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1161
type = ChangeAnim
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1163
trigger1 = ((GetHitVar(animtype)) = [3, 5]);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1164
value = 5030;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1165

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1167
type = ChangeAnim
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1169
trigger1 = (((GetHitVar(animtype)) = [4, 5]) && (SelfAnimExist((5047 + (floor((GetHitVar(animtype))))))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1170
value = (5047 + (floor((GetHitVar(animtype)))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1171

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1173
type = ChangeAnim
trigger1 = (Time > 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1175
value = Anim;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1176

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1178
type = ChangeState
trigger1 = HitShakeOver;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1180
value = 5030;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1181

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1183
type = ForceFeedback
trigger1 = (Anim = 5000);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1185
trigger2 = (Anim = 5010);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1186
persistent = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1187
time = 6;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1188
waveform = square;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1189

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1191
type = ForceFeedback
trigger1 = (Anim = 5001);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1193
trigger2 = (Anim = 5011);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1194
persistent = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1195
time = 8;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1196
waveform = sinesquare;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1197
ampl = 110, (-1), (-.3);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1198

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1200
type = ForceFeedback
trigger1 = (Anim = 5012);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1202
trigger2 = (Anim = 5002);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1203
trigger3 = (Anim = 5030);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1204
trigger4 = (Anim = [5051, 5059]);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1205
persistent = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1206
time = 15;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1207
waveform = sinesquare;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1208
ampl = 140;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1209


;!mtl-debug STATEDEF AIR_HIT_KNOCKBACK 5030
[Statedef 5030];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1213
type = A
movetype = H
physics = N
ctrl = 0

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1220
type = ChangeAnim
trigger1 = (Anim != [5000, 5199]);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1222
trigger1 = (SelfAnimExist(5030));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1223
value = 5030;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1224

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1226
type = VelAdd
trigger1 = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1228
y = (GetHitVar(yaccel));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1229

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1231
type = HitVelSet
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1233
x = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1234
y = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1235

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1237
type = ChangeState
triggerall = (!HitFall);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1239
trigger1 = HitOver;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1240
trigger2 = (Vel Y > 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1241
trigger2 = (Pos Y >= (Const(movement.air.gethit.groundlevel)));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1242
value = 5040;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1243

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1245
type = ChangeState
triggerall = HitFall;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1247
trigger1 = HitOver;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1248
trigger2 = (Vel Y > 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1249
trigger2 = (Pos Y >= (Const(movement.air.gethit.groundlevel)));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1250
value = 5050;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1251

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1253
type = ChangeState
trigger1 = (AnimTime = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1255
value = 5035;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1256


;!mtl-debug STATEDEF AIR_HIT_TRANSITION 5035
[Statedef 5035];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1260
type = A
movetype = H
physics = N

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1266
type = ChangeAnim
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1268
trigger1 = (SelfAnimExist(5035));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1269
trigger1 = (Anim != [5051, 5059]);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1270
trigger1 = (Anim != 5090);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1271
value = 5035;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1272

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1274
type = VelAdd
trigger1 = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1276
y = (GetHitVar(yaccel));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1277

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1279
type = ChangeState
triggerall = (!HitFall);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1281
trigger1 = HitOver;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1282
trigger2 = (AnimTime = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1283
trigger3 = (Vel Y > 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1284
trigger3 = (Pos Y >= (Const(movement.air.gethit.groundlevel)));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1285
trigger4 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1286
trigger4 = (Anim != 5035);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1287
value = 5040;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1288

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1290
type = ChangeState
triggerall = HitFall;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1292
trigger1 = HitOver;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1293
trigger2 = (AnimTime = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1294
trigger3 = (Vel Y > 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1295
trigger3 = (Pos Y >= (Const(movement.air.gethit.groundlevel)));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1296
trigger4 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1297
trigger4 = (Anim != 5035);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1298
value = 5050;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1299


;!mtl-debug STATEDEF AIR_HIT_RECOVER 5040
[Statedef 5040];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1303
type = A
movetype = H
physics = N

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1309
type = ChangeState
trigger1 = (!Alive);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1311
value = 5050;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1312
ctrl = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1313

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1315
type = ChangeAnim
trigger1 = (AnimTime = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1317
trigger1 = (Anim != 5040);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1318
trigger2 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1319
trigger2 = (Anim != 5035);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1320
value = 5040;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1321

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1323
type = CtrlSet
trigger1 = HitOver;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1325
value = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1326

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1328
type = StateTypeSet
trigger1 = HitOver;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1330
movetype = I;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1331

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1333
type = VelAdd
trigger1 = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1335
y = (GetHitVar(yaccel));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1336

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1338
type = ChangeState
trigger1 = (Vel Y > 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1340
trigger1 = (Pos Y >= 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1341
value = 52;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1342


;!mtl-debug STATEDEF AIR_HIT_FALL 5050
[Statedef 5050];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1346
type = A
movetype = H
physics = N

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1352
type = ChangeAnim
trigger1 = (AnimTime = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1354
trigger1 = (Anim = 5035);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1355
trigger2 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1356
trigger2 = (Anim != 5035);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1357
trigger2 = ((Anim != [5051, 5059]) && (Anim != [5061, 5069]));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1358
trigger2 = (Anim != 5090);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1359
value = 5050;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1360

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1362
type = ChangeAnim
trigger1 = (Anim = [5050, 5059]);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1364
trigger1 = (Vel Y >= cond((Anim = 5050), (Const720p(4)), (Const720p((-8)))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1365
trigger1 = (SelfAnimExist((Anim + 10)));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1366
value = (Anim + 10);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1367
persistent = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1368

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1370
type = VelAdd
trigger1 = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1372
y = (GetHitVar(yaccel));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1373

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1375
type = ChangeState
triggerall = (Vel Y > 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1377
triggerall = (Pos Y >= (Const(movement.air.gethit.groundrecover.ground.threshold)));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1378
triggerall = Alive;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1379
triggerall = CanRecover;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1380
trigger1 = (Command = "recovery");!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1381
value = 5200;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1382

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1384
type = ChangeState
triggerall = (Vel Y > (Const(movement.air.gethit.airrecover.threshold)));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1386
triggerall = Alive;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1387
triggerall = CanRecover;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1388
trigger1 = (Command = "recovery");!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1389
value = 5210;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1390

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1392
type = ChangeState
trigger1 = (Vel Y > 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1394
trigger1 = (Pos Y >= cond(((Anim = [5051, 5059]) || (Anim = [5061, 5069])), 0, (Const(movement.air.gethit.groundlevel))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1395
value = 5100;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1396


;!mtl-debug STATEDEF TRIP_HIT_SHAKE 5070
[Statedef 5070];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1400
type = A
movetype = H
physics = N
velset = 0, 0

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1407
type = ChangeAnim
trigger1 = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1409
value = 5070;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1410

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1412
type = ChangeState
trigger1 = HitShakeOver;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1414
value = 5071;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1415

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1417
type = ForceFeedback
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1419
time = 12;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1420
waveform = sinesquare;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1421
ampl = 140;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1422


;!mtl-debug STATEDEF TRIP_HIT_KNOCKBACK 5071
[Statedef 5071];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1426
type = A
movetype = H
physics = N

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1432
type = HitVelSet
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1434
x = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1435
y = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1436

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1438
type = VelAdd
trigger1 = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1440
y = (GetHitVar(yaccel));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1441

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1443
type = ChangeState
trigger1 = (Vel Y > 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1444
trigger1 = (Pos Y >= (Const(movement.air.gethit.trip.groundlevel)));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1445
value = 5110;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1447


;!mtl-debug STATEDEF DOWN_HIT_SHAKE 5080
[Statedef 5080];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1451
;!mtl-debug VARIABLE_ALLOCATION downedAnim int /home/jsmith/MDK/mtlcc:0
;!mtl-debug-next 1 0 var(1)
type = L
movetype = H
physics = N
velset = 0, 0

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1459
type = VarSet
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1461
var(1) = cond(((GetHitVar(yvel)) = 0), 5080, 5090);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1462

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1464
type = VarAdd
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1466
trigger1 = ((Anim = [5081, 5089]) || (Anim = [5111, 5119]));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1467
trigger1 = (SelfAnimExist(((var(1)) + (Anim / 10))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1468
var(1) = (Anim / 10);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1469

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1471
type = VarSet
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1473
trigger1 = ((var(1)) = 5090);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1474
trigger1 = (!(SelfAnimExist(5090)));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1475
var(1) = 5030;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1476

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1478
type = ChangeAnim
trigger1 = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1480
value = (var(1));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1481

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1483
type = ChangeState
trigger1 = HitShakeOver;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1485
trigger1 = ((GetHitVar(yvel)) = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1486
value = 5081;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1487

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1489
type = ChangeState
trigger1 = HitShakeOver;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1491
trigger1 = ((GetHitVar(yvel)) != 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1492
value = 5030;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1493


;!mtl-debug STATEDEF DOWN_HIT_KNOCKBACK 5081
[Statedef 5081];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1497
;!mtl-debug VARIABLE_ALLOCATION preventShowGroundFrame bool /home/jsmith/MDK/mtlcc:0
;!mtl-debug-next 0 8 var(0) & 256
type = L
movetype = H
physics = C

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1504
type = HitVelSet
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1506
x = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1507

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1509
type = VelSet
trigger1 = HitOver;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1511
x = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1512

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1514
type = VarSet
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1516
var(0) = ((((1) & 1) * 256) + (var(0) & -257));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1517

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1519
type = ChangeState
trigger1 = HitOver;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1521
triggerall = (((var(0)) := ((((((var(0)) & 256) / 256) & 1) * 256) + ((var(0)) & (-257)))) || 1);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1523
value = 5110;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1522


;!mtl-debug STATEDEF DOWN_HIT_GROUND 5100
[Statedef 5100];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1527
;!mtl-debug VARIABLE_ALLOCATION fallVelocity int /home/jsmith/MDK/mtlcc:0
;!mtl-debug-next 1 0 var(1)
type = L
movetype = H
physics = N

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1534
type = Null
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1536
trigger1 = ((GetHitVar(fall.yvel)) = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1537
trigger1 = (vel x < (-1));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1538
x = (-1);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1539

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1541
type = FallEnvShake
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1543

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1545
type = VarSet
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1547
var(1) = (floor(vel y));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1548

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1550
type = ChangeAnim
triggerall = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1552
trigger1 = ((Anim != [5051, 5059]) && (Anim != [5061, 5069]));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1553
trigger2 = (!(SelfAnimExist((5100 + (Anim / 10)))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1554
value = 5100;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1555

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1557
type = ChangeAnim
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1559
trigger1 = ((Anim = [5051, 5059]) || (Anim = [5061, 5069]));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1560
trigger1 = (SelfAnimExist((5100 + (Anim / 10))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1561
value = (5100 + (Anim / 10));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1562

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1564
type = PosSet
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1566
y = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1567

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1569
type = VelSet
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1571
y = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1572

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1574
type = VelMul
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1576
x = 0.75;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1577

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1579
type = ChangeState
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1581
trigger1 = ((GetHitVar(fall.yvel)) = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1582
value = 5110;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1583

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1585
type = Explod
trigger1 = (Time = 1);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1587
anim = (F(((60 + (btoi(((var(1)) > (Const720p(20)))))) + (btoi(((var(1)) > (Const720p(56))))))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1588
postype = none;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1589
pos = (Pos x + CameraPos x), 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1590
facing = Facing;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1591
sprpriority = cond(((var(1)) <= (Const720p(56))), (-10), 10);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1592

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1594
type = HitFallDamage
trigger1 = (Time = 3);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1596

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1598
type = PlaySnd
trigger1 = (Time = 1);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1600
value = F7, (cond(((var(1)) > (Const720p(20))), 1, 0) + cond(((var(1)) > (Const720p(56))), 1, 0));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1601

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1603
type = PosFreeze
trigger1 = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1605

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1607
type = ChangeState
trigger1 = (AnimTime = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1609
value = 5101;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1610

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1612
type = ForceFeedback
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1614
waveform = sinesquare;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1615
ampl = 128, (-3), (-.2), .005;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1616
time = 20;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1617


;!mtl-debug STATEDEF DOWN_HIT_BOUNCE 5101
[Statedef 5101];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1621
type = L
movetype = H
physics = N

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1627
type = ChangeAnim
triggerall = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1629
trigger1 = (Anim != [5101, 5109]);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1630
trigger2 = (!(SelfAnimExist((5160 + (Anim / 10)))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1631
value = 5160;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1632

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1634
type = ChangeAnim
triggerall = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1636
trigger1 = (Anim = [5101, 5109]);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1637
trigger1 = (SelfAnimExist((5160 + (Anim / 10))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1638
value = (5160 + (Anim / 10));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1639

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1641
type = HitFallVel
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1643

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1645
type = PosSet
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1647
y = (Const(movement.down.bounce.offset.y));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1648

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1650
type = PosAdd
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1652
x = (Const(movement.down.bounce.offset.x));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1653

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1655
type = VelAdd
trigger1 = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1657
y = (Const(movement.down.bounce.yaccel));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1658

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1660
type = ChangeState
trigger1 = (Vel Y > 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1661
trigger1 = (Pos Y >= (Const(movement.down.bounce.groundlevel)));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1662
value = 5110;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1664


;!mtl-debug STATEDEF DOWN_HIT_LIEDOWN 5110
[Statedef 5110];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1668
;!mtl-debug VARIABLE_ALLOCATION preventShowGroundFrame bool /home/jsmith/MDK/mtlcc:0
;!mtl-debug-next 0 8 var(0) & 256
;!mtl-debug VARIABLE_ALLOCATION fallVelocity int /home/jsmith/MDK/mtlcc:0
;!mtl-debug-next 1 0 var(1)
type = L
movetype = H
physics = N

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1676
type = FallEnvShake
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1678

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1680
type = ChangeAnim
trigger1 = (SelfAnimExist((5110 + (Anim / 10))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1682
trigger1 = (Anim = [5081, 5089]);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1683
value = (5110 + (Anim / 10));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1684
persistent = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1685

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1687
type = ChangeAnim
triggerall = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1689
triggerall = (Anim != [5110, 5119]);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1690
trigger1 = (Anim != [5161, 5169]);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1691
trigger2 = (!(SelfAnimExist((5170 + (Anim / 10)))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1692
value = 5170;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1693

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1695
type = ChangeAnim
triggerall = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1697
triggerall = (Anim != [5110, 5119]);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1698
trigger1 = (Anim = [5161, 5169]);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1699
trigger1 = (SelfAnimExist((5170 + (Anim / 10))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1700
value = (5170 + (Anim / 10));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1701

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1703
type = HitFallDamage
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1705

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1707
type = PosSet
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1709
y = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1710

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1712
type = VarSet
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1714
trigger1 = ((GetHitVar(fall.yvel)) != 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1715
var(1) = (floor(vel y));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1716

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1718
type = PlaySnd
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1720
trigger1 = (!(var(0) & 256));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1721
value = F7, (cond(((var(1)) > (Const720p(20))), 1, 0) + cond(((var(1)) > (Const720p(56))), 1, 0));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1722

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1724
type = Explod
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1726
trigger1 = (!(var(0) & 256));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1727
anim = (F(((60 + (btoi(((var(1)) > (Const720p(20)))))) + (btoi(((var(1)) > (Const720p(56))))))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1728
postype = none;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1729
pos = (Pos x + CameraPos x), 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1730
facing = Facing;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1731
sprpriority = cond(((var(1)) <= (Const720p(56))), (-10), 10);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1732

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1734
type = VelSet
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1736
y = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1737

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1739
type = ChangeAnim
triggerall = (Anim = [5171, 5179]);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1742
triggerall = (SelfAnimExist((5110 + (Anim / 10))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1743
trigger1 = (AnimTime = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1744
trigger2 = (var(0) & 256);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1745
persistent = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1741
value = (5110 + (Anim / 10));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1746

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1748
type = ChangeAnim
triggerall = (Anim != [5111, 5119]);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1750
trigger1 = (AnimTime = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1751
trigger2 = (var(0) & 256);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1752
value = 5110;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1753
persistent = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1754

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1756
type = ChangeState
triggerall = (!Alive);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1758
trigger1 = (AnimTime = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1759
trigger2 = (var(0) & 256);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1760
trigger3 = (Anim = [5110, 5119]);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1761
value = 5150;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1762

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1765
type = VarSet
trigger1 = (var(0) & 256);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1767
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1768
var(0) = ((((0) & 1) * 256) + (var(0) & -257));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1769

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1771
type = VelMul
trigger1 = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1773
x = 0.85;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1774

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1776
type = VelSet
trigger1 = ((abs(Vel x)) < (Const(movement.down.friction.threshold)));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1778
x = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1779
persistent = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1780

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1782
type = ForceFeedback
trigger1 = Alive;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1784
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1785
time = 8;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1786
ampl = 240;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1787
waveform = sine;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1788

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1790
type = ForceFeedback
trigger1 = (!Alive);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1792
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1793
ampl = 200, 7, (-.467);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1794
time = 30;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1795
waveform = sine;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1796


;!mtl-debug STATEDEF DOWN_HIT_GETUP 5120
[Statedef 5120];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1800
type = L
movetype = I
physics = N

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1806
type = ChangeAnim
triggerall = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1808
trigger1 = (Anim != [5111, 5119]);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1809
trigger2 = (!(SelfAnimExist((5120 + (Anim / 10)))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1810
value = 5120;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1811

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1813
type = ChangeAnim
triggerall = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1815
trigger1 = (Anim = [5111, 5119]);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1816
trigger1 = (SelfAnimExist((5120 + (Anim / 10))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1817
value = (5120 + (Anim / 10));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1818

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1820
type = VelSet
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1822
x = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1823

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1825
type = NotHitBy
trigger1 = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1827
value = SCA;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1828
time = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1829

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1831
type = HitFallSet
trigger1 = (AnimTime = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1833
value = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1834

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1836
type = NotHitBy
trigger1 = (AnimTime = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1838
value = , NT, ST, HT;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1839
time = 12;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1840

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1842
type = NotHitBy
trigger1 = (AnimTime = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1844
value2 = SCA;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1845
time = 3;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1846

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1848
type = ChangeState
trigger1 = (AnimTime = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1850
value = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1851
ctrl = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1852


;!mtl-debug STATEDEF DOWN_DEFEATED 5150
[Statedef 5150];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1856
type = L
movetype = H
physics = N
ctrl = 0
sprpriority = -3

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1864
type = ChangeAnim
triggerall = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1866
triggerall = (SelfAnimExist(5140));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1867
trigger1 = ((Anim != [5111, 5119]) && (Anim != [5171, 5179]));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1868
trigger2 = (!(SelfAnimExist((5140 + (Anim / 10)))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1869
value = 5140;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1870

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1872
type = ChangeAnim
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1874
trigger1 = ((Anim = [5111, 5119]) || (Anim = [5171, 5179]));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1875
trigger1 = (SelfAnimExist((5140 + (Anim / 10))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1876
value = (5140 + (Anim / 10));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1877

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1879
type = ChangeAnim
trigger1 = (MatchOver = 1);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1883
trigger1 = (Anim = [5140, 5149]);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1884
trigger1 = (SelfAnimExist((Anim + 10)));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1885
persistent = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1881
value = (Anim + 10);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1886

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1888
type = ChangeAnim
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1890
trigger1 = (Anim != [5140, 5159]);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1891
trigger1 = (Anim != [5110, 5119]);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1892
value = 5110;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1893

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1895
type = VelMul
trigger1 = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1897
x = 0.85;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1898

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1900
type = VelSet
trigger1 = ((abs(Vel x)) < (Const(movement.down.friction.threshold)));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1902
persistent = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1903
x = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1904

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1906
type = NotHitBy
trigger1 = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1908
value = SCA;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1909
time = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1910


;!mtl-debug STATEDEF AIR_HIT_RECOVER_GROUND 5200
[Statedef 5200];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1914
type = A
movetype = H
physics = N

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1920
type = ChangeAnim
trigger1 = (Anim = 5035);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1922
trigger1 = (AnimTime = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1923
value = 5050;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1924

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1926
type = VelAdd
trigger1 = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1928
y = (GetHitVar(yaccel));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1929

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1931
type = SelfState
trigger1 = (Vel Y > 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1933
trigger1 = (Pos Y >= (Const(movement.air.gethit.groundrecover.groundlevel)));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1934
value = 5201;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1935


;!mtl-debug STATEDEF AIR_FALL_RECOVER_GROUND 5201
[Statedef 5201];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1939
type = A
movetype = H
physics = A
anim = 5200

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1946
type = Turn
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1948
trigger1 = (p2dist X < (Const720p((-20))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1949

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1951
type = VelSet
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1953
x = (Const(velocity.air.gethit.groundrecover.x));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1954
y = (Const(velocity.air.gethit.groundrecover.y));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1955

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1957
type = PosSet
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1959
y = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1960

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1962
type = NotHitBy
trigger1 = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1964
value = SCA;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1965
time = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1966

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1968
type = PalFX
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1970
time = 3;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1971
add = 128, 128, 128;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1972

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1974
type = Explod
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1976
anim = F60;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1977
postype = none;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1978
pos = (pos x + camerapos x), (pos y - (floor(vel y)));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1979
facing = Facing;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1980
sprpriority = (-10);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1981


;!mtl-debug STATEDEF AIR_FALL_RECOVER_AIR 5210
[Statedef 5210];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1985
type = A
movetype = I
physics = N
anim = 5210
ctrl = 0

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1993
type = PalFX
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1995
time = 3;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1996
add = 128, 128, 128;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1997

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:1999
type = PosFreeze
trigger1 = (Time < 4);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2001

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2003
type = Turn
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2005
trigger1 = (p2dist X < (Const720p((-80))));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2006

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2008
type = VelMul
trigger1 = (Time = 4);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2010
x = (Const(velocity.air.gethit.airrecover.mul.x));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2011
y = (Const(velocity.air.gethit.airrecover.mul.y));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2012

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2014
type = VelAdd
trigger1 = (Time = 4);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2016
x = (Const(velocity.air.gethit.airrecover.add.x));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2017
y = (Const(velocity.air.gethit.airrecover.add.y));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2018

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2020
type = Null
trigger1 = (Time = 4);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2022
x = .8;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2023
y = .8;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2024

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2026
type = Null
trigger1 = (Time = 4);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2028
x = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2029
y = (-4.5);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2030

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2032
type = Null
trigger1 = (Time = 4);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2034
trigger1 = (Vel Y > 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2035
y = .5;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2036

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2038
type = Null
trigger1 = (Time = 4);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2040
trigger1 = (Vel Y > (-3));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2041
y = (-2);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2042

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2044
type = Null
trigger1 = (Time = 4);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2046
trigger1 = (Vel Y > (-2));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2047
y = (-1);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2048

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2050
type = VelAdd
trigger1 = (Time = 4);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2052
trigger1 = (Command = "holdup");!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2053
y = (Const(velocity.air.gethit.airrecover.up));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2054

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2056
type = VelAdd
trigger1 = (Time = 4);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2058
trigger1 = (Command = "holddown");!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2059
y = (Const(velocity.air.gethit.airrecover.down));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2060

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2062
type = VelAdd
trigger1 = (Time = 4);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2064
trigger1 = (Command = "holdfwd");!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2065
x = (Const(velocity.air.gethit.airrecover.fwd));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2066

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2068
type = VelAdd
trigger1 = (Time = 4);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2070
trigger1 = (Command = "holdback");!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2071
x = (Const(velocity.air.gethit.airrecover.back));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2072

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2074
type = NotHitBy
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2076
value = SCA;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2077
time = 15;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2078

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2080
type = CtrlSet
trigger1 = (Time = 20);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2082
value = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2083

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2085
type = VelAdd
trigger1 = (Time >= 4);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2087
y = (Const(movement.air.gethit.airrecover.yaccel));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2088

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2090
type = ChangeState
trigger1 = (Vel Y > 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2092
trigger1 = (Pos Y >= 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2093
value = 52;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2094
ctrl = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2095


;!mtl-debug STATEDEF CONTINUE 5500
[Statedef 5500];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2099
type = S
anim = 5300
ctrl = 0
velset = 0, 0

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2106
type = ChangeAnim
trigger1 = (Time = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2108
trigger1 = (SelfAnimExist(5500));!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2109
value = 5500;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2110


;!mtl-debug STATEDEF INITIALIZE 5900
[Statedef 5900];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2114
type = S

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2118
type = VarRangeSet
trigger1 = (RoundsExisted = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2120
value = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2121

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2123
type = VarRangeSet
trigger1 = (RoundsExisted = 0);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2125
fvalue = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2126

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2128
type = RemapPal
trigger1 = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2130
source = 1, 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2131
dest = 1, PalNo;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2132

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2134
type = ChangeState
trigger1 = (RoundNo = 1);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2136
value = 190;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2137

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2139
type = ChangeState
trigger1 = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2141
value = 0;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/stdlib/common1.mtl:2142


;!mtl-debug STATEDEF INTRO 190
[Statedef 190];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/sample/UnitTest/UnitTest.states0.mtl:1

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/sample/UnitTest/UnitTest.states0.mtl:4
type = Null
trigger1 = ((var(0) := ((((1) & 1) * 1) + (var(0) & -2))) & 1);!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/sample/UnitTest/UnitTest.states0.mtl:6


;!mtl-debug STATEDEF COMMAND -1
[Statedef -1];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/sample/UnitTest/UnitTest.commands.mtl:1

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/sample/UnitTest/UnitTest.commands.mtl:4
type = Null
trigger1 = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/sample/UnitTest/UnitTest.commands.mtl:6


;!mtl-debug STATEDEF CUSTOM 1
[Statedef 1];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/sample/UnitTest/UnitTest.states1.mtl:1

[State ];!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/sample/UnitTest/UnitTest.states1.mtl:3
type = Null
trigger1 = 1;!mtl-debug LOCATION /home/jsmith/MDK/mtlcc/sample/UnitTest/UnitTest.states1.mtl:5


