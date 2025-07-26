from typing import Optional, TypeVar, Callable

from mtl.types.context import TranslationContext
from mtl.types.trigger import TriggerTree, TriggerTreeNode
from mtl.types.shared import TranslationError
from mtl.types.translation import *
from mtl.builtins import BUILTIN_INT, BUILTIN_FLOAT, BUILTIN_BOOL, BUILTIN_STRING, BUILTIN_CINT, BUILTIN_TYPE

from mtl.utils.compiler import find_type, find_trigger, find, equals_insensitive, get_widest_match, _tryparse

def parse_builtin(input: str) -> Optional[TypeDefinition]:
    ## parses the input string to see if it matches any built-in type.
    if _tryparse(input, int) != None:
        return BUILTIN_INT
    elif _tryparse(input, float) != None:
        return BUILTIN_FLOAT
    elif input.lower() in ["true", "false"]:
        return BUILTIN_BOOL
    elif input.startswith('"') and input.endswith('"'):
        return BUILTIN_STRING
    elif len(input) > 1 and input[0] in ["F", "S"] and _tryparse(input[1:], int) != None:
        return BUILTIN_CINT
    return None

def get_struct_target(input: str, table: list[TypeParameter], ctx: TranslationContext) -> Optional[TypeDefinition]:
    ## first find the target at the top level
    components = input.split(" ")
    struct_name = components[0].strip()
    ## find the type of this struct, from either triggers or locals
    struct_type: Optional[TypeDefinition] = None
    if (match := find_trigger(struct_name, [], ctx)) != None:
        struct_type = match.type
    elif (var := find(table, lambda k: equals_insensitive(k.name, struct_name))) != None:
        struct_type = var.type
    if struct_type == None: return None
    if struct_type.category != TypeCategory.STRUCTURE: return None
    ## now determine the type of the field being accessed
    if (target := find(struct_type.members, lambda k: equals_insensitive(k.split(":")[0], components[1]))) == None:
        return None
    if (target_type := find_type(target.split(":")[1], ctx)) == None:
        return None
    ## if the target type is also a struct, and we have a secondary access, create a 'virtual local' for the target and recurse.
    if target_type.category == TypeCategory.STRUCTURE and len(components) > 2:
        new_struct_string = "_target " + " ".join(components[2:])
        return get_struct_target(new_struct_string, [TypeParameter("_target", target_type)], ctx)
    ## return the identified target type
    return target_type

