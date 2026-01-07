from typing import Optional

from mtl.types.shared import Location, TranslationError
from mtl.types.context import TranslationContext
from mtl.types.ini import StateControllerSection
from mtl.types.trigger import TriggerTreeNode
from mtl.types.translation import *
from mtl.types.builtins import *
from mtl.parser.trigger import parseTrigger
from mtl.utils.func import *

import copy

def find_type(type_name: str, ctx: TranslationContext) -> Optional[TypeDefinition]:
    return find(ctx.types, lambda k: equals_insensitive(k.name, type_name))

def find_template(template_name: str, ctx: TranslationContext) -> Optional[TemplateDefinition]:
    return find(ctx.templates, lambda k: equals_insensitive(k.name, template_name))

def find_statedef(state_name: str, ctx: TranslationContext) -> Optional[StateDefinition]:
    return find(ctx.statedefs, lambda k: equals_insensitive(k.name, state_name) or str(k.parameters.id) == state_name)

def find_trigger(trigger_name: str, param_types: list[TypeDefinition], ctx: TranslationContext, loc: Location) -> Optional[TriggerDefinition]:
    #all_matches = get_all(ctx.triggers, lambda k: equals_insensitive(k.name, trigger_name))
    trigger_lower = trigger_name.lower()
    all_matches = [trig for trig in ctx.triggers if trig._lower == trigger_lower]
    ## there may be multiple candidate matches, we need to check if the types provided as input match the types of the candidate.
    for match in all_matches:
        ## the input type count should exactly match.
        ## we do not support optional arguments for triggers yet.
        if len(param_types) != len(match.params): continue
        matched = True
        for index in range(len(param_types)):
            if get_type_match(param_types[index], match.params[index].type, ctx, loc, no_warn = True) == None:
                matched = False
        ## if no types failed to match, we can return this type as the signature matches
        if matched: 
            return match
    ## if we reach here, no matching signature was found
    return None

def find_property(property: str, controller: StateController) -> list[StateControllerProperty]:
    return list(filter(lambda k: equals_insensitive(property, k.key), controller.properties))

## this checks EACH possible match and identifies which can potentially match the input trigger.
def fuzzy_trigger(trigger_name: str, table: list[TypeParameter], params: list[TriggerTree], ctx: TranslationContext, loc: Location, scope: Optional[StateDefinitionScope] = None, pass_through: Optional[bool] = True) -> list[TriggerDefinition]:
    results: list[TriggerDefinition] = []
    #all_matches = get_all(ctx.triggers, lambda k: equals_insensitive(k.name, trigger_name))
    trigger_lower = trigger_name.lower()
    all_matches = [trig for trig in ctx.triggers if trig._lower == trigger_lower]
    
    for match in all_matches:
        is_match = True
        ## the input type count should exactly match.
        ## we do not support optional arguments for triggers yet.
        if len(params) != len(match.params): continue

        ## type-check each param to see if it can match the current trigger.
        for index in range(len(params)):
            ## this is to help handle automatic enum matching.
            next_expected = [TypeSpecifier(match.params[index].type)]
            ## keep this in, this triggers an earlier error message for failed trigger match
            type_check(params[index], table + match.params, ctx, expected = next_expected, scope = scope, pass_through = pass_through)
            ## check if the child type even resolves - if not, there may be an unidentified global or an unmatched automatic enum.
            try:
                if (child_type := type_check(params[index], table + match.params, ctx, expected = next_expected, scope = scope, pass_through = pass_through)) == None:
                    is_match = False
                    break
            except TranslationError:
                is_match = False
                break
            ## the resulting type must not be empty or tuple
            if len(child_type) != 1:
                raise TranslationError("Triggers are not permitted to accept tuple types.", loc)
            ## match the result type to the expected type of the input
            if get_type_match(child_type[0].type, match.params[index].type, ctx, loc, no_warn=True) == None:
                is_match = False
                break
        ## if all params matched, add it to the result
        if is_match:
            results.append(match)
    return results

def resolve_alias(type: str, ctx: TranslationContext, loc: Location) -> str:
    ## recursively reduces an alias to its target type
    target_type = find_type(type, ctx)
    if target_type == None:
        ## we return the input here because it's possible `type` is a type-string (such as int,int,float)
        return type
    if target_type.category != TypeCategory.ALIAS:
        return target_type.name
    return resolve_alias(target_type.members[0], ctx, loc)

def resolve_alias_typed(type: TypeDefinition, ctx: TranslationContext, loc: Location) -> TypeDefinition:
    ## recursively reduces an alias to its target type
    if type.category != TypeCategory.ALIAS:
        return type
    if (target_type := find_type(type.members[0], ctx)) == None:
        raise TranslationError(f"Could not find target type {type.members[0]} for alias with name {type.name}.", loc)
    return resolve_alias_typed(target_type, ctx, loc)

def unpack_types(type: str, ctx: TranslationContext, loc: Location) -> list[TypeSpecifier]:
    ## unpacks types in the form `t1,t2,t3` (multi-value types)
    ## additionally handles optional and repetition syntax
    result: list[TypeSpecifier] = []

    type = resolve_alias(type, ctx, loc)

    for subtype in type.split(","):
        subtype = subtype.strip()

        required = not subtype.endswith("?")
        subtype = subtype.replace("?", "")
        repeated = subtype.endswith("...")
        subtype = subtype.replace("...", "")

        ## need to re-resolve aliases here!
        ## what happens if the re-resolved alias is another packed type string? everything breaks!
        subtype = resolve_alias(subtype, ctx, loc)

        if (subtype_definition := find_type(subtype, ctx)) == None:
            raise TranslationError(f"Could not find a type with name {subtype}", loc)
        
        result.append(TypeSpecifier(subtype_definition, required, repeated))

    return result

