[Define Template]
name = CreateArmor
mtl.location.file = C:\Users\ziddi\MDK\mdk-python\examples\superarmor\superarmor.py
mtl.location.line = 15

[Define Parameters]
damageVariable = int
helperID = int

[State ]
type = Helper
trigger1 = NumHelper(helperID) = 0
name = "SuperArmor Helper"
id = helperID
pos = 0, 0
postype = PosType.P1
stateno = helperID
ownpal = true
supermovetime = 2147483647
pausemovetime = 2147483647
mtl.location.file = C:\Users\ziddi\MDK\mdk-python\examples\superarmor\superarmor.py
mtl.location.line = 17

[State ]
type = LifeAdd
trigger1 = NumHelper(helperID) != 0 && damageVariable > 0
value = -(damageVariable)
ignorehitpause = true
mtl.location.file = C:\Users\ziddi\MDK\mdk-python\examples\superarmor\superarmor.py
mtl.location.line = 24

[State ]
type = VarSet
trigger1 = true
damageVariable = 0
mtl.location.file = C:\Users\ziddi\MDK\mdk-python\examples\superarmor\superarmor.py
mtl.location.line = 26

[State ]
type = NotHitBy
trigger1 = NumHelper(helperID) != 0
value = HitType.SCA
mtl.location.file = C:\Users\ziddi\MDK\mdk-python\examples\superarmor\superarmor.py
mtl.location.line = 29

[State ]
type = NotHitBy
trigger1 = NumHelper(helperID) != 0
value2 = HitType.SCA
mtl.location.file = C:\Users\ziddi\MDK\mdk-python\examples\superarmor\superarmor.py
mtl.location.line = 30


[Define Template]
name = ArmorHelper
mtl.location.file = C:\Users\ziddi\MDK\mdk-python\examples\superarmor\superarmor.py
mtl.location.line = 33

[Define Parameters]
helperID = int

[State ]
type = StateTypeSet
trigger1 = true
statetype = root,StateType
mtl.location.file = C:\Users\ziddi\MDK\mdk-python\examples\superarmor\superarmor.py
mtl.location.line = 34

[State ]
type = ChangeAnim
trigger1 = Anim != root,Anim
value = root,Anim
mtl.location.file = C:\Users\ziddi\MDK\mdk-python\examples\superarmor\superarmor.py
mtl.location.line = 37

[State ]
type = AssertSpecial
trigger1 = true
flag = AssertType.Invisible
flag2 = AssertType.NoShadow
mtl.location.file = C:\Users\ziddi\MDK\mdk-python\examples\superarmor\superarmor.py
mtl.location.line = 39

[State ]
type = HitOverride
trigger1 = true
attr = HitType.SCA, HitAttr.AA, HitAttr.AP, HitAttr.AT
stateno = helperID
time = 1
forceair = false
ignorehitpause = true
mtl.location.file = C:\Users\ziddi\MDK\mdk-python\examples\superarmor\superarmor.py
mtl.location.line = 40

[State ]
type = BindToRoot
trigger1 = true
time = 1
facing = 1
pos = 0, 0
mtl.location.file = C:\Users\ziddi\MDK\mdk-python\examples\superarmor\superarmor.py
mtl.location.line = 41

[State ]
type = HitFallSet
trigger1 = true
value = false
mtl.location.file = C:\Users\ziddi\MDK\mdk-python\examples\superarmor\superarmor.py
mtl.location.line = 42

[State ]
type = DestroySelf
trigger1 = Life <= 0
mtl.location.file = C:\Users\ziddi\MDK\mdk-python\examples\superarmor\superarmor.py
mtl.location.line = 44


