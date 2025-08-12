from typing import Optional

## This is a straight conversion of a CNS superarmor shared in https://mugenarchive.com/forums/showthread.php?126780-Help-with-super-armor-coding
from mdk.compiler import library, template
from mdk.types import Expression, IntType, PosType, HitType, HitAttr, AssertType
from mdk.stdlib import *

from validator import Validate_CreateArmor, Validate_ArmorHelper

@template(inputs = [IntType, IntType], library = "superarmor.inc", validator = Validate_CreateArmor)
def CreateArmor(damageVariable: Expression, helperID: Optional[Expression] = None):
    if NumHelper(helperID) == 0:
        Helper(
            ownpal = True, postype = PosType.P1, pos = (0, 0), id = helperID,
            pausemovetime = (2 ** 31) - 1, supermovetime = (2 ** 31) - 1,
            name = "SuperArmor Helper", stateno = helperID
        )

    if NumHelper(helperID) != 0 and damageVariable > 0:
        LifeAdd(value = -damageVariable, ignorehitpause = True)
    
    VarSet(var = damageVariable, value = 0)

    if NumHelper(helperID) != 0:
        NotHitBy(value = (HitType.SCA, ))
        NotHitBy(value2 = (HitType.SCA, ))

@template(inputs = [IntType], library = "superarmor.inc", validator = Validate_ArmorHelper)
def ArmorHelper(helperID: Optional[Expression] = None):
    StateTypeSet(statetype = root.StateType)

    if Anim != root.Anim:
        ChangeAnim(value = root.Anim)
    
    AssertSpecial(flag = AssertType.Invisible, flag2 = AssertType.NoShadow)
    HitOverride(attr = (HitType.SCA, HitAttr.AA, HitAttr.AP, HitAttr.AT), stateno = helperID, time = 1, forceair = False, ignorehitpause = True)
    BindToRoot(time = 1, facing = 1, pos = (0, 0))
    HitFallSet(value = False)
    if Life <= 0:
        DestroySelf()

if __name__ == "__main__":
    library([CreateArmor, ArmorHelper])