def get_widest_match(t1: TypeDefinition, t2: TypeDefinition, ctx: TranslationContext, loc: Location) -> Optional[TypeDefinition]:
    ## match t1 to t2, accepting any widening conversion which allows the types to match.
    wide1 = get_type_match(t1, t2, ctx, loc, no_warn = True)
    wide2 = get_type_match(t2, t1, ctx, loc, no_warn = True)

    if wide1 != None and wide2 != None:
        ## if both conversions work, return the widest
        return wide1 if wide1.size >= wide2.size else wide2
    elif wide1 != None and wide2 == None:
        ## return the only working conversion
        return wide1
    elif wide1 == None and wide2 != None:
        ## return the only working conversion
        return wide2
    else:
        ## neither conversion worked, types are not compatible
        return None

def get_type_match(t1_: TypeDefinition, t2_: TypeDefinition, ctx: TranslationContext, loc: Location, no_warn: bool = False) -> Optional[TypeDefinition]:
    t1 = resolve_alias_typed(t1_, ctx, loc)
    t2 = resolve_alias_typed(t2_, ctx, loc)

    ## match t1 to t2, following type conversion rules.
    ## if types match, t1 return the type.
    if t1 == t2: return t1

    ## special handling for the `any` type, which should always convert to the other type
    if t1.name == "any" and t2.name != "any":
        return t2
    if t2.name == "any" and t1.name != "any":
        return t1

    ## this is based on section 1.1 of the spec.

    ## `int` is implicitly convertible to `float`
    if t1.name == "int" and t2.name == "float":
        return t2
    ## implicit convert `state` to `int`
    if t1.name == "int" and t2.name == "state":
        return t2
    if t1.name == "state" and t2.name == "int":
        return t1

    ## `float` cannot be implicitly converted to `int` as it results in loss of precision.
    if t1.name == "float" and t2.name == "int":
        ## in a lot of builtin cases an alternative to convert `int` to `float` will be taken. so just warn and return None.
        ## if no alternative exists an error will be emitted anyway.
        if not no_warn: print(f"Warning at {os.path.realpath(loc.filename)}:{loc.line}: Conversion from float to int may result in loss of precision. If this is intended, use functions like ceil or floor to convert, or explicitly cast one side of the expression.")
        return None
    
    ## smaller builtin types can implicitly convert to wider ones (`bool`->`byte`->`short`->`int`)
    if not ctx.compiler_flags.no_implicit_conversion and t1.name in ["bool", "byte", "short"] and t2.name in ["bool", "byte", "short", "int"] and t1.size <= t2.size:
        return t2
    
    ## `char` is implicitly convertible to `byte`, but the reverse is not true.
    if not ctx.compiler_flags.no_implicit_conversion and t1.name == "char" and t2.name == "byte":
        return t2
    
    ## it's permitted to 'widen' a concrete type to a union type if the union type has a matching member
    if t2.category == TypeCategory.UNION:
        for member in t2.members:
            if (target_type := find_type(member, ctx)) != None and (widened := get_type_match(t1, target_type, ctx, loc, no_warn)) != None:
                return widened
            
    ## it's permitted to convert integer types directly to bool for CNS compatibility.
    ## here `state` counts as an integer type.
    if not ctx.compiler_flags.no_implicit_bool and t1.name in ["byte", "short", "int", "state"] and t2.name == "bool":
        return t2
    
    ## implicitly convert enum/flag types to int/bool for compatibility.
    if not ctx.compiler_flags.no_implicit_conversion and t1.category in [TypeCategory.ENUM, TypeCategory.FLAG] and t2.name == "int":
        return t2
    if not ctx.compiler_flags.no_implicit_conversion and t2.category in [TypeCategory.ENUM, TypeCategory.FLAG] and t1.name == "int":
        return t1
    
    if not ctx.compiler_flags.no_implicit_bool and t1.category in [TypeCategory.ENUM, TypeCategory.FLAG] and t2.name == "bool":
        return t2
    if not ctx.compiler_flags.no_implicit_bool and t2.category in [TypeCategory.ENUM, TypeCategory.FLAG] and t1.name == "bool":
        return t1

    ## could not convert.
    return None

def parse_local(decl: str, ctx: TranslationContext, loc: Location) -> Optional[TypeParameter]:
    if len(decl.split("=")) < 2: return None
    ## locals always have form `name = type`
    ## they can also specify a default value as `name = type(default)`
    local_name = decl.split("=")[0].strip()
    local_exprn = decl.split("=")[1].strip()

    ## convert the expression to a type
    if (local_type := find_type(local_exprn.split("(")[0].strip(), ctx)) == None:
        raise TranslationError(f"Could not parse local variable type specifier {local_exprn} to a type.", loc)

    ## attempt to parse the default value to a tree
    ## (default values are supposed to be const but that can be determined later)
    if "(" in local_exprn:
        default_value = parseTrigger(local_exprn.split("(")[1].split(")")[0].strip(), loc)
    else:
        default_value = None

    return TypeParameter(local_name, local_type, default_value)

