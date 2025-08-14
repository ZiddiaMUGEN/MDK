from typing import Union, Callable, Optional
from functools import partial

from mdk.utils.controllers import controller
from mdk.utils.shared import convert

from mdk.types.specifier import TypeSpecifier
from mdk.types.context import StateController
from mdk.types.builtins import *
from mdk.types.defined import *
from mdk.types.expressions import Expression, TupleExpression, ConvertibleExpression

def set_if(ctrl: StateController, name: str, val: Optional[ConvertibleExpression]):
    if val != None:
        if not isinstance(val, Expression):
            val = convert(val)
        ctrl.params[name] = val

def set_if_tuple(ctrl: StateController, name: str, val: Optional[TupleExpression], type: TypeSpecifier):
    if val != None:
        converted = []
        for v in val:
            if isinstance(v, Expression):
                converted.append(v)
            else:
                converted.append(convert(v))
        exprn_string = ", ".join([t.exprn for t in converted])
        ctrl.params[name] = Expression(exprn_string, type)

def set_stateno(ctrl: StateController, name: str, val: Optional[Union[Expression, Callable[..., None], str, int]]):
    if val != None:
        if isinstance(val, partial):
            if "value" in val.keywords:
                ctrl.params[name] = Expression(val.keywords["value"], StateNoType)
            elif len(val.args) == 1:
                ctrl.params[name] = Expression(val.args[0], StateNoType)
            else:
                raise Exception(f"Could not determine target state definition name from input: {val} - bug the developers.")
        elif isinstance(val, Callable):
            ctrl.params[name] = Expression(val.__name__, StateNoType)
        elif isinstance(val, str):
            ctrl.params[name] = Expression(val, StateNoType)
        elif isinstance(val, int):
            ctrl.params[name] = Expression(str(val), StateNoType)
        elif isinstance(val, Expression) and val.type == StringType:
            ctrl.params[name] = Expression(val.exprn, StateNoType)
        else:
            ctrl.params[name] = Expression(val.exprn, StateNoType)

@controller(
    time = [IntType, None],
    length = [IntType, None],
    palcolor = [IntType, None],
    palinvertall = [BoolType, None],
    palbright = [ColorType, None],
    palcontrast = [ColorType, None],
    palpostbright = [ColorType, None],
    paladd = [ColorType, None],
    palmul = [ColorMultType, None],
    timegap = [IntType, None],
    framegap = [IntType, None],
    trans = [TransType, None]
)
def AfterImage(
    time: Optional[ConvertibleExpression] = None, 
    length: Optional[ConvertibleExpression] = None, 
    palcolor: Optional[ConvertibleExpression] = None, 
    palinvertall: Optional[ConvertibleExpression] = None, 
    palbright: Optional[TupleExpression] = None, 
    palcontrast: Optional[TupleExpression] = None, 
    palpostbright: Optional[TupleExpression] = None, 
    paladd: Optional[TupleExpression] = None, 
    palmul: Optional[TupleExpression] = None, 
    timegap: Optional[ConvertibleExpression] = None, 
    framegap: Optional[ConvertibleExpression] = None, 
    trans: Optional[ConvertibleExpression] = None, 
	ignorehitpause: Optional[ConvertibleExpression] = None, 
	persistent: Optional[ConvertibleExpression] = None
) -> StateController:
    result = StateController()

    set_if(result, "time", time)
    set_if(result, "length", length)
    set_if(result, "palcolor", palcolor)
    set_if(result, "palinvertall", palinvertall)

    set_if_tuple(result, "palbright", palbright, ColorType)
    set_if_tuple(result, "palcontrast", palcontrast, ColorType)
    set_if_tuple(result, "palpostbright", palpostbright, ColorType)
    set_if_tuple(result, "paladd", paladd, ColorType)
    set_if_tuple(result, "palmul", palmul, ColorMultType)

    set_if(result, "timegap", timegap)
    set_if(result, "framegap", framegap)
    set_if(result, "trans", trans)

    return result

@controller(time = [IntType])
def AfterImageTime(time: ConvertibleExpression, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "time", time)

    return result

@controller(value = [FloatType])
def AngleAdd(value: ConvertibleExpression, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "value", value)

    return result

