from mtl.types.translation import *
from mtl.types.context import *
from mtl.types.debug import DebugCategory
from mtl.types.builtins import BUILTIN_ANY

from mtl.utils.debug import debuginfo
from mtl.utils.compiler import *

def write_type_table(ctx: TranslationContext) -> list[str]:
    output: list[str] = []
    for type in ctx.types:
        if type.category not in [TypeCategory.BUILTIN, TypeCategory.BUILTIN_DENY, TypeCategory.STRING_ENUM, TypeCategory.STRING_FLAG]:
            output += debuginfo(DebugCategory.TYPE_DEFINITION, type)
    output.append("")
    return output

def write_variable_table(ctx: TranslationContext, index: int) -> list[str]:
    output: list[str] = []
    output += debuginfo(DebugCategory.VARIABLE_TABLE, ctx.allocations[index])
    for global_variable in ctx.globals:
        if index == 0 and resolve_alias_typed(global_variable.type, ctx, global_variable.location) != BUILTIN_FLOAT:
            output += debuginfo(DebugCategory.VARIABLE_ALLOCATION, global_variable)
        elif index == 1 and resolve_alias_typed(global_variable.type, ctx, global_variable.location) == BUILTIN_FLOAT:
            output += debuginfo(DebugCategory.VARIABLE_ALLOCATION, global_variable)
    output.append("")
    return output

def make_prop(prop: Any) -> str:
    if isinstance(prop, tuple):
        return str(", ".join([str(s) for s in prop]))
    elif isinstance(prop, bool):
        return "1" if prop else "0"
    else:
        return str(prop)

def write_statedef_property(statedef: StateDefinition, prop: str, output: list[str]):
    if prop in statedef.parameters.__dict__ and statedef.parameters.__dict__[prop] != None:
        output.append(f"{prop} = {make_prop(statedef.parameters.__dict__[prop])}")

def write_statedef(statedef: StateDefinition, ctx: TranslationContext) -> list[str]:
    output: list[str] = []

    output.append(f"[Statedef {statedef.name}]{debuginfo(DebugCategory.LOCATION, statedef.location)[0]}")
    for local_variable in statedef.locals:
        output += debuginfo(DebugCategory.VARIABLE_ALLOCATION, local_variable)

    for prop in ["type", "movetype", "physics", "anim", "ctrl", "poweradd", "juggle", "facep2", "hitdefpersist", "movehitpersist", "hitcountpersist", "sprpriority", "velset"]:
        write_statedef_property(statedef, prop, output)

    output.append("")

    table = statedef.locals + ctx.globals
    for controller in statedef.states:
        output += write_state_controller(controller, table, ctx)

    output.append("")

    return output

def emit_enum(input: str, type: TypeDefinition) -> str:
    ## takes an enum constant or flag combination and converts it to an integer.
    if type.category == TypeCategory.ENUM:
        for index in range(len(type.members)):
            if equals_insensitive(input, type.members[index]):
                return str(index)
    elif type.category == TypeCategory.FLAG:
        result = 0
        for index in range(len(type.members)):
            if type.members[index].lower() in input.lower():
                result += 2 ** index
        return str(result)
    
    raise TranslationError(f"Could not emit an enumeration value for input {input} and type {type.name}.", compiler_internal())