def parse_controller(state: StateControllerSection, ctx: TranslationContext) -> StateController:
    ## parsing a state controller involves
    if (type := find(state.properties, lambda k: equals_insensitive(k.key, "type"))) == None:
        raise TranslationError("State controllers must declare a type property.", state.location)
    ## check the controller type as it was parsed as if it is a trigger
    if type.value.node == TriggerTreeNode.MULTIVALUE and len(type.value.children) == 1:
        name = type.value.children[0].operator
    elif type.value.node == TriggerTreeNode.ATOM:
        name = type.value.operator
    else:
        raise TranslationError(f"Could not determine which template to use for state controller {type.value.operator}.", state.location)
    
    ## find the template (or builtin controller) to use for this state controller.
    if (template := find_template(name, ctx)) == None:
        raise TranslationError(f"Could not determine which template to use for state controller {name}.", state.location)
    
    ## for each property on the controller, we want to classify them into `triggers` or `properties` and assign to the appropriate group.
    triggers: dict[int, TriggerGroup] = {}
    properties: list[StateControllerProperty] = []
    for prop in state.properties:
        if prop.key == "type": continue
        if prop.key.startswith("trigger"):
            ## handle trigger groups
            group = prop.key[7:].strip()
            ## determine a numeric group ID
            if group == "all": group_index = 0
            else: group_index = tryparse(group, int)
            ## ensure group ID is numeric
            if group_index == None: raise TranslationError(f"Could not determine the group ID for trigger group named {prop.key}", prop.location)
            ## find the matching group
            if group_index not in triggers: triggers[group_index] = TriggerGroup([])
            triggers[group_index].triggers.append(prop.value)
        else:
            ## store the property
            if find(properties, lambda k: equals_insensitive(prop.key, k.key) and includes_insensitive(prop.key, ["persist"])) != None:
                raise TranslationError(f"Property {prop.key} was redefined in state controller.", prop.location)
            properties.append(prop)

    return StateController(name, triggers, properties, state.location)

def replace_recursive(tree: TriggerTree, old: TriggerTree, new: TriggerTree):
    ## make sure to replace THIS tree if it exactly matches the old one.
    if tree == old:
        tree.node = new.node
        tree.children = copy.deepcopy(new.children)
        tree.operator = new.operator
        return
    ## this iterates its children.
    for subindex in range(len(tree.children)):
        if tree.children[subindex] == old:
            tree.children[subindex] = copy.deepcopy(new)
        else:
            replace_recursive(tree.children[subindex], old, new)

def replace_expression(controller: StateController, old: TriggerTree, new: TriggerTree):
    ## find instances of `old` in the controller and replace with `new`.
    for group_id in controller.triggers:
        for trigger in controller.triggers[group_id].triggers:
            replace_recursive(trigger, old, new)
    for property in controller.properties:
        replace_recursive(property.value, old, new)

def replace_triggers(tree: TriggerTree, table: list[TypeParameter], ctx: TranslationContext, scope: Optional[StateDefinitionScope] = None) -> bool:
    replaced = False

    if tree.node == TriggerTreeNode.ATOM:
        # simple case with no parameters, which means we can substitute directly.
        if (match := find_trigger(tree.operator, [], ctx, tree.location)) == None:
            return replaced ## this implies the atom is not a trigger call, might be a bare value. we don't care much here as triggers are checked elsewhere.
        if match.category != TriggerCategory.BUILTIN and match.exprn != None:
            ## we only make replacements against user-defined triggers and operators.
            ## builtin operators have `exprn` as None.
            tree.node = match.exprn.node
            tree.children = copy.deepcopy(match.exprn.children)
            tree.operator = match.exprn.operator
            replaced = True
    elif tree.node == TriggerTreeNode.REDIRECT:
        ## for redirects we need to identify the target scope of the redirect
        ## before analyzing the target of the redirect expression.
        if (target := type_check(tree.children[0], table, ctx, scope = scope)) == None or target[0].type != BUILTIN_TARGET:
            raise TranslationError(f"Target of redirected expression could not be resolved to a target type.", tree.location)
        if equals_insensitive(tree.children[0].operator, "rescope") and scope != None:
            ## rescope needs special handling in type-checking.
            ## the target scope is really `children[0].children[1]`.
            target_node = tree.children[0].children[1]
            target_scope = get_redirect_scope(target_node, scope)
            target_table = list(filter(lambda k: k.scope == target_scope, ctx.globals))
        elif scope != None:
            target_scope = get_redirect_scope(tree.children[0], scope)
            target_table = list(filter(lambda k: k.scope == target_scope, ctx.globals))
        else:
            target_scope = None
            target_table = []
        ## now we need to analyze the redirect target, WITHIN the new target scope.
        replaced = replace_triggers(tree.children[1], target_table, ctx, scope = target_scope) or replaced
        return replaced
    elif tree.node == TriggerTreeNode.FUNCTION_CALL:
        ## it is possible for the function name to be the name of a struct type, in which case
        ## this trigger is a struct initializer. (this syntax is only legal in the body of a VarSet or in an assignment operator).
        if (match := find_type(tree.operator, ctx)) != None and match.category in [TypeCategory.BUILTIN_STRUCTURE, TypeCategory.STRUCTURE]:
            ## we need to make replacements on each struct member.
            if len(tree.children) != len(match.members):
                raise TranslationError(f"Initializer for struct with type {tree.operator} requires {len(match.members)} parameters, not {len(tree.children)}.", tree.location)
            for child in tree.children:
                replaced = replace_triggers(child, table, ctx, scope = scope) or replaced
            ## return as the struct call has been replaced
            return replaced

        ## we need to identify all overloads which CAN match this call, because at this point the child types are not known
        ## (and it's not trivial to infer since CNS allows enums to be specified without any indication of their type...)
        matches = fuzzy_trigger(tree.operator, table, tree.children, ctx, tree.location, scope = scope)
        if len(matches) == 0:
            ## if no match exists, the trigger does not exist.
            raise TranslationError(f"No matching trigger overload was found for trigger named {tree.operator}.", tree.location)
        elif len(matches) > 1:
            ## too many potential matches, maybe accepts 2 overloads with overlapping enum types?
            raise TranslationError(f"Could not identify a unique trigger overload for trigger named {tree.operator}.", tree.location)
        else:
            match = matches[0]
            ## only perform replacements on non-builtin triggers. but, still need to inspect children.
            if match.category == TriggerCategory.BUILTIN or match.exprn == None:
                for child in tree.children:
                    replaced = replace_triggers(child, table, ctx, scope = scope) or replaced
                return replaced
            ## we need to do 2 things:
            ## - copy the trigger expression and update it with parameter replacements
            new_trigger = copy.deepcopy(match.exprn)
            for index in range(len(match.params)):
                old_exprn = TriggerTree(TriggerTreeNode.ATOM, match.params[index].name, [], tree.location)
                replace_recursive(new_trigger, old_exprn, tree.children[index])
            ## - insert it in place of this node.
            tree.node = new_trigger.node
            tree.children = new_trigger.children
            tree.operator = new_trigger.operator
            replaced = True

    for child in tree.children:
        replaced = replace_triggers(child, table, ctx, scope = scope) or replaced

    return replaced

