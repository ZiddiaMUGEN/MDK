from typing import Optional
from typing import Callable, TypeVar

from inspect import getframeinfo, stack
from inspect import currentframe

from mtl.types.shared import Location, TranslationError
from mtl.types.context import TranslationContext
from mtl.types.ini import StateControllerSection
from mtl.types.trigger import TriggerTreeNode
from mtl.types.translation import *
from mtl.parser.trigger import parseTrigger

T = TypeVar('T')
def _tryparse(input: str, fn: Callable[[str], T]) -> Optional[T]:
    try:
        return fn(input)
    except:
        return None

def line_number() -> int:
    cf = currentframe()
    if cf != None and cf.f_back != None:
        return cf.f_back.f_lineno
    else:
        return 0

def compiler_internal() -> Location:
    caller = getframeinfo(stack()[1][0])
    return Location(caller.filename, caller.lineno)

T = TypeVar('T')
def find(l: list[T], p: Callable[[T], bool]) -> Optional[T]:
    result = next(filter(p, l), None)
    return result

def get_all(l: list[T], p: Callable[[T], bool]) -> list[T]:
    result = list(filter(p, l))
    return result

def equals_insensitive(s1: str, s2: str) -> bool:
    return s1.lower() == s2.lower()

def find_type(type_name: str, ctx: TranslationContext) -> Optional[TypeDefinition]:
    return find(ctx.types, lambda k: equals_insensitive(k.name, type_name))

def find_template(template_name: str, ctx: TranslationContext) -> Optional[TemplateDefinition]:
    return find(ctx.templates, lambda k: equals_insensitive(k.name, template_name))

def find_trigger(trigger_name: str, param_types: list[TypeDefinition], ctx: TranslationContext) -> Optional[TriggerDefinition]:
    all_matches = get_all(ctx.triggers, lambda k: equals_insensitive(k.name, trigger_name))
    ## there may be multiple candidate matches, we need to check if the types provided as input match the types of the candidate.
    for match in all_matches:
        ## the input type count should exactly match.
        ## we do not support optional arguments for triggers yet.
        if len(param_types) != len(match.params): continue
        matched = True
        for index in range(len(param_types)):
            if get_type_match(param_types[index], match.params[index].type, ctx) == None:
                matched = False
        ## if no types failed to match, we can return this type as the signature matches
        if matched: 
            return match
    ## if we reach here, no matching signature was found
    return None

def resolve_alias(type: str, ctx: TranslationContext, loc: Location) -> str:
    ## recursively reduces an alias to its target type
    target_type = find_type(type, ctx)
    if target_type == None:
        ## we return the input here because it's possible `type` is a type-string (such as int,int,float)
        return type
    if target_type.category != TypeCategory.ALIAS:
        return target_type.name
    return resolve_alias(target_type.members[0], ctx, loc)

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

def get_widest_match(t1: TypeDefinition, t2: TypeDefinition, ctx: TranslationContext) -> Optional[TypeDefinition]:
    ## match t1 to t2, accepting any widening conversion which allows the types to match.
    wide1 = get_type_match(t1, t2, ctx)
    wide2 = get_type_match(t2, t1, ctx)

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

def get_type_match(t1: TypeDefinition, t2: TypeDefinition, ctx: TranslationContext) -> Optional[TypeDefinition]:
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

    ## `float` cannot be implicitly converted to `int` as it results in loss of precision.
    if t1.name == "float" and t2.name == "int":
        ## in a lot of builtin cases an alternative to convert `int` to `float` will be taken. so just warn and return None.
        ## if no alternative exists an error will be emitted anyway.
        print(f"Warning: Conversion from float to int may result in loss of precision. If this is intended, use functions like ceil or floor to convert, or explicitly cast one side of the expression.")
        return None
    
    ## smaller builtin types can implicitly convert to wider ones (`bool`->`byte`->`short`->`int`)
    if t1.name in ["bool", "byte", "short"] and t2.name in ["bool", "byte", "short", "int"] and t1.size <= t2.size:
        return t2
    
    ## `char` is implicitly convertible to `byte`, but the reverse is not true.
    if t1.name == "char" and t2.name == "byte":
        return t2
    
    ## it's permitted to 'widen' a concrete type to a union type if the union type has a matching member
    if t2.category == TypeCategory.UNION:
        for member in t2.members:
            if (target_type := find_type(member, ctx)) != None and (widened := get_type_match(t1, target_type, ctx)) != None:
                return widened

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
    properties: dict[str, TriggerTree] = {}
    for prop in state.properties:
        if prop.key == "type": continue
        if prop.key.startswith("trigger"):
            ## handle trigger groups
            group = prop.key[7:].strip()
            ## determine a numeric group ID
            if group == "all": group_index = -1
            else: group_index = _tryparse(group, int)
            ## ensure group ID is numeric
            if group_index == None: raise TranslationError(f"Could not determine the group ID for trigger group named {prop.key}", prop.location)
            ## find the matching group
            if group_index not in triggers: triggers[group_index] = TriggerGroup([])
            triggers[group_index].triggers.append(prop.value)
        else:
            ## store the property
            if prop.key in properties: raise TranslationError(f"Property {prop.key} was redefined in state controller.", prop.location)
            properties[prop.key] = prop.value

    return StateController(name, triggers, properties, state.location)