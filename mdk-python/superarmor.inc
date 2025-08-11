[Define Template]
name = CreateArmor
local = damageTaken = float

[Define Parameters]
helperID = int

[State ]
type = Helper
trigger1 = NumHelper(helperID) = 0
name = "SuperArmor Helper"
id = helperID
pos = 0, 0
postype = PosType.P1
ownpal = true
supermovetime = 2147483647
pausemovetime = 2147483647

[State ]
type = LifeAdd
trigger1 = NumHelper(helperID) != 0 && damageTaken > 0
value = -(damageTaken)
ignorehitpause = true

[State ]
type = VarSet
trigger1 = true
damageTaken = 0

[State ]
type = NotHitBy
trigger1 = NumHelper(helperID) != 0
value = HitType.SCA

[State ]
type = NotHitBy
trigger1 = NumHelper(helperID) != 0
value2 = HitType.SCA