def merge_by_operand(triggers: list[TriggerTree], op: str, loc: Location) -> TriggerTree:
    ## recursively merges the list of triggers into a binary operator structure.
    if len(triggers) == 1: return triggers[0]
    return TriggerTree(TriggerTreeNode.BINARY_OP, op, [triggers[0], merge_by_operand(triggers[1:], op, loc)], loc)

def merge_triggers(triggers: dict[int, TriggerGroup], location: Location) -> list[TriggerTree]:
    ## take a list of triggers and merge them so they can be applied as `triggerall`.
    ## this means a) translating any `triggerall` statements directly into the result;
    result: list[TriggerTree] = triggers[0].triggers if 0 in triggers else []
    ## b) combining other groups into AND/OR constructs.
    all_groups: list[TriggerTree] = []
    for group_index in triggers:
        if group_index == 0: continue
        group = triggers[group_index].triggers
        ## combine all the triggers in the group into an AND construct
        all_groups.append(merge_by_operand(group, "&&", location))
    ## now combine all groups into an OR construct.
    result.append(merge_by_operand(all_groups, "||", location))
    return result

def find_globals(tree: TriggerTree, locals: list[TypeParameter], scope: StateDefinitionScope, ctx: TranslationContext) -> list[TypeParameter]:
    ## recursively identifies assignment statements.
    if tree.node == TriggerTreeNode.BINARY_OP and tree.operator == ":=" and tree.children[0].node == TriggerTreeNode.ATOM:
        ## ensure to check globals on RHS expression first!!
        result: list[TypeParameter] = []
        result += find_globals(tree.children[1], locals, scope, ctx)

        ## only include if the LHS does not match a known local
        if find(locals, lambda k: equals_insensitive(k.name, tree.children[0].operator)) == None:
            target_type = type_check(tree.children[1], locals, ctx, scope = scope)
            if target_type == None or len(target_type) == 0:
                raise TranslationError(f"Could not identify target type of global {tree.children[0].operator} from its assignment.", tree.location)
            if len(target_type) != 1:
                raise TranslationError(f"Target type of global {tree.children[0].operator} was a tuple, but globals cannot contain tuples.", tree.location)
            result.append(TypeParameter(tree.children[0].operator, target_type[0].type, location = tree.location, scope = scope))
        return result
    elif tree.node == TriggerTreeNode.BINARY_OP and tree.operator == ":=" and tree.children[0].node == TriggerTreeNode.FUNCTION_CALL:
        if tree.children[0].operator.lower() in ["var", "fvar", "sysvar", "sysfvar"]:
            raise TranslationError(f"State controller sets indexed variable which is not currently supported by MTL.", tree.location)
        raise TranslationError(f"Attempted to assign a value to a trigger expression {tree.children[0].operator}.", tree.location)
    else:
        result: list[TypeParameter] = []
        for child in tree.children:
            result += find_globals(child, locals, scope, ctx)
        return result

def get_struct_type(input: TriggerTree, table: list[TypeParameter], ctx: TranslationContext) -> Optional[TypeDefinition]:
    ## find the type of this struct, from either triggers or locals

    ## determine the type of the field being accessed
    if input.children[0].node == TriggerTreeNode.ATOM:
        struct_name = input.children[0]
        struct_type: Optional[TypeDefinition] = None
        if (match := find_trigger(struct_name.operator, [], ctx, compiler_internal(ctx.compiler_flags))) != None:
            struct_type = match.type
        elif (var := find(table, lambda k: equals_insensitive(k.name, struct_name.operator))) != None:
            struct_type = var.type
        return struct_type
    elif input.children[0].node == TriggerTreeNode.STRUCT_ACCESS:
        return get_struct_type(input.children[0], table, ctx)
    else:
        raise TranslationError(f"Can't determine target of struct access for target with node {input.children[0].node}.", input.location)

