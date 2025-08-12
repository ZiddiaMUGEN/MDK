[Define Template]
name = CreateArmor
local = damageTaken = float
mtl.location.file = C:\Users\ziddi\MDK\mdk-python\examples\includes\superarmor.py
mtl.location.line = 36

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
mtl.location.file = C:\Users\ziddi\MDK\mdk-python\examples\includes\superarmor.py
mtl.location.line = 40

[State ]
type = LifeAdd
trigger1 = NumHelper(helperID) != 0 && damageTaken > 0
value = -(damageTaken)
ignorehitpause = true
mtl.location.file = C:\Users\ziddi\MDK\mdk-python\examples\includes\superarmor.py
mtl.location.line = 47

[State ]
type = VarSet
trigger1 = true
damageTaken = 0
mtl.location.file = C:\Users\ziddi\MDK\mdk-python\examples\includes\superarmor.py
mtl.location.line = 49

[State ]
type = NotHitBy
trigger1 = NumHelper(helperID) != 0
value = HitType.SCA
mtl.location.file = C:\Users\ziddi\MDK\mdk-python\examples\includes\superarmor.py
mtl.location.line = 52

[State ]
type = NotHitBy
trigger1 = NumHelper(helperID) != 0
value2 = HitType.SCA
mtl.location.file = C:\Users\ziddi\MDK\mdk-python\examples\includes\superarmor.py
mtl.location.line = 53


