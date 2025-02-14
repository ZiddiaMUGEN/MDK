# contains a definition for each built-in state controller.
# this provides an interface to CNS controllers with properly-typed parameters.
from typing import Union, Optional, Tuple
from collections.abc import Callable

from mdk.utils import debug, format_bool, format_tuple
from mdk.triggers import Trigger
from mdk.types import Transparency
from mdk import state

TriggerInt = Union[Trigger, int]
TriggerFloat = Union[Trigger, float]
TriggerBool = Union[Trigger, bool]
TriggerVec2 = Tuple[TriggerFloat, TriggerFloat]
TriggerVec3 = Tuple[TriggerFloat, TriggerFloat, TriggerFloat]
TriggerRgb = Tuple[TriggerInt, TriggerInt, TriggerInt]
TriggerRgba = Tuple[TriggerInt, TriggerInt, TriggerInt, TriggerInt]

# decorator which provides a wrapper around each controller.
# this adds some extra debugging info, and also simplifies adding triggers to controllers and handling controller insertion into the active statedef.
def controller(fn: Callable) -> Callable:
    def wrapper(*args, ignorehitpause: Optional[bool] = None, persistent: Optional[int] = None, append: bool = True, **kwargs):
        debug(f"Executing controller {fn.__name__} with args: {args}, {kwargs}")
        ctrl: state.Controller = fn(*args, **kwargs)
        ctrl.type = fn.__name__
        if ignorehitpause != None: ctrl.params["ignorehitpause"] = format_bool(ignorehitpause)
        if persistent != None: ctrl.params["persistent"] = int(persistent)
        # hacky: this is a trick for the controllers to calle ach other without duplicating sctrls in the output.
        if append:
            for trigger in state.EXPRESSION_STACK:
                ctrl.add_trigger(1, trigger)
            state.CURRENT_STATEDEF.controllers.append(ctrl)
        return ctrl
    return wrapper

@controller
def AfterImage(
    time: Optional[TriggerInt] = None,
    length: Optional[TriggerInt] = None,
    palcolor: Optional[TriggerInt] = None,
    palinvertall: Optional[TriggerBool] = None,
    palbright: Optional[TriggerRgb] = None,
    palcontrast: Optional[TriggerRgb] = None,
    palpostbright: Optional[TriggerRgb] = None,
    paladd: Optional[TriggerRgb] = None,
    palmul: Optional[TriggerVec3] = None,
    timegap: Optional[TriggerInt] = None,
    framegap: Optional[TriggerInt] = None,
    trans: Optional[Transparency] = None
) -> state.Controller:
    result = state.Controller()

    if time != None: result.params["time"] = time
    if length != None: result.params["length"] = length
    if palcolor != None: result.params["palcolor"] = palcolor
    if palinvertall != None: result.params["palinvertall"] = format_bool(palinvertall)
    if palbright != None: result.params["palbright"] = format_tuple(palbright)
    if palcontrast != None: result.params["palcontrast"] = format_tuple(palcontrast)
    if palpostbright != None: result.params["palpostbright"] = format_tuple(palpostbright)
    if paladd != None: result.params["paladd"] = format_tuple(paladd)
    if palmul != None: result.params["palmul"] = format_tuple(palmul)
    if timegap != None: result.params["timegap"] = timegap
    if framegap != None: result.params["framegap"] = framegap
    if trans != None: result.params["trans"] = trans.name

    return result

@controller
def AfterImageTime(time: TriggerInt) -> state.Controller:
    result = state.Controller()

    result.params["time"] = time

    return result

@controller
def AllPalFX(
    time: Optional[TriggerInt] = None,
    add: Optional[TriggerRgb] = None,
    mul: Optional[TriggerRgb] = None,
    sinadd: Optional[TriggerRgba] = None,
    invertall: Optional[TriggerBool] = None,
    color: Optional[TriggerInt] = None,
) -> state.Controller:
    return PalFX(time, add, mul, sinadd, invertall, color, append = False)

@controller
def ChangeAnim(value: TriggerInt, elem: Optional[TriggerInt] = None) -> state.Controller:
    result = state.Controller()

    result.params["value"] = value
    if elem != None:
        result.params["elem"] = elem

    return result

@controller
def ChangeState(value: Union[TriggerInt, str, Callable], ctrl: Optional[TriggerBool] = None, anim: Optional[TriggerInt] = None) -> state.Controller:
    result = state.Controller()

    if type(value) == Callable:
        result.params["value"] = value.__name__
    else:
        result.params["value"] = value

    if ctrl != None:
        result.params["ctrl"] = ctrl
    
    if anim != None:
        result.params["anim"] = anim

    return result

@controller
def PalFX(
    time: Optional[TriggerInt] = None,
    add: Optional[TriggerRgb] = None,
    mul: Optional[TriggerRgb] = None,
    sinadd: Optional[TriggerRgba] = None,
    invertall: Optional[TriggerBool] = None,
    color: Optional[TriggerInt] = None,
) -> state.Controller:
    result = state.Controller()

    if time != None: result.params["time"] = time
    if add != None: result.params["add"] = format_tuple(add)
    if mul != None: result.params["mul"] = format_tuple(mul)
    if sinadd != None: result.params["sinadd"] = format_tuple(sinadd)
    if invertall != None: result.params["invertall"] = format_bool(invertall)
    if color != None: result.params["color"] = color

    return result

@controller
def VelSet(x: Optional[TriggerFloat] = None, y: Optional[TriggerFloat] = None) -> state.Controller:
    result = state.Controller()

    if x != None:
        result.params["x"] = x
    if y != None:
        result.params["y"] = y

    return result