def get_struct_target(input: TriggerTree, table: list[TypeParameter], ctx: TranslationContext) -> Optional[TypeDefinition]:
    ## determine the type of the field being accessed
    if input.children[0].node == TriggerTreeNode.ATOM:
        ## if first field is an ATOM, it contains a struct variable.
        if (struct_type := get_struct_type(input, table, ctx)) == None:
            return None
        if struct_type.category not in [TypeCategory.STRUCTURE, TypeCategory.BUILTIN_STRUCTURE]: return None
        target_name = input.children[1].operator
    elif input.children[0].node == TriggerTreeNode.STRUCT_ACCESS:
        ## otherwise, it contains a sub-access, recurse to get the inner target.
        if (struct_type := get_struct_target(input.children[0], table, ctx)) == None:
            return None
        target_name = input.children[1].operator
    else:
        raise TranslationError(f"Can't determine target of struct access for target with node {input.children[0].node}.", input.location)
    if (target := find(struct_type.members, lambda k: equals_insensitive(k.split(":")[0], target_name))) == None:
        return None
    if (target_type := find_type(target.split(":")[1], ctx)) == None:
        return None
    ## if the target type is also a struct, and we have a secondary access, create a 'virtual local' for the target and recurse.
    if target_type.category in [TypeCategory.STRUCTURE, TypeCategory.BUILTIN_STRUCTURE] and input.children[1].node == TriggerTreeNode.STRUCT_ACCESS:
        return get_struct_target(input.children[1], [TypeParameter(input.children[1].children[0].operator, target_type)], ctx)
    ## return the identified target type
    return target_type

def match_enum(input: str, enum: TypeDefinition) -> Optional[list[TypeSpecifier]]:
    if not enum.category in [TypeCategory.ENUM, TypeCategory.FLAG, TypeCategory.STRING_ENUM, TypeCategory.STRING_FLAG]:
        return None
    
    if enum.category in [TypeCategory.ENUM, TypeCategory.STRING_ENUM] and includes_insensitive(input, enum.members):
        ## for enum, input must exactly match a constant
        return [TypeSpecifier(enum)]
    elif enum.category == TypeCategory.STRING_FLAG:
        ## for STRING_FLAG, each member is one character. each character of input must exactly match a constant.
        for c in input:
            if not includes_insensitive(c, enum.members): return None
        return [TypeSpecifier(enum)]
    elif enum.category == TypeCategory.FLAG and includes_insensitive(input, enum.members):
        ## for FLAG, the input should be a SINGLE flag member. members are joined by bitwise or operators.
        return [TypeSpecifier(enum)]
    return None
    
def match_enum_parts(input: str, ctx: TranslationContext) -> Optional[list[TypeSpecifier]]:
    # enum names are permitted to contain `.` so we need to do extra work to match.
    # try to identify a matching typename for each segment of the name.
    split = input.split(".")
    for index in range(1, len(split)):
        maybe_typename = ".".join(split[:index])
        maybe_fieldname = ".".join(split[index:])
        if (enum := find_type(maybe_typename, ctx)) != None:
            if (matched := match_enum(maybe_fieldname, enum)) != None:
                return matched
    return None

