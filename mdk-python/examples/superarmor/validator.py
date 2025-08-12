from typing import Optional

from mdk.types.context import CompilerContext
from mdk.types import Expression, IntType, VariableExpression

ARMOR_INITIALIZED = False

def Validate_CreateArmor(**kwargs) -> Optional[dict[str, Expression]]:
    context = CompilerContext.instance()

    ## validator can modify the inputs, allowing for optionals.
    if 'helperID' not in kwargs or kwargs['helperID'] == None:
        kwargs['helperID'] = Expression("11777", IntType)

    assert 'damageVariable' in kwargs, "CreateArmor must be provided with a global variable for damage tracking."
    assert isinstance(kwargs['damageVariable'], VariableExpression), "CreateArmor must be provided with a global variable for damage tracking."
    assert kwargs['damageVariable'].exprn in context.globals, "CreateArmor damage variable must be global, not local."

    ## allow for single-initialization patterns.
    global ARMOR_INITIALIZED
    assert not ARMOR_INITIALIZED, "CreateArmor already initialized."
    ARMOR_INITIALIZED = True

    ## check the current statedef is -2
    assert context.current_state != None, "CreateArmor called outside of state context."
    assert "id" in context.current_state.params, "CreateArmor must be called from within state -2 for proper upkeep."
    assert context.current_state.params['id'].exprn == "-2", "CreateArmor must be called from within state -2 for proper upkeep."
    
    return kwargs

def Validate_ArmorHelper(**kwargs) -> Optional[dict[str, Expression]]:
    ## validator can modify the inputs, allowing for optionals.
    if 'helperID' not in kwargs or kwargs['helperID'] == None:
        kwargs['helperID'] = Expression("11777", IntType)
    
    return kwargs