@controller(value = [FloatType, None], scale = [FloatPairType, None])
def AngleDraw(value: Optional[ConvertibleExpression] = None, scale: Optional[TupleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "value", value)
    set_if_tuple(result, "scale", scale, FloatPairType)

    return result

@controller(value = [FloatType])
def AngleMul(value: ConvertibleExpression, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "value", value)

    return result

@controller(value = [FloatType])
def AngleSet(value: ConvertibleExpression, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "value", value)

    return result

"""
@controller(text = [StringType], params = [AnyType, None])
def AppendToClipboard(text: ConvertibleExpression, params: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    return result
"""

@controller(flag = [AssertType], flag2 = [AssertType, None], flag3 = [AssertType, None])
def AssertSpecial(flag: ConvertibleExpression, flag2: Optional[ConvertibleExpression] = None, flag3: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "flag", flag)
    set_if(result, "flag2", flag2)
    set_if(result, "flag3", flag3)

    return result

@controller(value = [IntType])
def AttackDist(value: ConvertibleExpression, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "value", value)

    return result

@controller(value = [FloatType])
def AttackMulSet(value: ConvertibleExpression, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "value", value)

    return result

@controller(time = [IntType, None], facing = [IntType, None], pos = [FloatPairType, None])
def BindToParent(time: Optional[ConvertibleExpression] = None, facing: Optional[ConvertibleExpression] = None, pos: Optional[TupleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "time", time)
    set_if(result, "facing", facing)
    set_if_tuple(result, "pos", pos, FloatPairType)

    return result

@controller(time = [IntType, None], facing = [IntType, None], pos = [FloatPairType, None])
def BindToRoot(time: Optional[ConvertibleExpression] = None, facing: Optional[ConvertibleExpression] = None, pos: Optional[TupleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "time", time)
    set_if(result, "facing", facing)
    set_if_tuple(result, "pos", pos, FloatPairType)

    return result

@controller(time = [IntType, None], id = [IntType, None], pos = [FloatPosType, None])
def BindToTarget(time: Optional[ConvertibleExpression] = None, id: Optional[ConvertibleExpression] = None, pos: Optional[TupleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "time", time)
    set_if(result, "id", id)
    set_if_tuple(result, "pos", pos, FloatPairType)

    return result

@controller(value = [IntType], elem = [IntType, None])
def ChangeAnim(value: ConvertibleExpression, elem: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "value", value)
    set_if(result, "elem", elem)

    return result

@controller(value = [IntType], elem = [IntType, None])
def ChangeAnim2(value: ConvertibleExpression, elem: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "value", value)
    set_if(result, "elem", elem)

    return result

@controller(value = [StateNoType, IntType, StringType], ctrl = [None, BoolType], anim = [None, IntType])
def ChangeState(value: Union[Expression, str, int, Callable[..., None]], ctrl: Optional[ConvertibleExpression] = None, anim: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_stateno(result, "value", value)

    set_if(result, "ctrl", ctrl)
    set_if(result, "anim", anim)

    return result

@controller()
def ClearClipboard(ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()
    return result

@controller(ctrl = [BoolType, None], value = [BoolType, None])
def CtrlSet(ctrl: Optional[ConvertibleExpression] = None, value: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "ctrl", ctrl)
    set_if(result, "value", value)

    return result

@controller(value = [FloatType])
def DefenceMulSet(value: ConvertibleExpression, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "value", value)

    return result

@controller()
def DestroySelf(ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()
    return result

"""
@controller(text = [StringType], params = [AnyType, None])
def DisplayToClipboard(text: ConvertibleExpression, params: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    return result
"""

@controller(value = [ColorType, None], time = [IntType, None], under = [BoolType, None])
def EnvColor(value: Optional[TupleExpression] = None, time: Optional[ConvertibleExpression] = None, under: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if_tuple(result, "value", value, ColorType)
    set_if(result, "time", time)
    set_if(result, "under", under)

    return result

@controller(time = [IntType], freq = [FloatType, None], ampl = [IntType, None], phase = [FloatType, None])
def EnvShake(time: ConvertibleExpression, freq: Optional[ConvertibleExpression] = None, ampl: Optional[ConvertibleExpression] = None, phase: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "time", time)
    set_if(result, "freq", freq)
    set_if(result, "ampl", ampl)
    set_if(result, "phase", phase)

    return result

@controller(
    anim = [AnimType],
    id = [IntType, None],
    pos = [FloatPairType, None],
    postype = [PosType, None],
    facing = [IntType, None],
    vfacing = [IntType, None],
    bindtime = [IntType, None],
    vel = [FloatPairType, None],
    accel = [FloatPairType, None],
    random = [IntPairType, None],
    removetime = [IntType, None],
    supermove = [BoolType, None],
    supermovetime = [IntType, None],
    pausemovetime = [IntType, None],
    scale = [FloatPairType, None],
    sprpriority = [IntType, None],
    ontop = [BoolType, None],
    shadow = [BoolType, None],
    ownpal = [BoolType, None],
    removeongethit = [BoolType, None],
    ignorehitpause = [BoolType, None],
    trans = [TransType, None]
)
def Explod(
    anim: ConvertibleExpression, 
    id: Optional[ConvertibleExpression] = None, 
    pos: Optional[TupleExpression] = None, 
    postype: Optional[ConvertibleExpression] = None, 
    facing: Optional[ConvertibleExpression] = None, 
    vfacing: Optional[ConvertibleExpression] = None, 
    bindtime: Optional[ConvertibleExpression] = None, 
    vel: Optional[TupleExpression] = None, 
    accel: Optional[TupleExpression] = None, 
    random: Optional[TupleExpression] = None, 
    removetime: Optional[ConvertibleExpression] = None, 
    supermove: Optional[ConvertibleExpression] = None, 
    supermovetime: Optional[ConvertibleExpression] = None, 
    pausemovetime: Optional[ConvertibleExpression] = None, 
    scale: Optional[TupleExpression] = None, 
    sprpriority: Optional[ConvertibleExpression] = None, 
    ontop: Optional[ConvertibleExpression] = None, 
    shadow: Optional[ConvertibleExpression] = None, 
    ownpal: Optional[ConvertibleExpression] = None, 
    removeongethit: Optional[ConvertibleExpression] = None, 
    trans: Optional[ConvertibleExpression] = None, 
	ignorehitpause: Optional[ConvertibleExpression] = None, 
	persistent: Optional[ConvertibleExpression] = None
) -> StateController:
    result = StateController()

    set_if(result, "anim", anim)
    set_if(result, "id", id)
    set_if_tuple(result, "pos", pos, FloatPairType)
    set_if(result, "postype", postype)
    set_if(result, "facing", facing)
    set_if(result, "vfacing", vfacing)
    set_if(result, "bindtime", bindtime)
    set_if_tuple(result, "vel", vel, FloatPairType)
    set_if_tuple(result, "accel", accel, FloatPairType)
    set_if_tuple(result, "random", random, IntPairType)
    set_if(result, "removetime", removetime)
    set_if(result, "supermove", supermove)
    set_if(result, "supermovetime", supermovetime)
    set_if(result, "pausemovetime", pausemovetime)
    set_if_tuple(result, "scale", scale, FloatPairType)
    set_if(result, "sprpriority", sprpriority)
    set_if(result, "ontop", ontop)
    set_if(result, "shadow", shadow)
    set_if(result, "ownpal", ownpal)
    set_if(result, "removeongethit", removeongethit)
    set_if(result, "trans", trans)

    return result

@controller(id = [IntType, None], time = [IntType, None])
def ExplodBindTime(id: Optional[ConvertibleExpression] = None, time: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "id", id)
    set_if(result, "time", time)

    return result

@controller(
    waveform = [WaveType, None],
    time = [IntType, None],
    freq = [WaveTupleType, None],
    ampl = [WaveTupleType, None],
    self = [BoolType, None]
)
def ForceFeedback(waveform: Optional[ConvertibleExpression] = None, time: Optional[ConvertibleExpression] = None, freq: Optional[TupleExpression] = None, ampl: Optional[TupleExpression] = None, self: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "waveform", waveform)
    set_if(result, "time", time)
    set_if_tuple(result, "freq", freq, WaveTupleType)
    set_if_tuple(result, "ampl", ampl, WaveTupleType)
    set_if(result, "self", self)

    return result

@controller()
def FallEnvShake(ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()
    return result

@controller(value = [IntType, None], under = [BoolType, None], pos = [FloatPairType, None], random = [IntType, None])
def GameMakeAnim(value: Optional[ConvertibleExpression] = None, under: Optional[ConvertibleExpression] = None, pos: Optional[TupleExpression] = None, random: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "value", value)
    set_if(result, "under", under)
    set_if_tuple(result, "pos", pos, FloatPairType)
    set_if(result, "random", random)

    return result

@controller()
def Gravity(ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()
    return result

@controller(
    helpertype = [HelperType, None],
    name = [StringType, None],
    id = [IntType, None],
    pos = [FloatPairType, None],
    postype = [PosType, None],
    facing = [IntType, None],
    stateno = [StateNoType, IntType, StringType, None],
    keyctrl = [BoolType, None],
    ownpal = [BoolType, None],
    supermovetime = [IntType, None],
    pausemovetime = [IntType, None],
    size_xscale = [FloatType, None],
    size_yscale = [FloatType, None],
    size_ground_back = [IntType, None],
    size_ground_front = [IntType, None],
    size_air_back = [IntType, None],
    size_air_front = [IntType, None],
    size_height = [IntType, None],
    size_proj_doscale = [IntType, None],
    size_head_pos = [IntPairType, None],
    size_mid_pos = [IntPairType, None],
    size_shadowoffset = [IntType, None]
)
def Helper(
    helpertype: Optional[ConvertibleExpression] = None, 
    name: Optional[ConvertibleExpression] = None, 
    id: Optional[ConvertibleExpression] = None, 
    pos: Optional[TupleExpression] = None, 
    postype: Optional[ConvertibleExpression] = None, 
    facing: Optional[ConvertibleExpression] = None,
    stateno: Optional[Union[Expression, str, int, Callable[..., None]]] = None, 
    keyctrl: Optional[ConvertibleExpression] = None, 
    ownpal: Optional[ConvertibleExpression] = None, 
    supermovetime: Optional[ConvertibleExpression] = None, 
    pausemovetime: Optional[ConvertibleExpression] = None, 
    size_xscale: Optional[ConvertibleExpression] = None, 
    size_yscale: Optional[ConvertibleExpression] = None, 
    size_ground_back: Optional[ConvertibleExpression] = None, 
    size_ground_front: Optional[ConvertibleExpression] = None, 
    size_air_back: Optional[ConvertibleExpression] = None, 
    size_air_front: Optional[ConvertibleExpression] = None, 
    size_height: Optional[ConvertibleExpression] = None, 
    size_proj_doscale: Optional[ConvertibleExpression] = None, 
    size_head_pos: Optional[TupleExpression] = None, 
    size_mid_pos: Optional[TupleExpression] = None, 
    size_shadowoffset: Optional[ConvertibleExpression] = None, 
	ignorehitpause: Optional[ConvertibleExpression] = None, 
	persistent: Optional[ConvertibleExpression] = None
) -> StateController:
    result = StateController()

    set_if(result, "helpertype", helpertype)
    set_if(result, "name", name)
    set_if(result, "id", id)
    set_if_tuple(result, "pos", pos, FloatPairType)
    set_if(result, "postype", postype)
    set_if(result, "facing", facing)
    set_stateno(result, "stateno", stateno)
    set_if(result, "keyctrl", keyctrl)
    set_if(result, "ownpal", ownpal)
    set_if(result, "supermovetime", supermovetime)
    set_if(result, "pausemovetime", pausemovetime)
    set_if(result, "size.xscale", size_xscale)
    set_if(result, "size.yscale", size_yscale)
    set_if(result, "size.ground.back", size_ground_back)
    set_if(result, "size.ground.front", size_ground_front)
    set_if(result, "size.air.back", size_air_back)
    set_if(result, "size.air.front", size_air_front)
    set_if(result, "size.height", size_height)
    set_if(result, "size.proj.doscale", size_proj_doscale)
    set_if_tuple(result, "size.head.pos", size_head_pos, IntPairType)
    set_if_tuple(result, "size.mid.pos", size_mid_pos, IntPairType)
    set_if(result, "size.shadowoffset", size_shadowoffset)

    return result

@controller(value = [IntType])
def HitAdd(value: ConvertibleExpression, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "value", value)

    return result

@controller(value = [HitStringType, None], value2 = [HitStringType, None], time = [IntType, None])
def HitBy(value: Optional[TupleExpression] = None, value2: Optional[TupleExpression] = None, time: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if_tuple(result, "value", value, HitStringType)
    set_if_tuple(result, "value2", value2, HitStringType)
    set_if(result, "time", time)

    return result

@controller(
    attr = [HitStringType],
    hitflag = [HitFlagType, None],
    guardflag = [GuardFlagType, None],
    affectteam = [TeamType, None],
    animtype = [HitAnimType, None],
    air_animtype = [HitAnimType, None],
    fall_animtype = [HitAnimType, None],
    priority = [PriorityPairType, None],
    damage = [IntPairType, None],
    pausetime = [IntPairType, None],
    guard_pausetime = [IntPairType, None],
    sparkno = [SpriteType, None],
    guard_sparkno = [SpriteType, None],
    sparkxy = [IntPairType, None],
    hitsound = [SoundPairType, None],
    guardsound = [SoundPairType, None],
    ground_type = [AttackType, None],
    air_type = [AttackType, None],
    ground_slidetime = [IntType, None],
    guard_slidetime = [IntType, None],
    ground_hittime = [IntType, None],
    guard_hittime = [IntType, None],
    air_hittime = [IntType, None],
    guard_ctrltime = [IntType, None],
    guard_dist = [IntType, None],
    yaccel = [FloatType, None],
    ground_velocity = [FloatType, None],
    guard_velocity = [FloatType, None],
    air_velocity = [FloatPairType, None],
    airguard_velocity = [FloatPairType, None],
    ground_cornerpush_veloff = [FloatType, None],
    air_cornerpush_veloff = [FloatType, None],
    down_cornerpush_veloff = [FloatType, None],
    guard_cornerpush_veloff = [FloatType, None],
    airguard_cornerpush_veloff = [FloatType, None],
    airguard_ctrltime = [IntType, None],
    air_juggle = [IntType, None],
    mindist = [IntPairType, None],
    maxdist = [IntPairType, None],
    snap = [IntPairType, None],
    p1sprpriority = [IntType, None],
    p2sprpriority = [IntType, None],
    p1facing = [IntType, None],
    p1getp2facing = [IntType, None],
    p2facing = [IntType, None],
    p1stateno = [StateNoType, IntType, StringType, None],
    p2stateno = [StateNoType, IntType, StringType, None],
    p2getp1state = [BoolType, None],
    forcestand = [BoolType, None],
    fall = [BoolType, None],
    fall_xvelocity = [FloatType, None],
    fall_yvelocity = [FloatType, None],
    fall_recover = [BoolType, None],
    fall_recovertime = [IntType, None],
    fall_damage = [IntType, None],
    air_fall = [BoolType, None],
    forcenofall = [BoolType, None],
    down_velocity = [FloatPairType, None],
    down_hittime = [IntType, None],
    down_bounce = [BoolType, None],
    id = [IntType, None],
    chainid = [IntType, None],
    nochainid = [IntPairType, None],
    hitonce = [BoolType, None],
    kill = [BoolType, None],
    guard_kill = [BoolType, None],
    fall_kill = [BoolType, None],
    numhits = [IntType, None],
    getpower = [IntPairType, None],
    givepower = [IntPairType, None],
    palfx_time = [IntType, None],
    palfx_mul = [ColorType, None],
    palfx_add = [ColorType, None],
    envshake_time = [IntType, None],
    envshake_freq = [FloatType, None],
    envshake_ampl = [IntType, None],
    envshake_phase = [FloatType, None],
    fall_envshake_time = [IntType, None],
    fall_envshake_freq = [FloatType, None],
    fall_envshake_ampl = [IntType, None],
    fall_envshake_phase = [FloatType, None]
)
def HitDef(
    attr: TupleExpression,
    hitflag: Optional[ConvertibleExpression] = None,
    guardflag: Optional[ConvertibleExpression] = None,
    affectteam: Optional[ConvertibleExpression] = None,
    animtype: Optional[ConvertibleExpression] = None,
    air_animtype: Optional[ConvertibleExpression] = None,
    fall_animtype: Optional[ConvertibleExpression] = None,
    priority: Optional[TupleExpression] = None,
    damage: Optional[ConvertibleExpression] = None,
    pausetime: Optional[ConvertibleExpression] = None,
    guard_pausetime: Optional[ConvertibleExpression] = None,
    sparkno: Optional[ConvertibleExpression] = None,
    guard_sparkno: Optional[ConvertibleExpression] = None,
    sparkxy: Optional[TupleExpression] = None,
    hitsound: Optional[TupleExpression] = None,
    guardsound: Optional[TupleExpression] = None,
    ground_type: Optional[ConvertibleExpression] = None,
    air_type: Optional[ConvertibleExpression] = None,
    ground_slidetime: Optional[ConvertibleExpression] = None,
    guard_slidetime: Optional[ConvertibleExpression] = None,
    ground_hittime: Optional[ConvertibleExpression] = None,
    guard_hittime: Optional[ConvertibleExpression] = None,
    air_hittime: Optional[ConvertibleExpression] = None,
    guard_ctrltime: Optional[ConvertibleExpression] = None,
    guard_dist: Optional[ConvertibleExpression] = None,
    yaccel: Optional[ConvertibleExpression] = None,
    ground_velocity: Optional[TupleExpression] = None,
    guard_velocity: Optional[TupleExpression] = None,
    air_velocity: Optional[TupleExpression] = None,
    airguard_velocity: Optional[TupleExpression] = None,
    ground_cornerpush_veloff: Optional[ConvertibleExpression] = None,
    air_cornerpush_veloff: Optional[ConvertibleExpression] = None,
    down_cornerpush_veloff: Optional[ConvertibleExpression] = None,
    guard_cornerpush_veloff: Optional[ConvertibleExpression] = None,
    airguard_cornerpush_veloff: Optional[ConvertibleExpression] = None,
    airguard_ctrltime: Optional[ConvertibleExpression] = None,
    air_juggle: Optional[ConvertibleExpression] = None,
    mindist: Optional[TupleExpression] = None,
    maxdist: Optional[TupleExpression] = None,
    snap: Optional[TupleExpression] = None,
    p1sprpriority: Optional[ConvertibleExpression] = None,
    p2sprpriority: Optional[ConvertibleExpression] = None,
    p1facing: Optional[ConvertibleExpression] = None,
    p1getp2facing: Optional[ConvertibleExpression] = None,
    p2facing: Optional[ConvertibleExpression] = None,
    p1stateno: Optional[Union[Expression, str, int, Callable[..., None]]] = None,
    p2stateno: Optional[Union[Expression, str, int, Callable[..., None]]] = None,
    p2getp1state: Optional[ConvertibleExpression] = None,
    forcestand: Optional[ConvertibleExpression] = None,
    fall: Optional[ConvertibleExpression] = None,
    fall_xvelocity: Optional[ConvertibleExpression] = None,
    fall_yvelocity: Optional[ConvertibleExpression] = None,
    fall_recover: Optional[ConvertibleExpression] = None,
    fall_recovertime: Optional[ConvertibleExpression] = None,
    fall_damage: Optional[ConvertibleExpression] = None,
    air_fall: Optional[ConvertibleExpression] = None,
    forcenofall: Optional[ConvertibleExpression] = None,
    down_velocity: Optional[TupleExpression] = None,
    down_hittime: Optional[ConvertibleExpression] = None,
    down_bounce: Optional[ConvertibleExpression] = None,
    chainid: Optional[ConvertibleExpression] = None,
    nochainid: Optional[TupleExpression] = None,
    hitonce: Optional[ConvertibleExpression] = None,
    kill: Optional[ConvertibleExpression] = None,
    guard_kill: Optional[ConvertibleExpression] = None,
    fall_kill: Optional[ConvertibleExpression] = None,
    numhits: Optional[ConvertibleExpression] = None,
    getpower: Optional[TupleExpression] = None,
    givepower: Optional[TupleExpression] = None,
    palfx_time: Optional[ConvertibleExpression] = None,
    palfx_mul: Optional[TupleExpression] = None,
    palfx_add: Optional[TupleExpression] = None,
    envshake_time: Optional[ConvertibleExpression] = None,
    envshake_freq: Optional[ConvertibleExpression] = None,
    envshake_ampl: Optional[ConvertibleExpression] = None,
    envshake_phase: Optional[ConvertibleExpression] = None,
    fall_envshake_time: Optional[ConvertibleExpression] = None,
    fall_envshake_freq: Optional[ConvertibleExpression] = None,
    fall_envshake_ampl: Optional[ConvertibleExpression] = None,
    fall_envshake_phase: Optional[ConvertibleExpression] = None, 
	ignorehitpause: Optional[ConvertibleExpression] = None, 
	persistent: Optional[ConvertibleExpression] = None
) -> StateController:
    result = StateController()

    set_if_tuple(result, "attr", attr, HitStringType)
    set_if(result, "hitflag", hitflag)
    set_if(result, "guardflag", guardflag)
    set_if(result, "affectteam", affectteam)
    set_if(result, "animtype", animtype)
    set_if(result, "air.animtype", air_animtype)
    set_if(result, "fall.animtype", fall_animtype)
    set_if_tuple(result, "priority", priority, PriorityPairType)
    set_if(result, "damage", damage)
    set_if(result, "pausetime", pausetime)
    set_if(result, "guard.pausetime", guard_pausetime)
    set_if(result, "sparkno", sparkno)
    set_if(result, "guard.sparkno", guard_sparkno)
    set_if_tuple(result, "sparkxy", sparkxy, IntPairType)
    set_if_tuple(result, "hitsound", hitsound, SoundPairType)
    set_if_tuple(result, "guardsound", guardsound, SoundPairType)
    set_if(result, "ground.type", ground_type)
    set_if(result, "air.type", air_type)
    set_if(result, "ground.slidetime", ground_slidetime)
    set_if(result, "guard.slidetime", guard_slidetime)
    set_if(result, "ground.hittime", ground_hittime)
    set_if(result, "guard.hittime", guard_hittime)
    set_if(result, "air.hittime", air_hittime)
    set_if(result, "guard.ctrltime", guard_ctrltime)
    set_if(result, "guard.dist", guard_dist)
    set_if(result, "yaccel", yaccel)
    set_if_tuple(result, "ground.velocity", ground_velocity, FloatPairType)
    set_if_tuple(result, "guard.velocity", guard_velocity, FloatPairType)
    set_if_tuple(result, "air.velocity", air_velocity, FloatPairType)
    set_if_tuple(result, "airguard.velocity", airguard_velocity, FloatPairType)
    set_if(result, "ground.cornerpush.veloff", ground_cornerpush_veloff)
    set_if(result, "air.cornerpush.veloff", air_cornerpush_veloff)
    set_if(result, "down.cornerpush.veloff", down_cornerpush_veloff)
    set_if(result, "guard.cornerpush.veloff", guard_cornerpush_veloff)
    set_if(result, "airguard.cornerpush.veloff", airguard_cornerpush_veloff)
    set_if(result, "airguard.ctrltime", airguard_ctrltime)
    set_if(result, "air.juggle", air_juggle)
    set_if_tuple(result, "mindist", mindist, IntPairType)
    set_if_tuple(result, "maxdist", maxdist, IntPairType)
    set_if_tuple(result, "snap", snap, IntPairType)
    set_if(result, "p1sprpriority", p1sprpriority)
    set_if(result, "p2sprpriority", p2sprpriority)
    set_if(result, "p1facing", p1facing)
    set_if(result, "p1getp2facing", p1getp2facing)
    set_if(result, "p2facing", p2facing)
    set_stateno(result, "p1stateno", p1stateno)
    set_stateno(result, "p2stateno", p2stateno)
    set_if(result, "p2getp1state", p2getp1state)
    set_if(result, "forcestand", forcestand)
    set_if(result, "fall", fall)
    set_if(result, "fall.xvelocity", fall_xvelocity)
    set_if(result, "fall.yvelocity", fall_yvelocity)
    set_if(result, "fall.recover", fall_recover)
    set_if(result, "fall.recovertime", fall_recovertime)
    set_if(result, "fall.damage", fall_damage)
    set_if(result, "air.fall", air_fall)
    set_if(result, "forcenofall", forcenofall)
    set_if_tuple(result, "down.velocity", down_velocity, FloatPairType)
    set_if(result, "down.hittime", down_hittime)
    set_if(result, "down.bounce", down_bounce)
    set_if(result, "chainid", chainid)
    set_if_tuple(result, "nochainid", nochainid, IntPairType)
    set_if(result, "hitonce", hitonce)
    set_if(result, "kill", kill)
    set_if(result, "guard.kill", guard_kill)
    set_if(result, "fall.kill", fall_kill)
    set_if(result, "numhits", numhits)
    set_if_tuple(result, "getpower", getpower, IntPairType)
    set_if_tuple(result, "givepower", givepower, IntPairType)
    set_if(result, "palfx.time", palfx_time)
    set_if_tuple(result, "palfx.mul", palfx_mul, ColorType)
    set_if_tuple(result, "palfx.add", palfx_add, ColorType)
    set_if(result, "envshake.time", envshake_time)
    set_if(result, "envshake.freq", envshake_freq)
    set_if(result, "envshake.ampl", envshake_ampl)
    set_if(result, "envshake.phase", envshake_phase)
    set_if(result, "fall.envshake.time", fall_envshake_time)
    set_if(result, "fall.envshake.freq", fall_envshake_freq)
    set_if(result, "fall.envshake.ampl", fall_envshake_ampl)
    set_if(result, "fall.envshake.phase", fall_envshake_phase)

    return result

@controller()
def HitFallDamage(ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()
    return result

@controller(value = [IntType, None], xvel = [FloatType, None], yvel = [FloatType, None])
def HitFallSet(value: Optional[ConvertibleExpression] = None, xvel: Optional[ConvertibleExpression] = None, yvel: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "value", value)
    set_if(result, "xvel", xvel)
    set_if(result, "yvel", yvel)

    return result

@controller()
def HitFallVel(ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()
    return result

@controller(
    attr = [HitStringType],
    stateno = [StateNoType, IntType, StringType, None],
    slot = [IntType, None],
    time = [IntType, None],
    forceair = [BoolType, None]
)
def HitOverride(attr: TupleExpression, stateno: Optional[Union[Expression, str, int, Callable[..., None]]] = None, slot: Optional[ConvertibleExpression] = None, time: Optional[ConvertibleExpression] = None, forceair: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if_tuple(result, "attr", attr, HitStringType)
    set_stateno(result, "stateno", stateno)
    set_if(result, "slot", slot)
    set_if(result, "time", time)
    set_if(result, "forceair", forceair)

    return result

@controller(x = [BoolType, None], y = [BoolType, None])
def HitVelSet(x: Optional[ConvertibleExpression] = None, y: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "x", x)
    set_if(result, "y", y)

    return result

@controller(value = [IntType], kill = [BoolType, None], absolute = [BoolType, None])
def LifeAdd(value: ConvertibleExpression, kill: Optional[ConvertibleExpression] = None, absolute: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "value", value)
    set_if(result, "kill", kill)
    set_if(result, "absolute", absolute)

    return result

@controller(value = [IntType])
def LifeSet(value: ConvertibleExpression, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "value", value)

    return result

@controller(pos = [IntPairType, None], pos2 = [FloatPairType, None], spacing = [IntType, None])
def MakeDust(pos: Optional[TupleExpression] = None, pos2: Optional[TupleExpression] = None, spacing: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if_tuple(result, "pos", pos, IntPairType)
    set_if_tuple(result, "pos2", pos2, FloatPairType)
    set_if(result, "spacing", spacing)

    return result

@controller(
    id = [IntType],
    pos = [FloatPairType, None],
    postype = [PosType, None],
    facing = [IntType, None],
    vfacing = [IntType, None],
    bindtime = [IntType, None],
    vel = [FloatPairType, None],
    accel = [FloatPairType, None],
    random = [IntPairType, None],
    removetime = [IntType, None],
    supermove = [BoolType, None],
    supermovetime = [IntType, None],
    pausemovetime = [IntType, None],
    scale = [FloatPairType, None],
    sprpriority = [IntType, None],
    ontop = [BoolType, None],
    shadow = [BoolType, None],
    ownpal = [BoolType, None],
    removeongethit = [BoolType, None],
    ignorehitpause = [BoolType, None],
    trans = [TransType, None]
)
def ModifyExplod(
    id: ConvertibleExpression, 
    pos: Optional[TupleExpression] = None, 
    postype: Optional[ConvertibleExpression] = None, 
    facing: Optional[ConvertibleExpression] = None, 
    vfacing: Optional[ConvertibleExpression] = None, 
    bindtime: Optional[ConvertibleExpression] = None, 
    vel: Optional[TupleExpression] = None, 
    accel: Optional[TupleExpression] = None, 
    random: Optional[TupleExpression] = None, 
    removetime: Optional[ConvertibleExpression] = None, 
    supermove: Optional[ConvertibleExpression] = None, 
    supermovetime: Optional[ConvertibleExpression] = None, 
    pausemovetime: Optional[ConvertibleExpression] = None, 
    scale: Optional[TupleExpression] = None, 
    sprpriority: Optional[ConvertibleExpression] = None, 
    ontop: Optional[ConvertibleExpression] = None, 
    shadow: Optional[ConvertibleExpression] = None, 
    ownpal: Optional[ConvertibleExpression] = None, 
    removeongethit: Optional[ConvertibleExpression] = None, 
    trans: Optional[ConvertibleExpression] = None, 
	ignorehitpause: Optional[ConvertibleExpression] = None, 
	persistent: Optional[ConvertibleExpression] = None
) -> StateController:
    result = StateController()

    set_if(result, "id", id)
    set_if_tuple(result, "pos", pos, FloatPairType)
    set_if(result, "postype", postype)
    set_if(result, "facing", facing)
    set_if(result, "vfacing", vfacing)
    set_if(result, "bindtime", bindtime)
    set_if_tuple(result, "vel", vel, FloatPairType)
    set_if_tuple(result, "accel", accel, FloatPairType)
    set_if_tuple(result, "random", random, IntPairType)
    set_if(result, "removetime", removetime)
    set_if(result, "supermove", supermove)
    set_if(result, "supermovetime", supermovetime)
    set_if(result, "pausemovetime", pausemovetime)
    set_if_tuple(result, "scale", scale, FloatPairType)
    set_if(result, "sprpriority", sprpriority)
    set_if(result, "ontop", ontop)
    set_if(result, "shadow", shadow)
    set_if(result, "ownpal", ownpal)
    set_if(result, "removeongethit", removeongethit)
    set_if(result, "trans", trans)

    return result

@controller()
def MoveHitReset(ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()
    return result

@controller(value = [HitStringType, None], value2 = [HitStringType, None], time = [IntType, None])
def NotHitBy(value: Optional[TupleExpression] = None, value2: Optional[TupleExpression] = None, time: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if_tuple(result, "value", value, HitStringType)
    set_if_tuple(result, "value2", value2, HitStringType)
    set_if(result, "time", time)

    return result

@controller()
def Null(ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()
    return result

@controller(x = [FloatType, None], y = [FloatType, None])
def Offset(x: Optional[ConvertibleExpression] = None, y: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "x", x)
    set_if(result, "y", y)

    return result

@controller(
    time = [IntType, None],
    add = [ColorType, None],
    mul = [ColorType, None],
    sinadd = [PeriodicColorType, None],
    invertall = [BoolType, None],
    color = [IntType, None]
)
def PalFX(
    time: Optional[ConvertibleExpression] = None, 
    add: Optional[TupleExpression] = None, 
    mul: Optional[TupleExpression] = None, 
    sinadd: Optional[TupleExpression] = None, 
    invertall: Optional[ConvertibleExpression] = None, 
    color: Optional[ConvertibleExpression] = None, 
	ignorehitpause: Optional[ConvertibleExpression] = None, 
	persistent: Optional[ConvertibleExpression] = None
) -> StateController:
    result = StateController()

    set_if(result, "time", time)
    set_if_tuple(result, "add", add, ColorType)
    set_if_tuple(result, "mul", mul, ColorType)
    set_if_tuple(result, "sinadd", sinadd, PeriodicColorType)
    set_if(result, "invertall", invertall)
    set_if(result, "color", color)

    return result

@controller(var = [IntType, FloatType, None], value = [IntType, FloatType, None])
def ParentVarAdd(var: Optional[Expression] = None, value: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    if var != None:
        set_if(result, var.exprn, value)

    return result

@controller(var = [IntType, FloatType, None], value = [IntType, FloatType, None])
def ParentVarSet(var: Optional[Expression] = None, value: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    if var != None:
        set_if(result, var.exprn, value)

    return result

@controller(time = [IntType], endcmdbuftime = [IntType, None], movetime = [IntType, None], pausebg = [BoolType, None])
def Pause(time: ConvertibleExpression, endcmdbuftime: Optional[ConvertibleExpression] = None, movetime: Optional[ConvertibleExpression] = None, pausebg: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "time", time)
    set_if(result, "endcmdbuftime", endcmdbuftime)
    set_if(result, "movetime", movetime)
    set_if(result, "pausebg", pausebg)

    return result

@controller(value = [BoolType])
def PlayerPush(value: ConvertibleExpression, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "value", value)

    return result

@controller(
    value = [SoundPairType],
    volumescale = [FloatType, None],
    channel = [IntType, None],
    lowpriority = [BoolType, None],
    freqmul = [FloatType, None],
    loop = [BoolType, None],
    pan = [IntType, None],
    abspan = [IntType, None]
)
def PlaySnd(
    value: TupleExpression, 
    volumescale: Optional[ConvertibleExpression] = None, 
    channel: Optional[ConvertibleExpression] = None, 
    lowpriority: Optional[ConvertibleExpression] = None, 
    freqmul: Optional[ConvertibleExpression] = None, 
    loop: Optional[ConvertibleExpression] = None, 
    pan: Optional[ConvertibleExpression] = None, 
    abspan: Optional[ConvertibleExpression] = None, 
	ignorehitpause: Optional[ConvertibleExpression] = None, 
	persistent: Optional[ConvertibleExpression] = None
) -> StateController:
    result = StateController()

    set_if_tuple(result, "value", value, SoundPairType)
    set_if(result, "volumescale", volumescale)
    set_if(result, "channel", channel)
    set_if(result, "lowpriority", lowpriority)
    set_if(result, "freqmul", freqmul)
    set_if(result, "loop", loop)
    set_if(result, "pan", pan)
    set_if(result, "abspan", abspan)

    return result

@controller(x = [FloatType, None], y = [FloatType, None])
def PosAdd(x: Optional[ConvertibleExpression] = None, y: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "x", x)
    set_if(result, "y", y)

    return result

@controller(value = [BoolType, None])
def PosFreeze(value: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "value", value)

    return result

@controller(x = [FloatType, None], y = [FloatType, None])
def PosSet(x: Optional[ConvertibleExpression] = None, y: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "x", x)
    set_if(result, "y", y)

    return result

@controller(value = [IntType])
def PowerAdd(value: ConvertibleExpression, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "value", value)

    return result

@controller(value = [IntType])
def PowerSet(value: ConvertibleExpression, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "value", value)

    return result

@controller(
    projid = [IntType, None],
    projint = [IntType, None],
    projhitint = [IntType, None],
    projremint = [IntType, None],
    projscale = [FloatPairType, None],
    projremove = [BoolType, None],
    projremovetime = [IntType, None],
    velocity = [FloatPairType, None],
    remvelocity = [FloatPairType, None],
    accel = [FloatPairType, None],
    velmul = [FloatPairType, None],
    projhits = [IntType, None],
    projmisstime = [IntType, None],
    projpriority = [IntType, None],
    projsprpriority = [IntType, None],
    projedgebound = [IntType, None],
    projstagebound = [IntType, None],
    projheightbound = [IntPairType, None],
    offset = [IntPairType, None],
    postype = [PosType, None],
    projshadow = [BoolType, None],
    supermovetime = [IntType, None],
    pausemovetime = [IntType, None],
    afterimage_time = [IntType, None],
    afterimage_length = [IntType, None],
    afterimage_palcolor = [IntType, None],
    afterimage_palinvertall = [BoolType, None],
    afterimage_palbright = [ColorType, None],
    afterimage_palcontrast = [ColorType, None],
    afterimage_palpostbright = [ColorType, None],
    afterimage_paladd = [ColorType, None],
    afterimage_palmul = [ColorMultType, None],
    afterimage_timegap = [IntType, None],
    afterimage_framegap = [IntType, None],
    afterimage_trans = [TransType, None]
)
def Projectile(
    projid: Optional[ConvertibleExpression] = None,
    projint: Optional[ConvertibleExpression] = None,
    projhitint: Optional[ConvertibleExpression] = None,
    projremint: Optional[ConvertibleExpression] = None,
    projscale: Optional[TupleExpression] = None,
    projremove: Optional[ConvertibleExpression] = None,
    projremovetime: Optional[ConvertibleExpression] = None,
    velocity: Optional[TupleExpression] = None,
    remvelocity: Optional[TupleExpression] = None,
    accel: Optional[TupleExpression] = None,
    velmul: Optional[TupleExpression] = None,
    projhits: Optional[ConvertibleExpression] = None,
    projmisstime: Optional[ConvertibleExpression] = None,
    projpriority: Optional[ConvertibleExpression] = None,
    projedgebound: Optional[ConvertibleExpression] = None,
    projstagebound: Optional[ConvertibleExpression] = None,
    projheightbound: Optional[TupleExpression] = None,
    offset: Optional[TupleExpression] = None,
    postype: Optional[ConvertibleExpression] = None,
    projshadow: Optional[ConvertibleExpression] = None,
    supermovetime: Optional[ConvertibleExpression] = None,
    pausemovetime: Optional[ConvertibleExpression] = None,
    afterimage_time: Optional[ConvertibleExpression] = None,
    afterimage_length: Optional[ConvertibleExpression] = None,
    afterimage_palcolor: Optional[ConvertibleExpression] = None,
    afterimage_palinvertall: Optional[ConvertibleExpression] = None,
    afterimage_palbright: Optional[TupleExpression] = None,
    afterimage_palcontrast: Optional[TupleExpression] = None,
    afterimage_palpostbright: Optional[TupleExpression] = None,
    afterimage_paladd: Optional[TupleExpression] = None,
    afterimage_palmul: Optional[TupleExpression] = None,
    afterimage_timegap: Optional[ConvertibleExpression] = None,
    afterimage_framegap: Optional[ConvertibleExpression] = None,
    afterimage_trans: Optional[ConvertibleExpression] = None, 
	ignorehitpause: Optional[ConvertibleExpression] = None, 
	persistent: Optional[ConvertibleExpression] = None
) -> StateController:
    result = StateController()

    set_if(result, "projid", projid)
    set_if(result, "projint", projint)
    set_if(result, "projhitint", projhitint)
    set_if(result, "projremint", projremint)
    set_if_tuple(result, "projscale", projscale, FloatPairType)
    set_if(result, "projremove", projremove)
    set_if(result, "projremovetime", projremovetime)
    set_if_tuple(result, "velocity", velocity, FloatPairType)
    set_if_tuple(result, "remvelocity", remvelocity, FloatPairType)
    set_if_tuple(result, "accel", accel, FloatPairType)
    set_if_tuple(result, "velmul", velmul, FloatPairType)
    set_if(result, "projhits", projhits)
    set_if(result, "projmisstime", projmisstime)
    set_if(result, "projpriority", projpriority)
    set_if(result, "projedgebound", projedgebound)
    set_if(result, "projstagebound", projstagebound)
    set_if_tuple(result, "projheightbound", projheightbound, IntPairType)
    set_if_tuple(result, "offset", offset, IntPairType)
    set_if(result, "postype", postype)
    set_if(result, "projshadow", projshadow)
    set_if(result, "supermovetime", supermovetime)
    set_if(result, "pausemovetime", pausemovetime)
    set_if(result, "afterimage.time", afterimage_time)
    set_if(result, "afterimage.length", afterimage_length)
    set_if(result, "afterimage.palcolor", afterimage_palcolor)
    set_if(result, "afterimage.palinvertall", afterimage_palinvertall)
    set_if_tuple(result, "afterimage.palbright", afterimage_palbright, ColorType)
    set_if_tuple(result, "afterimage.palcontrast", afterimage_palcontrast, ColorType)
    set_if_tuple(result, "afterimage.palpostbright", afterimage_palpostbright, ColorType)
    set_if_tuple(result, "afterimage.paladd", afterimage_paladd, ColorType)
    set_if_tuple(result, "afterimage.palmul", afterimage_palmul, ColorMultType)
    set_if(result, "afterimage.timegap", afterimage_timegap)
    set_if(result, "afterimage.framegap", afterimage_framegap)
    set_if(result, "afterimage.trans", afterimage_trans)

    return result

@controller(source = [IntPairType], dest = [IntPairType])
def RemapPal(source: TupleExpression, dest: TupleExpression, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if_tuple(result, "source", source, IntPairType)
    set_if_tuple(result, "dest", dest, IntPairType)

    return result

@controller(id = [IntType, None])
def RemoveExplod(id: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "id", id)

    return result

@controller(
    reversal_attr = [HitStringType],
    pausetime = [IntPairType, None],
    sparkno = [IntType, None],
    hitsound = [IntPairType, None],
    p1stateno = [IntType, None],
    p2stateno = [IntType, None],
    p1sprpriority = [IntType, None],
    p2sprpriority = [IntType, None],
    sparkxy = [IntPairType, None]
)
def ReversalDef(
    reversal_attr: TupleExpression, 
    pausetime: Optional[TupleExpression] = None, 
    sparkno: Optional[ConvertibleExpression] = None, 
    hitsound: Optional[TupleExpression] = None, 
    p1stateno: Optional[Union[Expression, str, int, Callable[..., None]]] = None, 
    p2stateno: Optional[Union[Expression, str, int, Callable[..., None]]] = None, 
    p1sprpriority: Optional[ConvertibleExpression] = None, 
    p2sprpriority: Optional[ConvertibleExpression] = None, 
    sparkxy: Optional[TupleExpression] = None, 
	ignorehitpause: Optional[ConvertibleExpression] = None, 
	persistent: Optional[ConvertibleExpression] = None
) -> StateController:
    result = StateController()

    set_if_tuple(result, "reversal.attr", reversal_attr, HitStringType)
    set_if_tuple(result, "pausetime", pausetime, IntPairType)
    set_if(result, "sparkno", sparkno)
    set_if_tuple(result, "hitsound", hitsound, IntPairType)
    set_stateno(result, "p1stateno", p1stateno)
    set_stateno(result, "p2stateno", p2stateno)
    set_if(result, "p1sprpriority", p1sprpriority)
    set_if(result, "p2sprpriority", p2sprpriority)
    set_if_tuple(result, "sparkxy", sparkxy, IntPairType)

    return result

@controller(value = [BoolType, None], movecamera = [BoolPairType, None])
def ScreenBound(value: Optional[ConvertibleExpression] = None, movecamera: Optional[TupleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "value", value)
    set_if_tuple(result, "movecamera", movecamera, BoolPairType)

    return result

@controller(value = [StateNoType, StringType, IntType], ctrl = [BoolType, None], anim = [IntType, None])
def SelfState(value: ConvertibleExpression, ctrl: Optional[ConvertibleExpression] = None, anim: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "value", value)
    set_if(result, "ctrl", ctrl)
    set_if(result, "anim", anim)

    return result

@controller(value = [IntType])
def SprPriority(value: ConvertibleExpression, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "value", value)

    return result

@controller(statetype = [StateType, None], movetype = [MoveType, None], physics = [PhysicsType, None])
def StateTypeSet(statetype: Optional[ConvertibleExpression] = None, movetype: Optional[ConvertibleExpression] = None, physics: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "statetype", statetype)
    set_if(result, "movetype", movetype)
    set_if(result, "physics", physics)

    return result

@controller(channel = [IntType], pan = [IntType], abspan = [IntType])
def SndPan(channel: ConvertibleExpression, pan: ConvertibleExpression, abspan: ConvertibleExpression, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "channel", channel)
    set_if(result, "pan", pan)
    set_if(result, "abspan", abspan)

    return result

@controller(channel = [IntType])
def StopSnd(channel: ConvertibleExpression, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "channel", channel)

    return result

@controller(
    time = [IntType, None],
    anim = [IntType, None],
    sound = [SoundPairType, None],
    pos = [FloatPairType, None],
    darken = [BoolType, None],
    p2defmul = [FloatType, None],
    poweradd = [IntType, None],
    unhittable = [BoolType, None]
)
def SuperPause(
    time: Optional[ConvertibleExpression] = None, 
    anim: Optional[ConvertibleExpression] = None, 
    sound: Optional[TupleExpression] = None,
    pos: Optional[TupleExpression] = None, 
    darken: Optional[ConvertibleExpression] = None, 
    p2defmul: Optional[ConvertibleExpression] = None, 
    poweradd: Optional[ConvertibleExpression] = None, 
    unhittable: Optional[ConvertibleExpression] = None, 
	ignorehitpause: Optional[ConvertibleExpression] = None, 
	persistent: Optional[ConvertibleExpression] = None
) -> StateController:
    result = StateController()

    set_if(result, "time", time)
    set_if(result, "anim", anim)
    set_if_tuple(result, "sound", sound, SoundPairType)
    set_if_tuple(result, "pos", pos, FloatPairType)
    set_if(result, "darken", darken)
    set_if(result, "p2defmul", p2defmul)
    set_if(result, "poweradd", poweradd)
    set_if(result, "unhittable", unhittable)

    return result

@controller(time = [IntType, None], id = [IntType, None], pos = [FloatPairType, None])
def TargetBind(time: Optional[ConvertibleExpression] = None, id: Optional[ConvertibleExpression] = None, pos: Optional[TupleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "time", time)
    set_if(result, "id", id)
    set_if_tuple(result, "pos", pos, FloatPairType)

    return result

@controller(excludeid = [IntType, None], keepone = [BoolType, None])
def TargetDrop(excludeid: Optional[ConvertibleExpression] = None, keepone: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "excludeid", excludeid)
    set_if(result, "keepone", keepone)

    return result

@controller(value = [IntType], id = [IntType, None])
def TargetFacing(value: ConvertibleExpression, id: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "value", value)
    set_if(result, "id", id)

    return result

@controller(value = [IntType], id = [IntType, None], kill = [BoolType, None], absolute = [BoolType, None])
def TargetLifeAdd(value: ConvertibleExpression, id: Optional[ConvertibleExpression] = None, kill: Optional[ConvertibleExpression] = None, absolute: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "value", value)
    set_if(result, "id", id)
    set_if(result, "kill", kill)
    set_if(result, "absolute", absolute)

    return result

@controller(value = [IntType], id = [IntType, None])
def TargetPowerAdd(value: ConvertibleExpression, id: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "value", value)
    set_if(result, "id", id)

    return result

@controller(value = [StateNoType, StringType, IntType], id = [IntType, None])
def TargetState(value: Union[Expression, str, int, Callable[..., None]], id: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_stateno(result, "value", value)
    set_if(result, "id", id)

    return result

@controller(x = [FloatType, None], y = [FloatType, None], id = [IntType, None])
def TargetVelAdd(x: Optional[ConvertibleExpression] = None, y: Optional[ConvertibleExpression] = None, id: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "x", x)
    set_if(result, "y", y)
    set_if(result, "id", id)

    return result

@controller(x = [FloatType, None], y = [FloatType, None], id = [IntType, None])
def TargetVelSet(x: Optional[ConvertibleExpression] = None, y: Optional[ConvertibleExpression] = None, id: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "x", x)
    set_if(result, "y", y)
    set_if(result, "id", id)

    return result

@controller(trans = [TransType], alpha = [IntPairType, None])
def Trans(trans: ConvertibleExpression, alpha: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "trans", trans)
    set_if(result, "alpha", alpha)

    return result

@controller()
def Turn(ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()
    return result

@controller(var = [IntType, FloatType, None], value = [IntType, FloatType, None])
def VarAdd(var: Optional[Expression] = None, value: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    if var != None:
        set_if(result, var.exprn, value)

    return result

@controller(var = [IntType, FloatType, None], value = [IntType, FloatType, None])
def VarSet(var: Optional[Expression] = None, value: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    if var != None:
        set_if(result, var.exprn, value)

    return result

@controller(v = [IntType], range = [IntPairType, None])
def VarRandom(v: ConvertibleExpression, range: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "v", v)
    set_if(result, "range", range)

    return result

@controller(value = [IntType], fvalue = [FloatType], first = [IntType, None], last = [IntType, None])
def VarRangeSet(value: ConvertibleExpression, fvalue: ConvertibleExpression, first: Optional[ConvertibleExpression] = None, last: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "value", value)
    set_if(result, "fvalue", fvalue)
    set_if(result, "first", first)
    set_if(result, "last", last)

    return result

@controller(x = [FloatType, None], y = [FloatType, None])
def VelAdd(x: Optional[ConvertibleExpression] = None, y: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "x", x)
    set_if(result, "y", y)

    return result

@controller(x = [FloatType, None], y = [FloatType, None])
def VelMul(x: Optional[ConvertibleExpression] = None, y: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "x", x)
    set_if(result, "y", y)

    return result

@controller(x = [FloatType, None], y = [FloatType, None])
def VelSet(x: Optional[ConvertibleExpression] = None, y: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "x", x)
    set_if(result, "y", y)

    return result

@controller(value = [IntType, None])
def VictoryQuote(value: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "value", value)

    return result

@controller(edge = [IntPairType, None], player = [IntPairType, None], value = [IntPairType, None])
def Width(edge: Optional[TupleExpression] = None, player: Optional[TupleExpression] = None, value: Optional[TupleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if_tuple(result, "edge", edge, IntPairType)
    set_if_tuple(result, "player", player, IntPairType)
    set_if_tuple(result, "value", value, IntPairType)

    return result

__all__ = [
    "AfterImage", "AfterImageTime", "AngleAdd", "AngleDraw", "AngleMul", "AngleSet", 
    "AssertSpecial", "AttackDist", "AttackMulSet", "BindToParent", "BindToRoot", "BindToTarget", "ChangeAnim", 
    "ChangeAnim2", "ChangeState", "ClearClipboard", "CtrlSet", "DefenceMulSet", "DestroySelf", 
    "EnvColor", "EnvShake", "Explod", "ExplodBindTime", "ForceFeedback", "FallEnvShake", "GameMakeAnim", "Gravity", 
    "Helper", "HitAdd", "HitBy", "HitDef", "HitFallDamage", "HitFallSet", "HitFallVel", "HitOverride", "HitVelSet", 
    "LifeAdd", "LifeSet", "MakeDust", "ModifyExplod", "MoveHitReset", "NotHitBy", "Null", "Offset", "PalFX", 
    "ParentVarAdd", "ParentVarSet", "Pause", "PlayerPush", "PlaySnd", "PosAdd", "PosFreeze", "PosSet", "PowerAdd", 
    "PowerSet", "Projectile", "RemapPal", "RemoveExplod", "ReversalDef", "ScreenBound", "SelfState", "SprPriority", 
    "StateTypeSet", "SndPan", "SuperPause", "TargetBind", "TargetDrop", "TargetFacing", "TargetLifeAdd", "TargetPowerAdd", 
    "TargetState", "TargetVelAdd", "TargetVelSet", "Trans", "Turn", "VarAdd", "VarSet", "VarRandom", "VarRangeSet", 
    "VelAdd", "VelMul", "VelSet", "VictoryQuote", "Width"
]