def type_check(tree: TriggerTree, table: list[TypeParameter], ctx: TranslationContext, expected: Optional[list[TypeSpecifier]] = None, scope: Optional[StateDefinitionScope] = None, pass_through: Optional[bool] = False) -> Optional[list[TypeSpecifier]]:
    ## runs a type check against a single tree. this assesses that the types of the components used in the tree
    ## are correct and any operators used in the tree are valid.
    ## this returns a list of Specifiers because the tree can potentially have multiple results (e.g. for multivalues)

    ## handle each type of node individually.
    if tree.node == TriggerTreeNode.ATOM:
        ## the simplest case is ATOM, which is likely either a variable name, a parameter-less trigger name, or a built-in type.
        if (parsed := parse_builtin(tree.operator)) != None:
            ## handle the case where the token is a built-in type
            return [TypeSpecifier(parsed.type)]
        elif not ctx.compiler_flags.no_implicit_enum and expected != None and len(expected) == 1 \
             and expected[0].type.category in [TypeCategory.ENUM, TypeCategory.FLAG, TypeCategory.STRING_ENUM, TypeCategory.STRING_FLAG] \
             and (result_type := match_enum(tree.operator, expected[0].type)) != None:
            ## if an expected type was passed, and the type is ENUM or FLAG,
            ## attempt to match the value to enum constants.
            return result_type
        elif (trigger := find_trigger(tree.operator, [], ctx, tree.location)) != None:
            ## if a trigger name matches, and the trigger has an overload which takes no parameters, accept it.
            return [TypeSpecifier(trigger.type)]
        elif (var := find(table, lambda k: equals_insensitive(k.name, tree.operator))) != None:
            ## if a variable name from the provided variable table matches, accept it.
            return [TypeSpecifier(var.type)]
        elif (type := find_type(tree.operator, ctx)) != None:
            ## if a type name matches, the resulting type is just `type`
            return [TypeSpecifier(BUILTIN_TYPE)]
        elif "." in tree.operator:
            ## might be an explicit enum type, extract enum typename and match on it
            return match_enum_parts(tree.operator, ctx)
        elif find_statedef(tree.operator, ctx) != None:
            ## match against statedef names explicitly
            return [TypeSpecifier(BUILTIN_STATE)]
        elif tree.operator == "":
            return [TypeSpecifier(BUILTIN_ANY)]
        else:
            ## in other cases the token was not recognized, so we return None.
            raise TranslationError(f"Could not determine the type of subexpression {tree.operator}", tree.location)
    elif tree.node == TriggerTreeNode.UNARY_OP or tree.node == TriggerTreeNode.BINARY_OP:
        ## unary and binary operators will have an `operator` trigger which describes the inputs and outputs.
        ## first determine the type of each input.
        inputs: list[TypeDefinition] = []
        ## test the types of each input to see if either side is an enum or flag.
        ## then we can pass the type to the other child to allow for specifier-less enums.
        maybe_expected: Optional[list[TypeSpecifier]] = None
        for child in tree.children:
            try:
                if (child_type := type_check(child, table, ctx, scope = scope, pass_through = pass_through)) != None:
                    if len(child_type) == 1 and child_type[0].type.category in [TypeCategory.ENUM, TypeCategory.STRING_ENUM, TypeCategory.FLAG, TypeCategory.STRING_FLAG]:
                        maybe_expected = child_type
            except TranslationError:
                continue
        is_hitdefattr = tree.children[0].node == TriggerTreeNode.ATOM and tree.children[0].operator.lower() == "hitdefattr"
        is_hitdefattr = is_hitdefattr or (tree.children[0].node == TriggerTreeNode.REDIRECT and tree.children[0].children[1].operator.lower() == "hitdefattr")
        for child in tree.children:
            # if any child fails type checking, bubble that up
            if (child_type := type_check(child, table, ctx, scope = scope, expected = maybe_expected, pass_through = pass_through)) == None:
                raise TranslationError(f"Could not determine the type of subexpression from operator {tree.operator}.", tree.location)
            # the result of `type_check` could be a multi-value type specifier list, but triggers cannot accept these types
            # as parameters. so simplify here.
            if len(child_type) != 1:
                if is_hitdefattr: inputs.append(BUILTIN_ANY)
                else: return None
            else:
                inputs.append(child_type[0].type)
        ## now try to find a trigger which matches the child types.
        if (match := find_trigger(f"operator{tree.operator}", inputs, ctx, tree.location)) != None:
            return [TypeSpecifier(match.type)]
        ## if no match exists, the trigger does not exist.
        print(tree)
        raise TranslationError(f"No matching operator overload was found for operator {tree.operator} and child types {', '.join([i.name for i in inputs])}", tree.location)
    elif tree.node == TriggerTreeNode.MULTIVALUE:
        ## multivalue operators can have one or more results. need to run the type check on each child,
        ## and return the list of type specifiers.
        specs: list[TypeSpecifier] = []
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

            if (child_type := type_check(child, table, ctx, next_expected, scope = scope, pass_through = pass_through)) == None:
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
            if (child_type := type_check(child, table, ctx, expected = [TypeSpecifier(BUILTIN_FLOAT)], scope = scope, pass_through = pass_through)) == None:
                raise TranslationError(f"Could not determine the type of subexpression from interval operator.", tree.location)
            ## it is not possible to nest multi-values. unpack the child
            if len(child_type) != 1: return None
            specs.append(child_type[0])
        ## confirm exactly 2 children
        if len(specs) != 2: return None
        ## get the widest matching type
        if (match := get_widest_match(specs[0].type, specs[1].type, ctx, tree.location)) == None:
            raise TranslationError(f"Input types {specs[0].type} and {specs[1].type} to interval operator could not be resolved to a common type.", tree.location)
        return [TypeSpecifier(match)]
    elif tree.node == TriggerTreeNode.FUNCTION_CALL:
        ## function calls (trigger calls) have the trigger name and the parameters as children.
        ## determine the child types, then identify the trigger overload which matches it.

        ## it is possible for the function name to be the name of a struct type, in which case
        ## this trigger is a struct initializer. (this syntax is only legal in the body of a VarSet or in an assignment operator).
        if (match := find_type(tree.operator, ctx)) != None and match.category in [TypeCategory.BUILTIN_STRUCTURE, TypeCategory.STRUCTURE]:
            ## we need to type check the arguments to the struct initializer.
            if len(tree.children) != len(match.members):
                raise TranslationError(f"Initializer for struct with type {tree.operator} requires {len(match.members)} parameters, not {len(tree.children)}.", tree.location)
            for subindex in range(len(tree.children)):
                child = tree.children[subindex]
                type_name = match.members[subindex].split(':')[1]
                if (expected_subtype := find_type(type_name, ctx)) == None:
                    raise TranslationError(f"Initializer for struct with type {tree.operator} requires unknown type {type_name} as an input.", tree.location)
                child_type = type_check(child, table, ctx, expected = [TypeSpecifier(expected_subtype)], scope = scope, pass_through = pass_through)
                if child_type == None or len(child_type) == 0:
                    raise TranslationError(f"Initializer for struct with type {tree.operator} requires unknown type {type_name} as an input.", tree.location)
                if child_type[0].type != expected_subtype:
                    raise TranslationError(f"Initializer for struct with type {tree.operator} requires parameter with type {type_name}, not {child_type[0].type.name}.", tree.location)
            ## return the struct type
            return [TypeSpecifier(match)]

        ## we need to identify all overloads which CAN match this call, because at this point the child types are not known
        ## (and it's not trivial to infer since CNS allows enums to be specified without any indication of their type...)
        matches = fuzzy_trigger(tree.operator, table, tree.children, ctx, tree.location, scope = scope, pass_through = pass_through)
        if len(matches) == 0:
            ## if no match exists, the trigger does not exist.
            raise TranslationError(f"No matching trigger overload was found for trigger named {tree.operator}.", tree.location)
        elif len(matches) > 1:
            ## too many potential matches, maybe accepts 2 overloads with overlapping enum types?
            raise TranslationError(f"Could not identify a unique trigger overload for trigger named {tree.operator}.", tree.location)
        else:
            return [TypeSpecifier(matches[0].type)]
    elif tree.node == TriggerTreeNode.STRUCT_ACCESS:
        ## struct access contains the access information in the operator.
        if (struct_type := get_struct_target(tree, table, ctx)) == None:
            raise TranslationError(f"Could not determine the type of the struct member access given by {tree.children[0].operator}.", tree.location)
        return [TypeSpecifier(struct_type)]
    elif tree.node == TriggerTreeNode.REDIRECT:
        ## redirects will always have the redirect target as child 1, and the redirect expression as child 2.
        if (target := type_check(tree.children[0], table, ctx, scope = scope, pass_through = pass_through)) == None or target[0].type != BUILTIN_TARGET:
            raise TranslationError(f"Target of redirected expression could not be resolved to a target type.", tree.location)
        if equals_insensitive(tree.children[0].operator, "rescope") and scope != None:
            ## rescope needs special handling in type-checking.
            ## the target scope is really `children[0].children[1]`.
            target_node = tree.children[0].children[1]
            target_scope = get_redirect_scope(target_node, scope)
            target_table = list(filter(lambda k: k.scope == target_scope, ctx.globals))
        elif scope != None:
            target_scope = get_redirect_scope(tree.children[0], scope)
            target_table = list(filter(lambda k: k.scope == target_scope, ctx.globals))
        else:
            target_scope = None
            target_table = []
        ## if `pass_through` is set, the input table contains locals to a template or trigger definition.
        ## pass them through to the redirect type check.
        if pass_through:
            target_table += table
        if (exprn := type_check(tree.children[1], target_table, ctx, scope = target_scope, pass_through = pass_through)) == None:
            raise TranslationError(f"Could not determine the type of the redirected expression.", tree.location)
        return exprn
    
    ## fallback which should never be reachable!
    return None