def type_check(tree: TriggerTree, table: list[TypeParameter], ctx: TranslationContext) -> Optional[list[TypeSpecifier]]:
    ## runs a type check against a single tree. this assesses that the types of the components used in the tree
    ## are correct and any operators used in the tree are valid.
    ## this returns a list of Specifiers because the tree can potentially have multiple results (e.g. for multivalues)

    ## handle each type of node individually.
    if tree.node == TriggerTreeNode.ATOM:
        ## the simplest case is ATOM, which is likely either a variable name, a parameter-less trigger name, or a built-in type.
        if (parsed := parse_builtin(tree.operator)) != None:
            ## handle the case where the token is a built-in type
            return [TypeSpecifier(parsed)]
        elif (trigger := find_trigger(tree.operator, [], ctx)) != None:
            ## if a trigger name matches, and the trigger has an overload which takes no parameters, accept it.
            return [TypeSpecifier(trigger.type)]
        elif (var := find(table, lambda k: equals_insensitive(k.name, tree.operator))) != None:
            ## if a variable name from the provided variable table matches, accept it.
            return [TypeSpecifier(var.type)]
        elif (type := find_type(tree.operator, ctx)) != None:
            ## if a type name matches, the resulting type is just `type`
            return [TypeSpecifier(BUILTIN_TYPE)]
        else:
            ## in other cases the token was not recognized, so we return None.
            raise TranslationError(f"Could not determine the type of subexpression {tree.operator}", tree.location)
    elif tree.node == TriggerTreeNode.UNARY_OP or tree.node == TriggerTreeNode.BINARY_OP:
        ## unary and binary operators will have an `operator` trigger which describes the inputs and outputs.
        ## first determine the type of each input.
        inputs: list[TypeDefinition] = []
        for child in tree.children:
            # if any child fails type checking, bubble that up
            if (child_type := type_check(child, table, ctx)) == None:
                raise TranslationError(f"Could not determine the type of subexpression from operator {tree.operator}.", tree.location)
            # the result of `type_check` could be a multi-value type specifier list, but triggers cannot accept these types
            # as parameters. so simplify here.
            if len(child_type) != 1: return None
            inputs.append(child_type[0].type)
        ## now try to find a trigger which matches the child types.
        if (match := find_trigger(f"operator{tree.operator}", inputs, ctx)) != None:
            return [TypeSpecifier(match.type)]
        ## if no match exists, the trigger does not exist.
        raise TranslationError(f"No matching operator overload was found for operator {tree.operator} and child types {', '.join([i.name for i in inputs])}", tree.location)
    elif tree.node == TriggerTreeNode.MULTIVALUE:
        ## multivalue operators can have one or more results. need to run the type check on each child,
        ## and return the list of type specifiers.
        specs: list[TypeSpecifier] = []
        for child in tree.children:
            if (child_type := type_check(child, table, ctx)) == None:
                raise TranslationError(f"Could not determine the type of subexpression from multivalued operator.", tree.location)
            ## it is not possible to nest multi-values. unpack the child
            if len(child_type) != 1: return None
            specs.append(child_type[0])
        return specs
    elif tree.node == TriggerTreeNode.INTERVAL_OP:
        ## interval operators have 2 children, which should have matching or coercible types.
        ## determine the widened type match and return that as the type of the interval.
        specs: list[TypeSpecifier] = []
        for child in tree.children:
            if (child_type := type_check(child, table, ctx)) == None:
                raise TranslationError(f"Could not determine the type of subexpression from interval operator.", tree.location)
            ## it is not possible to nest multi-values. unpack the child
            if len(child_type) != 1: return None
            specs.append(child_type[0])
        ## confirm exactly 2 children
        if len(specs) != 2: return None
        ## get the widest matching type
        if (match := get_widest_match(specs[0].type, specs[1].type, ctx)) == None:
            raise TranslationError(f"Input types {specs[0].type} and {specs[1].type} to interval operator could not be resolved to a common type.", tree.location)
        return [TypeSpecifier(match)]
    elif tree.node == TriggerTreeNode.FUNCTION_CALL:
        ## function calls (trigger calls) have the trigger name and the parameters as children.
        ## determine the child types, then identify the trigger overload which matches it.
        inputs: list[TypeDefinition] = []
        for child in tree.children:
            # if any child fails type checking, bubble that up
            if (child_type := type_check(child, table, ctx)) == None:
                raise TranslationError(f"Could not determine the type of subexpression in trigger {tree.operator}.", tree.location)
            # the result of `type_check` could be a multi-value type specifier list, but triggers cannot accept these types
            # as parameters. so simplify here.
            if len(child_type) != 1: return None
            inputs.append(child_type[0].type)
        ## now try to find a trigger which matches the child types.
        if (match := find_trigger(tree.operator, inputs, ctx)) != None:
            return [TypeSpecifier(match.type)]
        ## if no match exists, the trigger does not exist.
        raise TranslationError(f"No matching trigger overload was found for trigger named {tree.operator} and child types {', '.join([i.name for i in inputs])}", tree.location)
    elif tree.node == TriggerTreeNode.STRUCT_ACCESS:
        ## struct access contains the access information in the operator.
        if (struct_type := get_struct_target(tree.operator, table, ctx)) == None:
            raise TranslationError(f"Could not determine the type of the struct member access given by {tree.operator}.", tree.location)
        return [TypeSpecifier(struct_type)]
    
    ## fallback which should never be reachable!
    return None
