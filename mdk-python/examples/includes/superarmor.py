## please remember to remove this before making public!
import sys
sys.path.append("c:\\Users\\ziddi\\MDK\\mdk-python")

from typing import Optional

## This is a straight conversion of a CNS superarmor shared in https://mugenarchive.com/forums/showthread.php?126780-Help-with-super-armor-coding
from mdk.compiler import library, template, statedef, build
from mdk.types import Expression, IntType, PosType, FloatVar, HitType
from mdk.stdlib import *

from mdk.types.context import CompilerContext

ARMOR_INITIALIZED = False

def Validate_CreateArmor(**kwargs) -> Optional[dict[str, Expression]]:
    ## validator can modify the inputs, allowing for optionals.
    if 'helperID' not in kwargs or kwargs['helperID'] == None:
        print("helperID was none at callsite of CreateArmor")
        kwargs['helperID'] = Expression("11777", IntType)

    ## allow for single-initialization patterns.
    global ARMOR_INITIALIZED
    assert not ARMOR_INITIALIZED, "CreateArmor already initialized."
    ARMOR_INITIALIZED = True

    ## check the current statedef is -2
    context = CompilerContext.instance()
    assert context.current_state != None, "CreateArmor called outside of state context."
    assert "id" in context.current_state.params, "CreateArmor must be called from within state -2 for proper upkeep."
    assert context.current_state.params['id'].exprn == "-2", "CreateArmor must be called from within state -2 for proper upkeep."
    
    return kwargs

@template(inputs = [IntType], library = "superarmor.inc", validator = Validate_CreateArmor)
def CreateArmor(helperID: Optional[Expression] = None):
    damageTaken = FloatVar()

    if NumHelper(helperID) == 0:
        Helper(
            ownpal = True, postype = PosType.P1, pos = (0, 0), id = helperID,
            pausemovetime = (2 ** 31) - 1, supermovetime = (2 ** 31) - 1,
            name = "SuperArmor Helper"
        )

    if NumHelper(helperID) != 0 and damageTaken > 0:
        LifeAdd(value = -damageTaken, ignorehitpause = True)
    
    damageTaken.set(0)

    if NumHelper(helperID) != 0:
        NotHitBy(value = (HitType.SCA, ))
        NotHitBy(value2 = (HitType.SCA, ))

@statedef(stateno = -2)
def myCustomState():
    CreateArmor()

if __name__ == "__main__":
    #library([CreateArmor])
    build("superarmor.mtl")