def match_tuple(source: list[TypeSpecifier], target: TemplateParameter, ctx: TranslationContext, loc: Location):
    ## early-exit for obvious cases
    if len(source) > 0 and len(target.type) == 0:
        raise TranslationError(f"Failed to match type: target type {target.name} does not contain members, but input does.", loc)
    if len(source) == 0 and len(target.type) == 0: return
    ## iterate each value in `source`
    for index in range(len(source)):
        source_type = source[index]
        if index > len(target.type) and not target.type[-1].repeat:
            raise TranslationError(f"Failed to match type: input type has more members, but target type {target.name} has no repeated member.", loc)
        target_type = target.type[index] if index < len(target.type) else target.type[-1]
        if get_type_match(source_type.type, target_type.type, ctx, loc) == None:
            raise TranslationError(f"Failed to match type: could not match input type {source_type.type.name} to target type {target_type.type.name} for parameter {target.name}.", loc)
    ## confirm any remaining are not required
    if len(target.type) > len(source):
        for index in range(len(source), len(target.type)):
            if target.type[index].required:
                raise TranslationError(f"Failed to match tuple type: target member with type {target.type[index].type.name} is required but was not present.", loc)

## allocates space in the provided AllocationTable for a variable with the given size.
## returns the exact var and offset of the allocation.
## allocations are always byte-aligned.
def allocate(size: int, table: AllocationTable) -> Optional[tuple[int, int]]:
    ## search the table for the first index with available space.
    for index in range(table.max_size):
        current_used = table.data[index] if index in table.data else 0
        ## align to the next byte
        if (current_used % 8) != 0:
            current_used += 8 - (current_used % 8)
        current_available = 32 - current_used

        ## if the variable fits, allocate it
        if size <= current_available:
            table.data[index] = current_used + size
            ## return the allocation
            return (index, current_used)

    return None

def create_allocation(var: TypeParameter, ctx: TranslationContext):
    ## the real type of `global_variable` needs to be resolved.
    real_type = resolve_alias_typed(var.type, ctx, var.location)
    ## it's possible the real type is a bare builtin, or an enum/flag, or a structure.
    ## other types are forbidden and should throw an error.
    if real_type.category not in [TypeCategory.ENUM, TypeCategory.FLAG, TypeCategory.STRUCTURE, TypeCategory.BUILTIN_STRUCTURE, TypeCategory.BUILTIN]:
        raise TranslationError(f"Global variable named {var.name} has an invalid type {var.type.name} which was resolved to type category {real_type.category}.", var.location)
    if real_type == BUILTIN_FLOAT:
        ## handle BUILTIN_FLOAT directly since it's the only thing that allocates to float_allocation.
        if var.is_system:
            next = allocate(32, ctx.allocations[var.scope][3])
        else:
            next = allocate(real_type.size, ctx.allocations[var.scope][1])
        if next == None:
            raise TranslationError(f"Ran out of floating-point variable space to store variable {var.name}.", var.location)
        var.allocations.append(next)
    elif real_type.category == TypeCategory.BUILTIN:
        ## bare BUILTIN have size specified, so allocate directly.
        if var.is_system:
            next = allocate(32, ctx.allocations[var.scope][2])
        else:
            next = allocate(real_type.size, ctx.allocations[var.scope][0])
        if next == None:
            raise TranslationError(f"Ran out of integer variable space to store variable {var.name}.", var.location)
        var.allocations.append(next)
    elif real_type.category in [TypeCategory.ENUM, TypeCategory.FLAG]:
        ## these are just int in disguise.
        if var.is_system:
            next = allocate(32, ctx.allocations[var.scope][2])
        else:
            next = allocate(BUILTIN_INT.size, ctx.allocations[var.scope][0])
        if next == None:
            raise TranslationError(f"Ran out of integer variable space to store variable {var.name}.", var.location)
        var.allocations.append(next)
    elif real_type.category == TypeCategory.STRUCTURE or real_type.category == TypeCategory.BUILTIN_STRUCTURE:
        ## space needs to be allocated for EACH structure member.
        for member in real_type.members:
            if (member_type := find_type(member.split(":")[1], ctx)) == None:
                raise TranslationError(f"Could not determine the final type of member {member} on structure {var.type}.", var.location)
            ## allocate space for this structure member
            next_target = TypeParameter(member.split(":")[0], member_type, scope = var.scope)
            create_allocation(next_target, ctx)
            ## keep in mind this member could have ALSO been a structure.
            ## therefore assign ALL allocations on this structure to the parent.
            var.allocations += next_target.allocations