## this function handles converting trees to Expressions.
## it also handles type-checking, the types in the Expressions are concrete.
def emit_trigger_recursive(tree: TriggerTree, table: list[TypeParameter], ctx: TranslationContext, expected: Optional[list[TypeSpecifier]] = None) -> Expression:
    if tree.node == TriggerTreeNode.MULTIVALUE:
        ## multivalue, this kind of sucks but it should only come up at top level.
        ## express as a combined expression with type BUILTIN_ANY
        children: list[Expression] = []
        for index in range(len(tree.children)):
            child = tree.children[index]
            
            ## pass an expected type down the tree.
            if expected == None or len(expected) == 0:
                next_expected = None
            elif index < len(expected):
                next_expected = [expected[index]]
            elif expected[-1].repeat:
                next_expected = [expected[-1]]
            else:
                next_expected = None

            children.append(emit_trigger_recursive(child, table, ctx, expected = next_expected))

        return Expression(BUILTIN_ANY, ", ".join([e.value for e in children]))
    elif tree.node == TriggerTreeNode.UNARY_OP or tree.node == TriggerTreeNode.BINARY_OP:
        ## resolve child types.
        children: list[Expression] = []
        for child in tree.children:
            children.append(emit_trigger_recursive(child, table, ctx))
        ## find an operator trigger for the types.
        if (match := find_trigger(f"operator{tree.operator}", [e.type for e in children], ctx, tree.location)) == None:
            raise TranslationError(f"Could not find a matching operator {tree.operator} for types {', '.join([e.type.name for e in children])}", tree.location)
        ## if the operator is assignment, and the LHS is a VariableExpression (it always should be...), then the expression needs to use its assignment mask.
        if tree.operator == ":=" and isinstance(children[0], VariableExpression):
            children[0].value = f"var({children[0].allocation[0]})"
            if children[0].is_float: children[0].value = f"f{children[0].value}"
            children[1].value = mask_write(children[0].allocation[0], children[1].value, children[0].allocation[1], children[0].type.size, children[0].type == BUILTIN_FLOAT)
        ## if the trigger has a const evaluator, use it. otherwise, trust the output type.
        if match.const != None:
            return match.const(children, ctx)
        elif tree.node == TriggerTreeNode.UNARY_OP:
            return Expression(match.type, f"({tree.operator}{children[0].value})")
        else:
            return Expression(match.type, f"({children[0].value} {tree.operator} {children[1].value})")
    elif tree.node == TriggerTreeNode.INTERVAL_OP:
        ## interval, construct an expression and return the widest match between the children.
        children: list[Expression] = []
        for child in tree.children:
            children.append(emit_trigger_recursive(child, table, ctx))
        if (widest := get_widest_match(children[0].type, children[1].type, ctx, tree.location)) == None:
            raise TranslationError(f"Could not match types between {children[0].type} and {children[1].type} in interval operator.", tree.location)
        return Expression(widest, f"{tree.operator[0]}{children[0].value}, {children[1].value}{tree.operator[1]}")
    elif tree.node == TriggerTreeNode.FUNCTION_CALL:
        ## function call, need to fuzzy-match the right trigger overload
        ## and then either call the const evaluator or emit the result.
        matches = fuzzy_trigger(tree.operator, table, tree.children, ctx, tree.location)
        if len(matches) != 1:
            raise TranslationError(f"Failed to identify a single trigger overload for trigger {tree.operator}.", tree.location)
        ## emit each child with the expected type from the matched overload
        match = matches[0]
        children: list[Expression] = []
        for index in range(len(tree.children)):
            child = tree.children[index]
            
            ## pass an expected type down the tree.
            if match.params == None or len(match.params) == 0:
                next_expected = None
            elif index < len(match.params):
                next_expected = [TypeSpecifier(match.params[index].type)]
            else:
                next_expected = None

            children.append(emit_trigger_recursive(child, table, ctx, expected = next_expected))
        
        ## if the matched trigger has a const evaluator, return it
        if match.const != None:
            return match.const(children, ctx)
        elif len(children) == 0:
            return Expression(match.type, f"{match.name}")
        else:
            return Expression(match.type, f"({match.name}({', '.join([e.value for e in children])}))")
    elif tree.node == TriggerTreeNode.ATOM:
        ## the simplest case is ATOM, which is likely either a variable name, a parameter-less trigger name, or a built-in type.
        if (parsed := parse_builtin(tree.operator)) != None:
            ## handle the case where the token is a built-in type
            return Expression(parsed.type, make_prop(parsed.value))
        elif find_trigger(tree.operator, [], ctx, tree.location) != None:
            ## if a trigger name matches, and the trigger has an overload which takes no parameters, accept it.
            return emit_trigger_recursive(TriggerTree(TriggerTreeNode.FUNCTION_CALL, tree.operator, [], tree.location), table, ctx, expected)
        elif (var := find(table, lambda k: equals_insensitive(k.name, tree.operator))) != None:
            ## if a variable name from the provided variable table matches, accept it and respond with VariableExpression
            ## the value of the VariableExpression is the access-masked expression.
            ## if the value is being used in a VarSet (walrus operator) it will get caught in BINARY_OPERATOR
            ## and the write-masked expression will be used instead.
            return VariableExpression(var.type, f"({mask_variable(var.allocations[0][0], var.allocations[0][1], var.type.size, var.type == BUILTIN_FLOAT)})", var.allocations[0], var.type == BUILTIN_FLOAT)
        elif find_type(tree.operator, ctx) != None:
            ## if a type name matches, the resulting type is just `type`
            return Expression(BUILTIN_TYPE, tree.operator)
        elif expected != None and len(expected) == 1 and expected[0].type.category in [TypeCategory.ENUM, TypeCategory.FLAG]:
            ## if an expected type was passed, and the type is ENUM or FLAG,
            ## attempt to match the value to enum constants.
            if (result := match_enum(tree.operator, expected[0].type)) == None:
                raise TranslationError(f"Could not determine the type of subexpression {tree.operator}", tree.location)
            ## get the int constant for this enum or flag.
            value = emit_enum(tree.operator, result[0].type)
            return Expression(result[0].type, value)
        elif expected != None and len(expected) == 1 and expected[0].type.category in [TypeCategory.STRING_ENUM, TypeCategory.STRING_FLAG]:
            ## if an expected type was passed, and the type is ENUM or FLAG,
            ## attempt to match the value to enum constants.
            if (result := match_enum(tree.operator, expected[0].type)) == None:
                raise TranslationError(f"Could not determine the type of subexpression {tree.operator}", tree.location)
            return Expression(result[0].type, tree.operator)
        else:
            ## in other cases the token was not recognized, so we return None.
            raise TranslationError(f"Could not determine the type of subexpression {tree.operator}", tree.location)
    elif tree.node == TriggerTreeNode.STRUCT_ACCESS:
        ## struct access contains the access information in the operator.
        ## this needs to evaluate down to either a static expression (e.g. `Vel y`) or a variable access for user-defined structs.
        if (struct_type := get_struct_type(tree.operator, table, ctx)) == None:
            raise TranslationError(f"Could not determine the type of the struct given by {tree.operator}.", tree.location)
        if struct_type.category == TypeCategory.BUILTIN_STRUCTURE:
            if (member_type := get_struct_target(tree.operator, table, ctx)) == None:
                raise TranslationError(f"Could not determine the type of the struct member given by {tree.operator}.", tree.location)
            return Expression(member_type, tree.operator)
        else:
            ## TODO: this needs to determine the VariableExpression represented by the struct access.
            raise TranslationError("I was too lazy to finish struct implementation!", tree.location)
    elif tree.node == TriggerTreeNode.REDIRECT:
        ## redirects consist of a LHS redirect target and a RHS redirect expression.
        ## the overall expression is just <target>,<expression>.
        target = emit_trigger_recursive(tree.children[0], table, ctx)
        if target.type != BUILTIN_TARGET:
            raise TranslationError(f"Target {target.value} of redirected expression could not be resolved to a target type.", tree.location)
        
        exprn = emit_trigger_recursive(tree.children[1], table, ctx)
        if target.value.startswith("(") and target.value.endswith(")"):
            target.value = target.value[1:-1]
        return Expression(exprn.type, f"({target.value},{exprn.value})")

    raise TranslationError(f"Failed to emit a single trigger value.", tree.location)

