## please remember to remove this before making public!
import sys
sys.path.append("c:\\Users\\ziddi\\MDK\\mdk-python")

## This is a straight conversion of a CNS superarmor shared in https://mugenarchive.com/forums/showthread.php?126780-Help-with-super-armor-coding
from mdk.compiler import library, template, statedef, build
from mdk.types import IntExpression, IntType, IntVar
from mdk.stdlib import *

@template(inputs = [IntType], library = "superarmor.inc")
def CreateArmor(helperID: Expression):
    ## since helperID is Optional, need to give a default value.
    if helperID == None:
        helperID = IntExpression(12345)

    if NumHelper(helperID) == 0:
        #Helper(ownpal = True, postype = )
        pass

if __name__ == "__main__":
    library([CreateArmor])