def create_table() -> tuple[AllocationTable, AllocationTable, AllocationTable, AllocationTable]:
    return (AllocationTable({}, 60), AllocationTable({}, 40), AllocationTable({}, 5), AllocationTable({}, 5))

def recursive_struct_assign(source_access: TriggerTree, member_name: str, struct_type: TypeDefinition, tree: TriggerTree, location: Location, ctx: TranslationContext) -> list[TriggerTree]:
    ## generates one or more trigger statements for assignment of a value to a struct variable.

    ## check if the member being accessed is a STRUCTURE type itself.
    member_type = None
    for member in struct_type.members:
        if member.split(":")[0] == member_name:
            if (member_type := find_type(member.split(":")[1], ctx)) == None:
                raise TranslationError(f"Failed to find type for struct member with name {member_name}.", location)
            if member_type != None: break
    
    if member_type == None:
        raise TranslationError(f"Failed to find type for struct member with name {member_name}.", location)
    
    ## base case: not a nested structure, return the normal assignment.
    if member_type.category != TypeCategory.STRUCTURE and member_type.category != TypeCategory.BUILTIN_STRUCTURE:
        return [
            TriggerTree(
                TriggerTreeNode.BINARY_OP,
                "||",
                [
                    TriggerTree(
                        TriggerTreeNode.FUNCTION_CALL,
                        "cast",
                        [
                            TriggerTree(
                                TriggerTreeNode.BINARY_OP,
                                ":=",
                                [
                                    TriggerTree(TriggerTreeNode.STRUCT_ACCESS, "", [
                                        source_access,
                                        TriggerTree(TriggerTreeNode.ATOM, member_name, [], location)
                                    ], location),
                                    tree
                                ],
                                location
                            ),
                            TriggerTree(TriggerTreeNode.ATOM, "bool", [], location)
                        ],
                        location
                    ),
                    TriggerTree(TriggerTreeNode.ATOM, "true", [], location)
                ],
                location
            )
        ]
    
    ## nested case: you need to return an assignment statement for EACH member in the nested struct.
    if len(member_type.members) != len(tree.children):
        raise TranslationError(f"Nested structure assignment for {member_name} must have {len(member_type.members)} parameters, not {len(tree.children)}.", location)

    results: list[TriggerTree] = []
    for subindex in range(len(member_type.members)):
        submember_name = member_type.members[subindex].split(":")[0]
        results += recursive_struct_assign(
            TriggerTree(TriggerTreeNode.STRUCT_ACCESS, "", [
                source_access,
                TriggerTree(TriggerTreeNode.ATOM, member_name, [], location)
            ], location),
            submember_name, member_type, tree.children[subindex], location, ctx
        )

    return results

def find_member_length(type: TypeDefinition, location: Location, ctx: TranslationContext) -> int:
    ## finds the total length of a struct member, accounting for nested structs.
    if type.category not in [TypeCategory.STRUCTURE, TypeCategory.BUILTIN_STRUCTURE]:
        return 1
    total = 0
    for member in type.members:
        member_typename = member.split(":")[1]
        if (member_type := find_type(member_typename, ctx)) == None:
            raise TranslationError(f"Could not determine type of struct member {member_typename}.", location)
        total += find_member_length(member_type, location, ctx)
    return total

def find_struct_allocation(table: list[TypeParameter], tree: TriggerTree, target: str, ctx: TranslationContext) -> Optional[tuple[int, TypeDefinition]]:
    ## given a struct access tree, finds the allocation offset to use for that access.
    if tree.children[0].node == TriggerTreeNode.STRUCT_ACCESS:
        ## for a nested access, recursively get the offset of the subaccess and add the offset to the parent access.
        result = find_struct_allocation(table, tree.children[0], tree.children[0].children[1].operator, ctx)
        if result == None:
            raise TranslationError(f"Could not determine offset for struct allocation.", tree.location)
        offset = result[0]
        source_type = result[1]
    elif tree.children[0].node == TriggerTreeNode.ATOM:
        ## for a simple access (where the access source is a var name) return the index of `target` in `members`
        if (var := find(table, lambda k: equals_insensitive(k.name, tree.children[0].operator))) == None:
            raise TranslationError(f"Could not determine type of struct access for {tree.children[0].operator}.", tree.location)
        source_type = var.type
        offset = 0
    else:
        raise TranslationError(f"Structs must have STRUCT_ACCESS or ATOM nodes, not {tree.children[0].node}.", tree.location)

    for index in range(len(source_type.members)):
        member_name = source_type.members[index].split(":")[0]
        member_typename = source_type.members[index].split(":")[1]
        if (member_type := find_type(member_typename, ctx)) == None:
            raise TranslationError(f"Could not determine type of struct member {member_name}.", tree.location)
        if member_name == target:
            return (offset, member_type)
        offset += find_member_length(member_type, tree.location, ctx)
    return None


        

