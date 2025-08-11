from typing import Optional, Callable
from functools import partial
import inspect

from mdk.types.context import StateDefinition, TemplateDefinition, StateController, CompilerContext, StateScope, StateScopeType
from mdk.types.specifier import TypeSpecifier
from mdk.types.errors import TriggerException, CompilationException
from mdk.types.expressions import Expression
from mdk.types.builtins import IntType
from mdk.types.defined import StateType, MoveType, PhysicsType

from mdk.utils.shared import convert_tuple, format_bool, create_compiler_error
from mdk.utils.controllers import make_controller
from mdk.utils.compiler import write_controller, rewrite_function

from mdk.stdlib.controllers import ChangeState

def build(output: str, skip_templates: bool = False):
    context = CompilerContext.instance()
    try:
        ## builds the character from the input data.
        for state in context.statedefs:
            definition = context.statedefs[state]
            context.current_state = definition
            try:
                definition.fn() # this call registers the controllers in the statedef with the statedef itself.
            except Exception as exc:
                raise CompilationException(exc)
            context.current_state = None

        template_groups = set()
        if not skip_templates and len(context.templates) != 0:
            templates: list[Callable] = []
            for t in context.templates:
                templates.append(context.templates[t].fn)
                if context.templates[t].library == None:
                    context.templates[t].library = output + ".inc"
                template_groups.add(context.templates[t].library)
            library(templates)
        
        with open(output, mode="w") as f:
            if not skip_templates and len(context.templates) != 0:
                for group in template_groups:
                    f.write("[Include]\n")
                    f.write(f"source = {group}\n")
            f.write("\n")
            for name in context.statedefs:
                statedef = context.statedefs[name]
                f.write(f"[Statedef {name}]\n")
                for param in statedef.params:
                    f.write(f"{param} = {statedef.params[param]}\n")
                for local in statedef.locals:
                    f.write(f"local = {local.name} = {local.type.name}\n")
                f.write("\n")
                for controller in statedef.controllers:
                    write_controller(controller, f)
                    f.write("\n")
                f.write("\n")
    except TriggerException as exc:
        print(exc.get_message())
    except CompilationException as exc:
        create_compiler_error(exc)
    except Exception as exc:
        print("An internal error occurred while compiling a template, bug the developers.")
        raise exc

def library(templates: list[Callable], output: Optional[str] = None):
    if len(templates) == 0:
        raise Exception("Please specify some templates to be built.")
    context = CompilerContext.instance()
    try:
        per_file: dict[str, list[TemplateDefinition]] = {}
        for template in context.templates:
            definition = context.templates[template]
            context.current_template = definition
            kwargs = {}
            for param in definition.params:
                type = definition.params[param]
                kwargs[param] = Expression(param, type)
            try:
                definition.fn(**kwargs)
            except Exception as exc:
                raise CompilationException(exc)
            context.current_template = None
            if definition.library == None and output == None:
                raise CompilationException(f"Output library was not specified for template {definition.fn.__name__}, either specify a default output in call to library() or specify a library in the template() annotation.")
            if definition.library == None and output != None and definition.fn in templates:
                definition.library = output
            if definition.library not in per_file:
                per_file[definition.library] = [] # type: ignore
            per_file[definition.library].append(definition) # type: ignore

        for group in per_file:
            print(f"Creating output include file {group}.")
            with open(group, mode="w") as f:
                for definition in per_file[group]:
                    f.write("[Define Template]\n")
                    f.write(f"name = {definition.fn.__name__}\n")
                    for local in definition.locals:
                        f.write(f"local = {local.name} = {local.type.name}\n")
                    f.write("\n")
                    f.write("[Define Parameters]\n")
                    for param in definition.params:
                        f.write(f"{param} = {definition.params[param].name}\n")
                    f.write("\n")
                    for controller in definition.controllers:
                        write_controller(controller, f)
                        f.write("\n")
                    f.write("\n")
    except TriggerException as exc:
        print(exc.get_message())
    except CompilationException as exc:
        create_compiler_error(exc)
    except Exception as exc:
        print("An internal error occurred while compiling a template, bug the developers.")
        raise exc