def emit_trigger(tree: TriggerTree, table: list[TypeParameter], ctx: TranslationContext, expected: Optional[list[TypeSpecifier]] = None) -> str:
    debug = debuginfo(DebugCategory.LOCATION, tree.location)[0]
    return f"{emit_trigger_recursive(tree, table, ctx, expected).value}{debug}"

def write_state_controller(controller: StateController, table: list[TypeParameter], ctx: TranslationContext) -> list[str]:
    output: list[str] = []

    output.append(f"[State ]{debuginfo(DebugCategory.LOCATION, controller.location)[0]}")

    ## identify template/builtin for this controller
    if (template := find_template(controller.name, ctx)) == None:
        raise TranslationError(f"Failed to find any template or builtin controller for name {controller.name}", controller.location)
    
    output.append(f"type = {template.name}")

    for group_index in controller.triggers:
        group_name = "triggerall" if group_index == 0 else f"trigger{group_index}"
        for trigger in controller.triggers[group_index].triggers:
            trigger_text = emit_trigger(trigger, table, ctx)
            output.append(f"{group_name} = {trigger_text}")
    
    for property in controller.properties:
        if (prop := find(template.params, lambda k: equals_insensitive(k.name, property.key))) == None:
            expected = []
        else:
            expected = prop.type
        prop_key = property.key
        property_text = emit_trigger(property.value, table, ctx, expected = expected)
        ## if this is VarSet or VarAdd, any properties (which are not ignorehitpause/persistent)
        ## are actually variable assignments.
        ## convert the LHS into the variable name, and the RHS into an assignment-masked expression.
        if includes_insensitive(controller.name, ["VarSet", "VarAdd"]) and not includes_insensitive(property.key, ["ignorehitpause", "persistent"]):
            if (allocation := find(table, lambda k: equals_insensitive(k.name, property.key))) == None:
                raise TranslationError(f"Failed to find any variable definition for name {property.key} on {controller.name} controller.", controller.location)
            text_split = property_text.split(";")
            prop_key = f"var({allocation.allocations[0][0]})"
            if allocation.type == BUILTIN_FLOAT: prop_key = f"f{prop_key}"
            property_text = mask_write(allocation.allocations[0][0], text_split[0], allocation.allocations[0][1], allocation.type.size, allocation.type == BUILTIN_FLOAT) + ";" + text_split[1]

        output.append(f"{prop_key} = {property_text}")
    
    output.append("")

    return output