def statedef(
    type: Expression = StateType.U,
    movetype: Expression = MoveType.U,
    physics: Expression = PhysicsType.U,
    anim: Optional[int] = None,
    velset: Optional[tuple[float, float]] = None,
    ctrl: Optional[bool] = None,
    poweradd: Optional[int] = None,
    juggle: Optional[int] = None,
    facep2: Optional[bool] = None,
    hitdefpersist: Optional[bool] = None,
    movehitpersist: Optional[bool] = None,
    hitcountpersist: Optional[bool] = None,
    sprpriority: Optional[int] = None,
    stateno: Optional[int] = None,
    scope: Optional[StateScope] = None
) -> Callable:
    def decorator(fn: Callable) -> Callable:
        return create_statedef(fn, type, movetype, physics, anim, velset, ctrl, poweradd, juggle, facep2, hitdefpersist, movehitpersist, hitcountpersist, sprpriority, stateno, scope)
    return decorator

## used by the @statedef decorator to create new statedefs,
## but can also be used by character developers to create statedefs ad-hoc (e.g. in a loop).
def create_statedef(
    fn: Callable,
    type: Expression = StateType.U,
    movetype: Expression = MoveType.U,
    physics: Expression = PhysicsType.U,
    anim: Optional[int] = None,
    velset: Optional[tuple[float, float]] = None,
    ctrl: Optional[bool] = None,
    poweradd: Optional[int] = None,
    juggle: Optional[int] = None,
    facep2: Optional[bool] = None,
    hitdefpersist: Optional[bool] = None,
    movehitpersist: Optional[bool] = None,
    hitcountpersist: Optional[bool] = None,
    sprpriority: Optional[int] = None,
    stateno: Optional[int] = None,
    scope: Optional[StateScope] = None
) -> Callable:
    print(f"Discovered a new StateDef named {fn.__name__}. Will process and load this StateDef.")
    
    new_fn = rewrite_function(fn)
    statedef = StateDefinition(new_fn, {}, [], [])

    # apply each parameter
    if stateno != None: statedef.params["id"] = Expression(str(stateno), IntType)
    statedef.params["type"] = type
    statedef.params["movetype"] = movetype
    statedef.params["physics"] = physics
    if anim != None: statedef.params["anim"] = Expression(str(anim), IntType)
    if velset != None: statedef.params["velset"] = convert_tuple(velset)
    if ctrl != None: statedef.params["ctrl"] = format_bool(ctrl)
    if poweradd != None: statedef.params["poweradd"] = Expression(str(poweradd), IntType)
    if juggle != None: statedef.params["juggle"] = Expression(str(juggle), IntType)
    if facep2 != None: statedef.params["facep2"] = format_bool(facep2)
    if hitdefpersist != None: statedef.params["hitdefpersist"] = format_bool(hitdefpersist)
    if movehitpersist != None: statedef.params["movehitpersist"] = format_bool(movehitpersist)
    if hitcountpersist != None: statedef.params["hitcountpersist"] = format_bool(hitcountpersist)
    if sprpriority != None: statedef.params["sprpriority"] = Expression(str(sprpriority), IntType)

    # add the new statedef to the context
    ctx = CompilerContext.instance()
    if fn.__name__ in ctx.statedefs:
        raise Exception(f"Attempted to overwrite statedef with name {fn.__name__}.")
    ctx.statedefs[fn.__name__] = statedef

    return partial(ChangeState, value = fn.__name__)

def do_template(name: str, *args, **kwargs) -> StateController:
    def generic_template(*args, **kwargs):
        if len(args) != 0:
            raise Exception("Templates cannot be called with positional arguments, only keyword arguments.")
        result = StateController()
        for arg in kwargs:
            result.params[arg] = kwargs[arg]
        return result
    ctrl = make_controller(generic_template, *args, **kwargs)
    ctrl.type = name
    return ctrl

def template(inputs: list[TypeSpecifier], library: Optional[str] = None) -> Callable:
    def decorator(fn: Callable):
        print(f"Discovered a new Template named {fn.__name__}. Will process and load this Template.")
        # get params of decorated function
        signature = inspect.signature(fn)

        # create new function with ast fixes
        new_fn = rewrite_function(fn)

        # ensure parameters align
        if len(signature.parameters) != len(inputs):
            raise Exception(f"Mismatch in template parameter count: saw {len(inputs)} input types, and {len(signature.parameters)} real parameters.")

        params: dict[str, TypeSpecifier] = {}
        index = 0
        for param in signature.parameters:
            params[param] = inputs[index]
            index += 1
        template = TemplateDefinition(new_fn, library, params, [], [])

        # add the new template to the context
        ctx = CompilerContext.instance()
        if fn.__name__ in ctx.templates:
            raise Exception(f"Attempted to overwrite template with name {fn.__name__}.")
        ctx.templates[fn.__name__] = template

        return partial(do_template, fn.__name__)
    return decorator
    
__all__ = ["build", "library", "statedef", "create_statedef", "template"]