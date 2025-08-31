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
    """
    Internal method used to set a property on a controller if the input value is not None.

    The input value is converted to an Expression before being assigned.
    """
    if val != None:
        if not isinstance(val, Expression):
            val = convert(val)
        ctrl.params[name] = val

def set_if_tuple(ctrl: StateController, name: str, val: Optional[TupleExpression], type: TypeSpecifier):
    """
    Internal method used to set a property on a controller if the input value is not None.

    The input value is a tuple of ConvertibleExpression.

    The input value is converted to an Expression before being assigned.
    """
    if val != None:
        converted = []
        for v in val:
            if isinstance(v, Expression):
                converted.append(v)
            else:
                converted.append(convert(v))
        exprn_string = ", ".join([t.exprn for t in converted])
        ctrl.params[name] = Expression(exprn_string, type)

def set_stateno(ctrl: StateController, name: str, val: Optional[Union[Expression, Callable[..., None | StateController], str, int]]):
    """
    Internal method used to set a property on a controller if the input value is not None.

    The input value must be either an Expression, or some value which can represent a state controller (a function, a partial, a string, ...)
    """
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
    trans = [TransTypeT, None]
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
    """
<h2>AfterImage</h2>
<p>Enables player afterimage effects. The character's frames are stored in a history buffer, and are displayed after a delay as afterimages.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>time = <em>duration</em> (int)</dt>
<dd>Specifies the number of ticks that the afterimages should be
displayed for. Set to -1 to display indefinitely. Defaults to 1.</dd>
<dt>length = <em>no_of_frames</em> (int)</dt>
<dd>Sets the capacity of the frame history buffer. The history will
hold up to <em>no_of_frames</em> of the character's most recently saved
frames. Assuming constant values for timegap and framegap,
increasing the length can increase the number and "age" (for lack
of a better term) of afterimages displayed at one time. The
maximum length is 60, and the default is 20.</dd>
<dt>palcolor = <em>col</em> (int)</dt>
<dd>See below.</dd>
<dt>palinvertall = <em>invertall</em> (bool)</dt>
<dd>See below.</dd>
<dt>palbright = <em>add_r</em>, <em>add_g</em>, <em>add_b</em> (int)</dt>
<dd>See below.</dd>
<dt>palcontrast = <em>mul_r</em>, <em>mul_g</em>, <em>mul_b</em> (int)</dt>
<dd>See below.</dd>
<dt>palpostbright = <em>add2_r</em>, <em>add2_g</em>, <em>add2_b</em> (int)</dt>
<dd><p>These parameters determine palette effects to be applied to all afterimages. First the color level is adjusted according to the palcolor value, then if invertall is non-zero the colors are inverted. Afterwards, the palbright components are added to the corresponding component of the player's palette, then each component is multiplied by the corresponding palcontrast component divided by 256, then the palpostbright components are added to the result. The value of palcolor ranges from 0 (greyscale) to 256 (normal color). For instance, if the red component of the character's palette is denoted <em>pal_r</em>, then the red component of the afterimage palette is given by (<em>pal_r</em> + <em>add_r</em>) * <em>mul_r</em> / 256 + <em>add2_r</em>, assuming palcolor and palinvert are left at their default values. Valid values are 0-256 for palcolor, 0-255 for palbright and palpostbright components, and any non-negative integer for palcontrast components. The defaults are:</p>
<pre>palcolor = 256
palinvertall = 0
palbright = 30,30,30
palcontrast = 120,120,220
palpostbright = 0,0,0
</pre>
</dd>
<dt>paladd = <em>add_r</em>, <em>add_g</em>, <em>add_b</em> (int)</dt>
<dd>See below.</dd>
<dt>palmul = <em>mul_r</em>, <em>mul_g</em>, <em>mul_b</em> (float)</dt>
<dd><p>These parameters specify palette effects that are applied repeatedly to successive frames in the afterimage. In one application of these palette effects, first the paladd components are added to the afterimage palette, then the components are multiplied by the palmul multipliers. These effects are applied zero times to the most recent afterimage frame, once to the  second-newest afterimage frame, twice in succession to the third-newest afterimage frame, etc. Valid values are 0-255 for the paladd components, and any non-negative float value for the palmul multipliers. The defaults are:</p>
<pre>paladd = 10,10,25
palmul = .65,.65,.75
</pre>
</dd>
<dt>timegap = <em>value</em> (int)</dt>
<dd>This parameter controls how many frames to skip between saving
player frames to the history buffer for afterimage display. The
default is 1 (skip no frames). To save every third frame (for
example), you would use timegap = 3.</dd>
<dt>framegap = <em>value</em> (int)</dt>
<dd>Every <em>value</em>'th frame in the history buffer will be displayed as an
afterimage. For instance, if framegap = 4 (the default), then the
first, fifth, ninth, ... frames of the history buffer will be
displayed as afterimages.</dd>
<dt>trans = <em>type</em> (string)</dt>
<dd>Specifies the transparency type for the afterimages. Valid values for <em>type</em>
are "none" for an opaque afterimage, "add", "add1", and "sub".
Defaults to "none".</dd>
</dl>
</dd>
</dl>
    """
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
    """
<h2>AfterImageTime</h2>
<p>Changes the duration of the player's afterimage effects, if currently enabled. If no afterimage effects are being displayed, this controller does nothing.
Known bugs: If the timegap parameter in the originating AfterImage controller is not set at 1, using this AfterImageTime will cause the frame positions to be reset.</p>
<dl>
<dt>Required parameters:</dt>
<dd><dl>
<dt>time = <em>new_duration</em> (int)</dt>
<dd>Sets the new number of ticks that the afterimages will be
displayed before being removed.</dd>
</dl>
</dd>
<dt>Alternate syntax:</dt>
<dd>value = <em>new_duration</em> (int)</dd>
<dt>Optional parameters:</dt>
<dd>none</dd>
<dt>Example:</dt>
<dd>none</dd>
</dl>
    """
    result = StateController()

    set_if(result, "time", time)

    return result

@controller(
    time = [IntType, None],
    add = [ColorType, None],
    mul = [ColorType, None],
    sinadd = [PeriodicColorType, None],
    invertall = [BoolType, None],
    color = [IntType, None]
)
def AllPalFX(
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

@controller(value = [FloatType])
def AngleAdd(value: ConvertibleExpression, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>AngleAdd</h2>
<p>Adds to the drawing rotation angle used by AngleDraw.</p>
<dl>
<dt>Required arguments:</dt>
<dd><dl>
<dt>value = <em>add_angle</em> (float)</dt>
<dd><em>add_angle</em> should be given in degrees.</dd>
</dl>
</dd>
<dt>Optional arguments:</dt>
<dd>none</dd>
</dl>
    """
    result = StateController()

    set_if(result, "value", value)

    return result

@controller(value = [FloatType, None], scale = [FloatPairType, None])
def AngleDraw(value: Optional[ConvertibleExpression] = None, scale: Optional[TupleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>AngleDraw</h2>
<p>Draws the player (for 1 frame) rotated about his axis by the angle set by the AngleSet controller. When facing right, a positive angle means a counterclockwise rotation.</p>
<dl>
<dt>Required arguments:</dt>
<dd>none</dd>
<dt>Optional arguments:</dt>
<dd><dl>
<dt>value = <em>angle</em> (float)</dt>
<dd>Sets the drawing angle in degrees.</dd>
</dl>
</dd>
<dt>scale = <em>xscale</em>, <em>yscale</em> (float, float)</dt>
<dd>Scales the player sprite.</dd>
<dt>Notes:</dt>
<dd>Rotation/scaling does not affect the player’s collision boxes.</dd>
</dl>
    """
    result = StateController()

    set_if(result, "value", value)
    set_if_tuple(result, "scale", scale, FloatPairType)

    return result

@controller(value = [FloatType])
def AngleMul(value: ConvertibleExpression, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>AngleMul</h2>
<p>Multiplies the drawing rotation angle used by AngleDraw by the specified factor.</p>
<dl>
<dt>Required arguments:</dt>
<dd><dl>
<dt>value = <em>angle_multiplier</em> (float)</dt>
<dd>Multiplies the drawing angle by <em>angle_multiplier</em>.</dd>
</dl>
</dd>
<dt>Optional arguments:</dt>
<dd>none</dd>
</dl>
    """
    result = StateController()

    set_if(result, "value", value)

    return result

@controller(value = [FloatType])
def AngleSet(value: ConvertibleExpression, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>AngleSet</h2>
<p>Sets the drawing rotation angle used by AngleDraw. The angle is initialized at 0.</p>
<dl>
<dt>Required arguments:</dt>
<dd><dl>
<dt>value = <em>angle</em> (float)</dt>
<dd>the value of <em>angle</em> is interpreted to be in degrees.</dd>
</dl>
</dd>
<dt>Optional arguments:</dt>
<dd>none</dd>
</dl>
    """
    result = StateController()

    set_if(result, "value", value)

    return result

@controller(text = [StringType], params = [AnyType, None])
def AppendToClipboard(text: ConvertibleExpression, params: Optional[TupleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "text", text)
    set_if_tuple(result, "params", params, AnyType)

    return result

@controller(flag = [AssertTypeT], flag2 = [AssertTypeT, None], flag3 = [AssertTypeT, None])
def AssertSpecial(flag: ConvertibleExpression, flag2: Optional[ConvertibleExpression] = None, flag3: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>AssertSpecial</h2>
<p>This controller allows you to assert up to three special flags simultaneously. MUGEN will automatically "deassert" each flag at every game tick, so you must assert a flag for each tick that you want it to be active.</p>
<dl>
<dt>Required parameters:</dt>
<dd><dl>
<dt>flag = <em>flag_name</em></dt>
<dd><em>flag_name</em> is a string specifying the flag to assert.</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>flag2 = <em>flag2_name</em></dt>
<dd>An optional flag to assert.</dd>
<dt>flag3 = <em>flag3_name</em></dt>
<dd>Another optional flag to assert.</dd>
</dl>
</dd>
<dt>Details:</dt>
<dd><dl>
<dt>The flag name can be one of the following:</dt>
<dd><dl>
<dt>intro</dt>
<dd>Tells MUGEN that the character is currently performing his intro
pose. Must be asserted on every tick while the intro pose is
being performed.</dd>
<dt>invisible</dt>
<dd>Turns the character invisible while asserted. Does not affect
display of afterimages.</dd>
<dt>roundnotover</dt>
<dd>Tells MUGEN that the character is currently performing his win
pose. Should be asserted on every tick while the win pose is being
performed.</dd>
<dt>nobardisplay</dt>
<dd>Disables display of life, super bars, etc. while asserted.</dd>
<dt>noBG</dt>
<dd>Turns off the background. The screen is cleared to black.</dd>
<dt>noFG</dt>
<dd>Disables display of layer 1 of the stage (the foreground).</dd>
<dt>nostandguard</dt>
<dd>While asserted, disables standing guard for the character.</dd>
<dt>nocrouchguard</dt>
<dd>While asserted, disables crouching guard for the character.</dd>
<dt>noairguard</dt>
<dd>While asserted, disables air guard for the character.</dd>
<dt>noautoturn</dt>
<dd>While asserted, keeps the character from automatically turning
to face the opponent.</dd>
<dt>nojugglecheck</dt>
<dd>While asserted, disables juggle checking. P2 can be juggled
regardless of juggle points.</dd>
<dt>nokosnd</dt>
<dd>Suppresses playback of sound 11, 0 (the KO sound) for players
who are knocked out. For players whose KO sound echoes, nokosnd
must be asserted for 50 or more ticks after the player is KOed
in order to suppress all echoes.</dd>
<dt>nokoslow</dt>
<dd>While asserted, keeps MUGEN from showing the end of the round in
slow motion.</dd>
<dt>noshadow</dt>
<dd>While asserted, disables display of this player's shadows.</dd>
<dt>globalnoshadow</dt>
<dd>Disables display of all player, helper and explod shadows.</dd>
<dt>nomusic</dt>
<dd>While asserted, pauses playback of background music.</dd>
<dt>nowalk</dt>
<dd>While asserted, the player cannot enter his walk states, even if
he has control. Use to prevent run states from canceling into
walking.</dd>
<dt>timerfreeze</dt>
<dd>While asserted, keeps the round timer from counting down. Useful
to keep the round from timing over in the middle of a splash
screen.</dd>
<dt>unguardable</dt>
<dd>While asserted, all the asserting player's HitDefs become
unblockable, i.e., their guardflags are ignored.</dd>
</dl>
</dd>
</dl>
</dd>
</dl>
    """
    result = StateController()

    set_if(result, "flag", flag)
    set_if(result, "flag2", flag2)
    set_if(result, "flag3", flag3)

    return result

@controller(value = [IntType])
def AttackDist(value: ConvertibleExpression, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>AttackDist</h2>
<p>Changes the value of the guard.dist parameter for the player's current HitDef. The guard.dist is the x-distance from P1 in which P2 will go
into a guard state if P2 is holding the direction away from P1.
The effect of guard.dist only takes effect when P1 has movetype = A.</p>
<dl>
<dt>Required parameters:</dt>
<dd><dl>
<dt>value = <em>guard_dist</em> (int)</dt>
<dd>New guard distance, in pixels.</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd>none</dd>
</dl>
    """
    result = StateController()

    set_if(result, "value", value)

    return result

@controller(value = [FloatType])
def AttackMulSet(value: ConvertibleExpression, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>AttackMulSet</h2>
<p>Sets the player's attack multiplier. All damage the player gives is scaled by this amount.</p>
<dl>
<dt>Required parameters:</dt>
<dd><dl>
<dt>value = <em>attack_mul</em> (float)</dt>
<dd>Specifies the desired multiplier. For instance, an <em>attack_mul</em> of 2
deals double damage.</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd>none</dd>
</dl>
    """
    result = StateController()

    set_if(result, "value", value)

    return result

@controller(time = [IntType, None], facing = [IntType, None], pos = [FloatPairType, None])
def BindToParent(time: Optional[ConvertibleExpression] = None, facing: Optional[ConvertibleExpression] = None, pos: Optional[TupleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>BindToParent</h2>
<p>If the player is a helper, binds the player to a specified position relative to its parent. If the player is not a helper, this controller does nothing.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>time = <em>bind_time</em> (int)</dt>
<dd>Specify number of ticks that this binding should be effective.
Defaults to 1.</dd>
<dt>facing = <em>facing_flag</em> (int)</dt>
<dd>If <em>facing_flag</em> is -1, makes the player always face the opposite
direction from its parent during the binding time. If <em>facing_flag *
is 1, makes the player always face the same direction as its
parent during the binding time. If *facing_flag</em> is 0, the player
will not turn regardless of what its parent does. Defaults to 0.</dd>
<dt>pos = <em>pos_x</em> (float), <em>pos_y</em> (float)</dt>
<dd><em>pos_x</em> and <em>pos_y</em> specify the offsets (from the parent's axis) to
bind to. Defaults to 0,0.</dd>
</dl>
</dd>
<dt>Notes:</dt>
<dd>If the player's parent is destroyed (for example, if it is a
helper, and executes DestroySelf), then the effect of
BindToParent is terminated.</dd>
</dl>
    """
    result = StateController()

    set_if(result, "time", time)
    set_if(result, "facing", facing)
    set_if_tuple(result, "pos", pos, FloatPairType)

    return result

@controller(time = [IntType, None], facing = [IntType, None], pos = [FloatPairType, None])
def BindToRoot(time: Optional[ConvertibleExpression] = None, facing: Optional[ConvertibleExpression] = None, pos: Optional[TupleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>BindToRoot</h2>
<p>If the player is a helper, binds the player to a specified position relative to its root. If the player is not a helper, this controller does nothing.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>time = <em>bind_time</em> (int)</dt>
<dd>Specify number of ticks that this binding should be effective.
Defaults to 1.</dd>
<dt>facing = <em>facing_flag</em> (int)</dt>
<dd>If <em>facing_flag</em> is -1, makes the player always face the opposite
direction from its root during the binding time. If <em>facing_flag</em>
is 1, makes the player always face the same direction as its
root during the binding time. If <em>facing_flag</em> is 0, the player
will not turn regardless of what its root does. Defaults to 0.</dd>
<dt>pos = <em>pos_x</em> (float), <em>pos_y</em> (float)</dt>
<dd><em>pos_x</em> and <em>pos_y</em> specify the offsets (from the root's axis) to
bind to. Defaults to 0,0.</dd>
</dl>
</dd>
<dt>Notes:</dt>
<dd>If the player's root is disabled for any reason, then the effect of
BindToRoot is terminated.</dd>
</dl>
    """
    result = StateController()

    set_if(result, "time", time)
    set_if(result, "facing", facing)
    set_if_tuple(result, "pos", pos, FloatPairType)

    return result

@controller(time = [IntType, None], id = [IntType, None], pos = [FloatPosType, None])
def BindToTarget(time: Optional[ConvertibleExpression] = None, id: Optional[ConvertibleExpression] = None, pos: Optional[TupleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>BindToTarget</h2>
<p>Binds the player to a specified position relative to the specified target.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>time = <em>bind_time</em> (int)</dt>
<dd>Specify number of ticks that this binding should be effective.
Defaults to 1.</dd>
<dt>ID = <em>bind_id</em> (int)</dt>
<dd>Specifies ID number of the target to bind to. Defaults to -1 (pick
any target).</dd>
<dt>pos = <em>pos_x</em> (float), <em>pos_y</em> (float), <em>postype</em> (string)</dt>
<dd><em>pos_x</em> and <em>pos_y</em> specify the offsets (from the bind point) to bind
to. The bind point defaults to the target's axis.
If <em>postype</em> is "Foot", then the bind point is the target's axis.
If <em>postype</em> is "Mid", then the bind point is the target's
midsection.
If <em>postype</em> is "Head", then the bind point is the target's head.
In the latter two cases, the bind point is determined from the
values of the head.pos and mid.pos parameters in the target's CNS
file. The bind point is not guaranteed to match up with the
target's head or midsection.</dd>
</dl>
</dd>
</dl>
    """
    result = StateController()

    set_if(result, "time", time)
    set_if(result, "id", id)
    set_if_tuple(result, "pos", pos, FloatPairType)

    return result

@controller(
    time = [IntType, None],
    add = [ColorType, None],
    mul = [ColorType, None],
    sinadd = [PeriodicColorType, None],
    invertall = [BoolType, None],
    color = [IntType, None]
)
def BGPalFX(
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

@controller(value = [IntType], elem = [IntType, None])
def ChangeAnim(value: ConvertibleExpression, elem: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>ChangeAnim</h2>
<p>Changes the action number of the player's animation.</p>
<dl>
<dt>Required parameters:</dt>
<dd><dl>
<dt>value = <em>anim_no</em> (int)</dt>
<dd><em>anim_no</em> is the action number to change to.</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>elem = <em>elem_no</em> (int)</dt>
<dd><em>elem_no</em> is the element number within the specified action
to start from.</dd>
</dl>
</dd>
</dl>
    """
    result = StateController()

    set_if(result, "value", value)
    set_if(result, "elem", elem)

    return result

@controller(value = [IntType], elem = [IntType, None])
def ChangeAnim2(value: ConvertibleExpression, elem: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>ChangeAnim2</h2>
<p>Like ChangeAnim, except this controller should be used if you have placed P2 in a custom state via a hit and wish to change P2's animation to one specified in P1's air file. For example, when making throws, use this to change P2 to a being-thrown animation.</p>
    """
    result = StateController()

    set_if(result, "value", value)
    set_if(result, "elem", elem)

    return result

@controller(value = [StateNoType, IntType, StringType], ctrl = [None, BoolType], anim = [None, IntType])
def ChangeState(value: Union[Expression, str, int, Callable[..., None | StateController]], ctrl: Optional[ConvertibleExpression] = None, anim: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>ChangeState</h2>
<p>Changes the state number of the player.</p>
<dl>
<dt>Required parameters:</dt>
<dd><dl>
<dt>value = <em>state_no</em> (int)</dt>
<dd><em>state_no</em> is the number of the state to change to.</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>ctrl = <em>ctrl_flag</em> (int)</dt>
<dd><em>ctrl_flag</em> is the value to set the player's control
flag to. 0 for no control, nonzero for control.</dd>
<dt>anim = <em>anim_no</em> (int)</dt>
<dd>This is the action number to switch to. If omitted,
the player's animation will remain unchanged.</dd>
</dl>
</dd>
</dl>
    """
    result = StateController()

    set_stateno(result, "value", value)

    set_if(result, "ctrl", ctrl)
    set_if(result, "anim", anim)

    return result

@controller()
def ClearClipboard(ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>ClearClipboard</h2>
<p>Erases any text currently on the player's clipboard.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd>none</dd>
</dl>
    """
    result = StateController()
    return result

@controller(ctrl = [BoolType, None], value = [BoolType, None])
def CtrlSet(ctrl: Optional[ConvertibleExpression] = None, value: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>CtrlSet</h2>
<p>Sets the player's control flag.</p>
<dl>
<dt>Required parameters:</dt>
<dd><dl>
<dt>value = <em>ctrl_flag</em> (int)</dt>
<dd>Set to nonzero to have control, or 0 to disable control.</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd>none</dd>
</dl>
    """
    result = StateController()

    set_if(result, "ctrl", ctrl)
    set_if(result, "value", value)

    return result

@controller(value = [FloatType])
def DefenceMulSet(value: ConvertibleExpression, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>DefenceMulSet</h2>
<p>Sets the player's defense multiplier. All damage the player takes is scaled by this amount.</p>
<dl>
<dt>Required parameters:</dt>
<dd><dl>
<dt>value = <em>defense_mul</em> (float)</dt>
<dd>Specifies the defense multiplier.</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd>none</dd>
<dt>Notes:</dt>
<dd>The LifeAdd controller is not affected by the player's defense multiplier.</dd>
</dl>
    """
    result = StateController()

    set_if(result, "value", value)

    return result

@controller()
def DestroySelf(ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>DestroySelf</h2>
<p>If called by a helper-type character, DestroySelf causes that character to be removed from the field of play. DestroySelf is not valid for non-helper characters.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>recursive = <em>recursive_flag</em> (int)</dt>
<dd>If 1, all helper descendents of this helper will also be destroyed.
Defaults to 0.</dd>
<dt>removeexplods = <em>remove_explods</em> (int)</dt>
<dd>If 1, all explods belonging to the helper will also be removed.
If <em>recursive_flag</em> is 1, explods belonging to descendents of the helper
will also be removed.
Defaults to 0.</dd>
</dl>
</dd>
<dt>Notes:</dt>
<dd><p>Any players or explods bound to the helper will be forcefully unbound when DestroySelf
is executed.</p>
<p class="last">Any unremoved explods belonging to a destroyed helper will become orphaned.</p>
</dd>
</dl>
    """
    result = StateController()
    return result

@controller(text = [StringType], params = [AnyType, None])
def DisplayToClipboard(text: ConvertibleExpression, params: Optional[TupleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    result = StateController()

    set_if(result, "text", text)
    set_if_tuple(result, "params", params, AnyType)

    return result

@controller(value = [ColorType, None], time = [IntType, None], under = [BoolType, None])
def EnvColor(value: Optional[TupleExpression] = None, time: Optional[ConvertibleExpression] = None, under: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>EnvColor</h2>
<p>Turns the whole screen a solid color, excepting foreground-layer animations like hit sparks and "ontop" explods. Foreground layers of the stage will not be visible.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>value = <em>col_r</em>, <em>col_g</em>, <em>col_b</em> (int)</dt>
<dd>Specifies the R, G, and B components of the color to set the
screen to. Each component should be an integer between 0 and 255.
The larger a component, the more of that color will appear in the
environment color. The default is 255,255,255 (pure white).</dd>
<dt>time = <em>effective_time</em> (int)</dt>
<dd>Specifies how many ticks the environment color should be
displayed. Defaults to 1 tick. Set to -1 to have the EnvColor
persist indefinitely.</dd>
<dt>under = <em>under_flag</em> (int)</dt>
<dd>Set <em>under_flag</em> to 1 to have the environment color drawn under
characters and projectiles. In other words, characters and
projectiles will be visible on top of the colored backdrop.
Defaults to 0.</dd>
</dl>
</dd>
</dl>
    """
    result = StateController()

    set_if_tuple(result, "value", value, ColorType)
    set_if(result, "time", time)
    set_if(result, "under", under)

    return result

@controller(time = [IntType], freq = [FloatType, None], ampl = [IntType, None], phase = [FloatType, None])
def EnvShake(time: ConvertibleExpression, freq: Optional[ConvertibleExpression] = None, ampl: Optional[ConvertibleExpression] = None, phase: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>EnvShake</h2>
<p>Causes the screen to shake vertically.</p>
<dl>
<dt>Required parameters:</dt>
<dd><dl>
<dt>time = <em>shake_time</em> (int)</dt>
<dd>Specifies the number of ticks to shake the screen for.</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>freq = <em>shake_speed</em> (float)</dt>
<dd><em>shake_speed</em> is a float between 0 (slow shake) to 180 (fast
shake). Defaults to 60.</dd>
<dt>ampl = <em>shake_amplitude</em> (int)</dt>
<dd>The larger the amplitude, the farther the screen shakes up and
down. A negative amplitude means that the screen will shake down
first. Defaults to -4 in 240p, -8 in 480p, -16 in 720p.</dd>
<dt>phase = <em>phase_offset</em> (float)</dt>
<dd>Specifies the phase offset for the shaking. The default is 0,
unless the frequency multiplier is 90 or greater. In this case,
the default phase offset is 90.</dd>
</dl>
</dd>
</dl>
    """
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
    postype = [PosTypeT, None],
    space = [SpaceTypeT, None],
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
    trans = [TransTypeT, None],
    angle = [IntType, None],
    alpha = [IntPairType, None]
)
def Explod(
    anim: ConvertibleExpression, 
    id: Optional[ConvertibleExpression] = None, 
    pos: Optional[TupleExpression] = None, 
    postype: Optional[ConvertibleExpression] = None,
    space: Optional[ConvertibleExpression] = None,
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
    angle: Optional[ConvertibleExpression] = None,
    alpha: Optional[TupleExpression] = None,
	ignorehitpause: Optional[ConvertibleExpression] = None, 
	persistent: Optional[ConvertibleExpression] = None
) -> StateController:
    """
<h2>Explod</h2>
<p>The Explod controller is a flexible tool for displaying animations such as sparks, dust and other visual effects. Its functionality includes that of GameMakeAnim, which is now deprecated.</p>
<dl>
<dt>Required parameters:</dt>
<dd><dl>
<dt>anim = <em>[F]anim_no</em> (int)</dt>
<dd><em>anim_no</em> specifies the number of the animation to play back. The
'F' prefix is optional: if included, then the animation is played
back from fightfx.air.</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>ID = <em>id_no</em> (int)</dt>
<dd><em>id_no</em> specifies an ID number for this explod. Used to identify particular explods in
triggers and controllers that affect explods.</dd>
<dt>space = <em>space</em> (string)</dt>
<dd><p>Specifies the coordinate space in which the explod is to be created.
Valid values for <em>space</em> are:</p>
<dl class="last docutils">
<dt>screen</dt>
<dd>This coordinate space maps to the screen.  The upper-left corner is
0,0 and the lower-right corner is ScreenWidth,ScreenHeight (refer to the
triggers with these names).  Explods created in screen space are not
affected by camera movement or zoom.</dd>
<dt>stage</dt>
<dd>This coordinate space maps to the stage space in which players reside.
0,0 is the center of the stage at ground level.
Explods created in screen space are affected by camera movement and zoom.
This is the default.</dd>
</dl>
</dd>
<dt>pos = <em>off_x</em>, <em>off_y</em> (float, float)</dt>
<dd>If the explod is not bound, <em>off_x</em> and <em>off_y</em> specify the position at
which to create the explod.
If the explod is bound, <em>off_x</em> and <em>off_y</em> specify the offset from the
object to which the explod is bound to.</dd>
<dt>facing = <em>facing</em> (int)</dt>
<dd>Set <em>facing</em> to 1 to have the explod face in the same direction as
the positive <em>off_x</em>, and -1 to have the explod face in the opposite
direction. Defaults to 1.</dd>
<dt>vfacing = <em>vfacing</em> (int)</dt>
<dd>Set <em>vfacing</em> to -1 to have the explod display vertically flipped,
or 1 to have the explod display vertically unflipped. Defaults to
1.</dd>
<dt>bindID = <em>bind_id</em> (int)</dt>
<dd>ID number of a player or helper to bind to.  The position of a bound
explod is relative to the object that it is bound to.
Special values are -1 (bind to any single player) and -2 (do not bind).
Defaults to -2.  The bindtime parameter is required if bindID is not -2.
Screen space explods cannot be bound.</dd>
<dt>bindtime = <em>bind_time</em> (int)</dt>
<dd>Specifies the number of game ticks to keep the explod bound.
After the bindtime has expired, the explod will be
explod will no longer be bound to the bind point, and will
maintain its position (unless affected by the vel or accel
parameters). If <em>bind_time</em> is -1, then the explod will be bound
until the explod is removed or another controller affects the bindtime.</dd>
<dt>vel = <em>x_vel</em>, <em>y_vel</em> (float, float)</dt>
<dd>Specifies initial X and Y velocity components for the explod.
These are interpreted relative to the explod's "facing" direction.
These default to 0 if omitted.</dd>
<dt>accel = <em>x_accel</em>, <em>y_accel</em> (float, float)</dt>
<dd>Specifies X and Y acceleration components for the explod. These
default to 0.</dd>
<dt>removetime = <em>rem_time</em> (int)</dt>
<dd>If <em>rem_time</em> is positive, the explod will be removed after having
been displayed for that number of game ticks. If <em>rem_time</em> is -1,
the explod will be displayed indefinitely. If <em>rem_time</em> is -2,
the explod will be removed when its animtime reaches 0. The
default value is -2.</dd>
<dt>supermovetime = <em>move_time</em> (int)</dt>
<dd>Specifies the number of ticks that the explod will be
unfrozen during a SuperPause. Used where you want the
explod to be animated during a SuperPause, such as for custom
super sparks. Defaults to 0.</dd>
<dt>pausemovetime = <em>move_time</em> (int)</dt>
<dd>Specifies the number of ticks that the explod should be
unfrozen during a Pause. Defaults to 0.</dd>
<dt>scale = <em>x_scale</em>, <em>y_scale</em> (float, float)</dt>
<dd><em>x_scale</em> and <em>y_scale</em> specify the scaling factors to apply to the
explod in the horizontal and vertical directions. Both default to
1 (no scaling) if omitted.</dd>
<dt>angle = <em>angle</em> (float)</dt>
<dd><em>angle</em> specifies the explod's drawing angle in degrees.
Defaults to 0.</dd>
<dt>yangle = <em>y_angle</em> (float)</dt>
<dd><em>y_angle</em> specifies the explod's drawing angle around the y-axis in degrees.
Defaults to 0.</dd>
<dt>xangle = <em>x_angle</em> (float)</dt>
<dd><em>x_angle</em> specifies the explod's drawing angle around the x-axis in degrees.
Defaults to 0.</dd>
<dt>sprpriority = <em>pr</em> (int)</dt>
<dd><em>pr</em> specifies the drawing priority for the explod. Animations
with higher priority get drawn over animations with lesser
priority. For instances, setting sprpriority = -3 will cause the
explod to be drawn under most characters and other explods, which
usually have sprpriority &gt;= -2.
Defaults to 0 if omitted.</dd>
<dt>ontop = <em>bvalue</em> (boolean)</dt>
<dd>Set ontop = 1 to have the explod drawn over all other sprites and
background layers. This parameter has precedence over sprpriority.
Defaults to 0.</dd>
<dt>shadow = <em>shadow</em> (int)</dt>
<dd>If <em>shadow</em> is not 0, a shadow will be drawn for the explod,
else no shadow will be drawn.  Defaults to 0.</dd>
<dt>ownpal = <em>ownpal_flag</em> (int)</dt>
<dd><p>If <em>ownpal_flag</em> is 0, the explod color will be affected by subsequent
execution of the player's PalFX and RemapPal controllers. This
is normally the default.</p>
<p class="last">If <em>ownpal_flag</em> is 1, the explod color will not be affected by subsequent
execution of the player's PalFX and RemapPal controllers.
This is the default if the anim is from fightfx.air.</p>
</dd>
<dt>remappal = <em>dst_pal_grp</em>, <em>dst_pal_item</em> (int, int)</dt>
<dd>Forces a palette remap of the explod's indexed-color sprites to the specified palette.
This parameter is used only if <em>ownpal_flag</em> is non-zero and a fight.def
anim is not used.
If <em>dst_pal_grp</em> is -1, this parameter will be ignored.
Defaults to -1, 0.</dd>
<dt>removeongethit = <em>bvalue</em> (boolean)</dt>
<dd>Setting this to 1 will cause the explod removed if the player gets
hit. Defaults to 0.</dd>
<dt>ignorehitpause = <em>bvalue</em> (boolean)</dt>
<dd>If this is 1, the explod will be animated independently of the
player that created it. If set to 0, it will not be updated when
the player is in hitpause. Defaults to 1.</dd>
<dt>trans = <em>trans_type</em> (string)</dt>
<dd>Overrides the explod's animation transparency settings. See the Trans controller for details. An "alpha" parameter may be specified if trans_type is an additive type. If omitted, does nothing.</dd>
</dl>
</dd>
<dt>Deprecated parameters:</dt>
<dd><dl>
<dt>postype = <em>postype_string</em> (string)</dt>
<dd><p><em>postype_string</em> specifies how to interpret the pos parameters.
In all cases, a positive <em>off_y</em> means a downward displacement.</p>
<p>Valid values for <em>postype_string</em> are the following:</p>
<dl>
<dt>p1</dt>
<dd>Interprets pos relative to p1's axis. A positive <em>off_x</em> is toward the front of p1.
This is the default value for postype for characters with a mugenversion of 1.0 or less.</dd>
<dt>p2</dt>
<dd>Interprets pos relative to p2's axis. A positive <em>off_x</em> is toward the front of p2.</dd>
<dt>front</dt>
<dd>Interprets <em>off_x</em> relative to the edge of the screen that p1 is
facing toward, and <em>off_y</em> relative to the top of the screen. A
positive <em>off_x</em> is to the right of the screen,
whereas a negative <em>off_x</em> is toward the left.</dd>
<dt>back</dt>
<dd>Interprets <em>off_x</em> relative to the edge of the screen that p1 is
facing away from, and <em>off_y</em> relative to the top of the screen. A
positive <em>off_x</em> is toward the center of the screen, whereas a
negative <em>off_x</em> is away from the center.
For historical reasons, the offset behavior is inconsistent with
postype = front.</dd>
<dt>left</dt>
<dd>Interprets <em>off_x</em> and <em>off_y</em> relative to the upper-left corner of
the screen. A positive <em>off_x</em> is toward the right of the
screen.</dd>
<dt>right</dt>
<dd>Interprets <em>off_x</em> and <em>off_y</em> relative to the upper-right corner of
the screen. A positive <em>off_x</em> is toward the right of the
screen.</dd>
<dt>none</dt>
<dd>Interprets <em>off_x</em> and <em>off_y</em> as an absolute position.
This is the default value for postype for characters with a mugenversion
of 1.1 or higher.</dd>
</dl>
<p>The use of p1 or p2 postype will create an explod in stage space.
The use of front, back, left or right postype will create an explod in
screen space.</p>
<p>The postype parameter has been deprecated in 1.1, with its functionality
replaced by a combination of the space and bindID parameters, as well as
the ScreenWidth, ScreenHeight, and various Edge triggers.</p>
<p>In 1.1, the equivalent parameters that replace postype are:</p>
<p>postype = p1</p>
<pre class="literal-block">space = stage
pos = Pos X + CameraPos X, Pos Y
facing = facing
</pre>
<p>postype = p2</p>
<pre class="literal-block">space = stage
pos = (enemynear, Pos X) + CameraPos X, (enemynear, Pos Y)
facing = enemynear, facing
</pre>
<p>postype = front</p>
<pre class="literal-block">space = screen
pos = ifelse(facing = -1, 0, ScreenWidth), 0
facing = 1
</pre>
<p>postype = back</p>
<pre class="literal-block">space = screen
pos = ifelse(facing = 1, 0, ScreenWidth), 0
facing = facing
</pre>
<p>postype = left</p>
<pre class="literal-block">space = screen
pos = 0, 0
facing = 1
</pre>
<p>postype = right</p>
<pre>space = screen
pos = ScreenWidth, 0
facing = 1
</pre>
</dd>
<dt>random = <em>rand_x</em>, <em>rand_y</em> (int, int)</dt>
<dd>Causes the explod's bind point to be displaced by a random amount
when created. <em>rand_x</em> specifies the displacement range in the x
direction, and <em>rand_y</em> specifies the displacement range in the y
direction. For instance, if pos = 0,0 and random = 40,80, then the
explod's x location will be a random number between -20 and 19,
and its y location will be a random number between -40 and 39.
Both arg1 and arg2 default to 0 if omitted.</dd>
<dt>supermove = <em>bvalue</em> (boolean)</dt>
<dd><p><strong>This parameter is deprecated -- use supermovetime parameter instead</strong></p>
<p class="last">Set supermove = 1 to have the explod persist until the end of a
super pause, regardless of the value of removetime. Defaults to 0.</p>
</dd>
</dl>
</dd>
<dt>Notes:</dt>
<dd><p>The position of an explod that is bound to a player is determined only after
all player updates have completed (compared to helpers, which are created
relative to the player's immediate position when the controller was executed).
This behavior is necessary to make explods bind properly to the player's
screen position.</p>
<p class="last">For example, assume the player has an x velocity of 5 and a position of (160,0).
If an explod is created with an offset of 0,0 relative to p1, then the explod's
actual screen position will be 165,0.</p>
</dd>
</dl>
    """
    result = StateController()

    set_if(result, "anim", anim)
    set_if(result, "id", id)
    set_if_tuple(result, "pos", pos, FloatPairType)
    set_if(result, "postype", postype)
    set_if(result, "space", space)
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
    set_if(result, "angle", angle)
    set_if_tuple(result, "alpha", alpha, IntPairType)

    return result

@controller(id = [IntType, None], time = [IntType, None])
def ExplodBindTime(id: Optional[ConvertibleExpression] = None, time: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>ExplodBindTime</h2>
<p>Changes the position binding time of the player's explods.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>ID = <em>id_no</em> (int)</dt>
<dd>Only explods with ID number equal to <em>id_no</em> will have their
position binding affected. Set ID to -1 to affect the binding of
all explods. The default value is -1.</dd>
<dt>time = <em>binding_time</em> (int)</dt>
<dd>Specifies the number of ticks for which the explods should be
bound to their binding points (defined at the time the explods
were created.) Defaults to 1 tick. A time of -1 binds the explods
indefinitely or until another controller changes the bindtime.</dd>
</dl>
</dd>
<dt>Alternate syntax:</dt>
<dd>value = <em>binding_time</em> may be used instead of time = <em>binding_time</em>.</dd>
</dl>
    """
    result = StateController()

    set_if(result, "id", id)
    set_if(result, "time", time)

    return result

@controller(
    waveform = [WaveTypeT, None],
    time = [IntType, None],
    freq = [WaveTupleType, None],
    ampl = [WaveTupleType, None],
    self = [BoolType, None]
)
def ForceFeedback(waveform: Optional[ConvertibleExpression] = None, time: Optional[ConvertibleExpression] = None, freq: Optional[TupleExpression] = None, ampl: Optional[TupleExpression] = None, self: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>ForceFeedback</h2>
<p>Creates force feedback for supported force feedback devices. <strong>This controller is not implemented in MUGEN 1.0.</strong></p>
<p>Parameters to the ForceFeedback controller may not be specified using arithmetic expressions. It is an exception in this regard.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>waveform = <em>wave_type</em> (string)</dt>
<dd>Valid waveforms are "sine", "square", "sinesquare", and "off". For
the Dual Shock controller, a sine waveform corresponds to the
large rumble motor, and a square waveform corresponds to the
smaller buzzer motor. sinesquare, of course, corresponds to both
motors simultaneously. Use "off" to turn off any force feedback
that is currently executing. waveform defaults to sine.</dd>
<dt>time = <em>duration</em> (integer constant)</dt>
<dd>Specifies how long the force feedback should last, in ticks.
Defaults to 60.</dd>
<dt>freq = <em>start</em> (integer constant), <em>d1</em>, <em>d2</em>, <em>d3</em> (float constants)</dt>
<dd>Force feedback frequency varies between 0 and 255. The formula
used to determine force feedback frequency is
start + <em>d1</em> * t + <em>d2</em> * t ** 2 + <em>d3</em> * t ** 3
where t represents the number of ticks elapsed since the force
feedback was initiated. Defaults to
freq = 128,0,0,0.
Currently, the frequency parameter is completely ignored.</dd>
<dt>ampl = <em>start</em> (integer constant), <em>d1</em>, <em>d2</em>, <em>d3</em> (float constants)</dt>
<dd>Force feedback amplitude varies between 0 and 255. The formula
used to determine force feedback frequency is
start + <em>d1</em> * t + <em>d2</em> * t ** 2 + <em>d3</em> * t ** 3
where t represents the number of ticks elapsed since the force
feedback was initiated. Defaults to
ampl = 128,0,0,0</dd>
<dt>self = <em>self_flag</em> (boolean constant)</dt>
<dd>If <em>self_flag</em> is 1, then P1's pad will vibrate. If self is 0, then P2's
pad will vibrate. Defaults to 1.</dd>
</dl>
</dd>
</dl>
    """
    result = StateController()

    set_if(result, "waveform", waveform)
    set_if(result, "time", time)
    set_if_tuple(result, "freq", freq, WaveTupleType)
    set_if_tuple(result, "ampl", ampl, WaveTupleType)
    set_if(result, "self", self)

    return result

@controller()
def FallEnvShake(ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>FallEnvShake</h2>
<p>Shakes the screen using the fall.envshake parameters set by an attack (see HitDef controller). This controller is effective only if GetHitVar(fall.envshake.time) is not zero, and it sets GetHitVar(fall.envshake.time) to zero after being executed. This controller is used in common1.cns to shake the screen when a player falls, and is not normally useful otherwise.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd>none</dd>
</dl>
    """
    result = StateController()
    return result

@controller(value = [IntType, None], under = [BoolType, None], pos = [FloatPairType, None], random = [IntType, None])
def GameMakeAnim(value: Optional[ConvertibleExpression] = None, under: Optional[ConvertibleExpression] = None, pos: Optional[TupleExpression] = None, random: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>GameMakeAnim</h2>
<p>Creates a game animation, like a hit spark or a super charging effect. This controller has been superseded by Explod and is now considered deprecated. Support for it may be removed in future versions.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>value = <em>anim_no</em> (int)</dt>
<dd>Specifies the animation number (from fightfx) of the animation to
play. Defaults to 0.</dd>
<dt>under = <em>under_flag</em> (int)</dt>
<dd>If <em>under_flag</em> is 1, the animation is drawn behind the character
sprites. Defaults to 0 (draw over characters).</dd>
<dt>pos = <em>x_pos</em>, <em>y_pos</em> (float)</dt>
<dd>Specifies the position to display the animation at, relative to
the player axis. Defaults to 0,0.</dd>
<dt>random = <em>rand_amt</em> (int)</dt>
<dd>The position of the animation will be displaced in the x and y
directions by (different) random amounts. The displacement can be
as large as half of rand_amt. Defaults to 0.</dd>
</dl>
</dd>
</dl>
    """
    result = StateController()

    set_if(result, "value", value)
    set_if(result, "under", under)
    set_if_tuple(result, "pos", pos, FloatPairType)
    set_if(result, "random", random)

    return result

@controller()
def Gravity(ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>Gravity</h2>
<p>Accelerates the player downwards, using the value of the player's "yaccel" constant.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd>none</dd>
</dl>
    """
    result = StateController()
    return result

@controller(
    helpertype = [HelperTypeT, None],
    name = [StringType, None],
    id = [IntType, None],
    pos = [FloatPairType, None],
    postype = [PosTypeT, None],
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
    stateno: Optional[Union[Expression, str, int, Callable[..., None | StateController]]] = None, 
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
    """
<h2>Helper</h2>
<p>Creates another instance of the player as a helper character.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>helpertype = <em>type_string</em> (string)</dt>
<dd><strong>This parameter is deprecated; player-type helpers are not supported.</strong>
If helpertype = normal, then the helper will be allowed to move
off the edge of the screen. Furthermore, the camera will not move
to try to keep the helper on screen. If helpertype = player, then
the helper will be constrained to the screen and will be followed
by the camera, just like a normal player. Defaults to normal.
If you plan to use a helper for camera manipulation, do not use
a player-type helper; instead use the ScreenBound
controller in a normal helper with the "movecamera" parameter.</dd>
<dt>name = "<em>name_string</em>" (string)</dt>
<dd>Specifies a name for this helper, which must be enclosed in double
quotes. If omitted, the name defaults to "&lt;parent&gt;'s helper",
where &lt;parent&gt; represents the name of the player creating the
helper.</dd>
<dt>ID = <em>id_no</em> (int)</dt>
<dd>Sets an ID number to refer to this helper by. Defaults to 0.</dd>
<dt>pos = <em>off_x</em>, <em>off_y</em> (float)</dt>
<dd>Specifies the x and y offsets to create this helper at. The
precise meaning of these parameters is dependent on the postype.
Defaults to 0,0.</dd>
<dt>postype = <em>postype_string</em> (string)</dt>
<dd><p><em>postype_string</em> specifies the postype -- how to interpret the pos
parameters.
In all cases, a positive y offset means a downward displacement.
In all cases, <em>off_y</em> is relative to the position of the player.</p>
<p>Valid values for <em>postype_string</em> are the following:</p>
<dl class="last docutils">
<dt>p1</dt>
<dd>Interprets offset relative to p1's axis. A positive <em>off_x</em> is
toward the front of p1. This is the default value for postype.</dd>
<dt>p2</dt>
<dd>Interprets offset relative to p2's axis. A positive <em>off_x</em> is
toward the front of p2.  If p2 does not exist, the position is
calculated with respect to p1 and a warning is logged.</dd>
<dt>front</dt>
<dd>Interprets <em>off_x</em> relative to the edge of the screen that p1 is
facing toward. A positive <em>off_x</em>
is away from the center of the screen, whereas a
negative <em>off_x</em> is toward the center.</dd>
<dt>back</dt>
<dd>Interprets <em>off_x</em> relative to the edge of the screen that p1 is
facing away from. A positive <em>off_x</em>
is toward the center of the screen, whereas a
negative <em>off_x</em> is away from the center.</dd>
<dt>left</dt>
<dd>Interprets <em>off_x</em> relative to the left edge of
the screen. A positive <em>off_x</em> is toward the right of the
screen.</dd>
<dt>right</dt>
<dd>Interprets <em>off_x</em> relative to the right edge of
the screen. A positive <em>off_x</em> is toward the right of the
screen.</dd>
</dl>
</dd>
<dt>facing = <em>facing</em> (int)</dt>
<dd>If postype is left or right, setting <em>facing</em> to 1 will make the
helper face the right, and a value of -1 makes the helper face
left.
For all other values of postype except p2, if <em>facing</em> is 1, the
helper will face the same direction as the player. If <em>facing</em> is
-1, the helper will face the opposite direction.
In the case of postype = p2, <em>facing</em> has the same effect as above,
except it is with respect to p2's facing. Defaults to 1.</dd>
<dt>stateno = <em>start_state</em> (int)</dt>
<dd>Determines the state number that the helper starts off in.
Defaults to 0.</dd>
<dt>keyctrl = <em>ctrl_flag</em> (boolean)</dt>
<dd>If <em>ctrl_flag</em> is 1, then the helper is able to read command input from
the player (e.g., the keyboard or joystick). Also, the helper will
inherit its root's State -1. If <em>ctrl_flag</em> is 0, then the helper does
not have access to command input, and does not inherit State -1.
The default value of <em>ctrl_flag</em> is 0.</dd>
<dt>ownpal = <em>ownpal_flag</em> (boolean)</dt>
<dd><p>If <em>ownpal_flag</em> is 0, the helper will be affected by subsequent
execution of its parent's PalFX and RemapPal controllers. This
is the default.</p>
<p class="last">If <em>ownpal_flag</em> is 1, the helper will receive its own working palette
which is independent of its parent's.</p>
</dd>
<dt>remappal = <em>dst_pal_grp</em>, <em>dst_pal_item</em> (int, int)</dt>
<dd>Forces a palette remap of the helper's indexed-color sprites to the specified palette.
This parameter is used only if <em>ownpal_flag</em> is non-zero.
If <em>dst_pal_grp</em> is -1, this parameter will be ignored.
Defaults to -1, 0.</dd>
<dt>supermovetime = <em>move_time</em> (int)</dt>
<dd>Specifies the number of ticks that the helper should be
unfrozen during a SuperPause. Defaults to 0.</dd>
<dt>pausemovetime = <em>move_time</em> (int)</dt>
<dd>Determines the number of ticks that the helper should be
unfrozen during a Pause. Defaults to 0.</dd>
<dt>size.xscale (float)</dt>
<dd>See below.</dd>
<dt>size.yscale (float)</dt>
<dd>See below.</dd>
<dt>size.ground.back (int)</dt>
<dd>See below.</dd>
<dt>size.ground.front (int)</dt>
<dd>See below.</dd>
<dt>size.air.back (int)</dt>
<dd>See below.</dd>
<dt>size.air.front (int)</dt>
<dd>See below.</dd>
<dt>size.height (int)</dt>
<dd>See below.</dd>
<dt>size.proj.doscale (int)</dt>
<dd>See below.</dd>
<dt>size.head.pos (int,int)</dt>
<dd>See below.</dd>
<dt>size.mid.pos (int,int)</dt>
<dd>See below.</dd>
<dt>size.shadowoffset (int)</dt>
<dd>These parameters have the same meaning as the corresponding
parameters in the root's CNS file. You can specify one or more of
these parameters to change it to a value suitable for this helper.
Otherwise, they default to the values inherited from the parent.</dd>
</dl>
</dd>
</dl>
    """
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
    """
<h2>HitAdd</h2>
<p>Adds to the current combo counter.</p>
<dl>
<dt>Required parameters:</dt>
<dd><dl>
<dt>value = <em>add_count</em> (int)</dt>
<dd><em>add_count</em> specifies the number of hits to add to the current
combo counter.</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd>none</dd>
</dl>
    """
    result = StateController()

    set_if(result, "value", value)

    return result

@controller(value = [HitStringType, None], value2 = [HitStringType, None], time = [IntType, None])
def HitBy(value: Optional[TupleExpression] = None, value2: Optional[TupleExpression] = None, time: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>HitBy</h2>
<p>Temporarily specifies the types of hits that are be allowed hit to the player.</p>
<dl>
<dt>Required parameters:</dt>
<dd><dl>
<dt>value = <em>attr_string</em>  OR  value2 = <em>attr_string</em></dt>
<dd>Only one of the above parameters can be specified. <em>attr_string</em>
should be a standard hit attribute string.  See Details.</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>time = <em>effective_time</em> (int)</dt>
<dd>Specifies the number of game ticks that these HitBy attributes
should be effective for. Defaults to 1.</dd>
</dl>
</dd>
<dt>Details:</dt>
<dd>The player has two hit attribute slots, which can be set using the
value or value2 parameters to the HitBy controller. These slots can
also be set by the NotHitBy controller. When a slot is set, it gets
a timer (the effective time) which counts down toward zero. If the
timer has not yet reached zero, the slot is considered to be active.
The player can be hit by a HitDef only if that HitDef's attribute
appears in all currently active slots.
Using the HitBy controller sets the specified slot to contain only
those hit attributes which appear in the HitBy attribute string.</dd>
</dl>
    """
    result = StateController()

    set_if_tuple(result, "value", value, HitStringType)
    set_if_tuple(result, "value2", value2, HitStringType)
    set_if(result, "time", time)

    return result

@controller(
    attr = [HitStringType],
    hitflag = [HitFlagTypeF, None],
    guardflag = [GuardFlagTypeF, None],
    affectteam = [TeamTypeT, None],
    animtype = [HitAnimTypeT, None],
    air_animtype = [HitAnimTypeT, None],
    fall_animtype = [HitAnimTypeT, None],
    priority = [PriorityPairType, None],
    damage = [IntPairType, None],
    pausetime = [IntPairType, None],
    guard_pausetime = [IntPairType, None],
    sparkno = [SpriteType, IntType, None],
    guard_sparkno = [SpriteType, IntType, None],
    sparkxy = [IntPairType, None],
    hitsound = [SoundPairType, None],
    guardsound = [SoundPairType, None],
    ground_type = [AttackTypeT, None],
    air_type = [AttackTypeT, None],
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
    pausetime: Optional[TupleExpression] = None, 
    guard_pausetime: Optional[TupleExpression] = None, 
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
    p1stateno: Optional[Union[Expression, str, int, Callable[..., None | StateController]]] = None,
    p2stateno: Optional[Union[Expression, str, int, Callable[..., None | StateController]]] = None,
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
    """
<h2>HitDef</h2>
<p>Defines a single hit of the player's attack. If the player's Clsn1 box (red) comes in contact with his opponent's Clsn2 box (blue), and the HitDef was define on or before that particular point in time, then the specified effect will be applied. This is one of the more complex, but most commonly-used controllers.
A single HitDef is valid only for a single hit. To make a move hit several times, you must trigger more than one HitDef during the attack.</p>
<dl>
<dt>Required parameters:</dt>
<dd><dl>
<dt>attr = <em>hit_attribute</em> (string)</dt>
<dd><p>This is the attribute of the attack. It is used to determine if
the attack can hit P2. It has the format:</p>
<p>attr = <em>arg1</em>, <em>arg2</em></p>
<p>Where:
<em>arg1</em> is either "S", "C" or "A". Similar to "statetype" for the
StateDef, this says whether the attack is a standing, crouching,
or aerial attack.</p>
<p class="last"><em>arg2</em> is a 2-character string. The first character is either "N"
for "normal", "S" for "special", or "H" for "hyper" (or "super",
as it is commonly known). The second character must be either
"A" for "attack" (a normal hit attack), "T" for "throw", or "P"
for projectile.</p>
</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>hitflag = <em>hit_flags</em> (string)</dt>
<dd><p>This determines what type of state P2 must be in for P1 to hit. <em>hit_flags</em> is a string containing a combination of the following characters:</p>
<p>"H" for "high", "L" for "low" or "A" for air. "M" (mid) is equivalent to saying "HL". "F" is for fall, and if included will allow P1 to juggle falling opponents in the air. "D" is for "lying Down", and if included allows P1 to hit opponents lying down on the ground. "H", "L" or "A" (or "M") must be present in the hitflag string.</p>
<p>Two optional characters are "+" and "-". If "+" is added, then the hit only affects people in a gethit state. This may be useful for chain-moves that should not affect opponents who were not hit by the first move in the chain attack. If "-" is added, then the hit only affects players that are NOT in a gethit state. You should use "-" for throws and other moves you do not want P1 to be able to combo into. "+" and "-" are mutually exclusive, ie. cannot be used at the same time.</p>
<p class="last">If omitted, this defaults to "MAF".</p>
</dd>
<dt>guardflag = <em>hit_flags</em> (string)</dt>
<dd><p>This determines how P2 may guard the attack. hit_flags is a string containing a combination of the following characters:</p>
<p class="last">"H" for "high", "L" for "low" or "A" for air. "M" (mid) is equivalent to saying "HL". If omitted, defaults to an empty string, meaning P2 cannot guard the attack.</p>
</dd>
<dt>affectteam = <em>team_type</em> (string)</dt>
<dd><em>team_type</em> specifies which team's players can be hit by this
HitDef. Use B for both teams (all players), E for enemy team
(opponents), or F for friendly team (your own team). The default
is E.</dd>
<dt>animtype = <em>anim_type</em> (string)</dt>
<dd>This refers to the type of animation that P2 will go into when hit
by the attack. Choose from "light", "medium", "hard", "back", "up",
or "diagup".
The first three are self-explanatory. "Back" is the
animation where P2 is knocked off her feet. "Up" should be used
when the character is knocked straight up in the air (for instance,
by an uppercut), and "DiagUp" should be used when the character is
knocked up and backwards in the air, eventually landing on his
head.
The default is "Light".</dd>
<dt>air.animtype = <em>anim_type</em> (string)</dt>
<dd>Similar to the "animtype" parameter, this is the animtype to set
P2 to if P2 is in the air, instead of on the ground. Defaults to
the same value as the "animtype" parameter if omitted.</dd>
<dt>fall.animtype = <em>anim_type</em> (string)</dt>
<dd>Similar to the "animtype" parameter, this is the animtype to set
P2 to if P2 is hit while falling. Defaults to Up if air.animtype
is Up, or Back otherwise.</dd>
<dt>priority = <em>hit_prior</em> (int), <em>hit_type</em> (string)</dt>
<dd><p>Specifies the priority for this hit. Hits with higher priorities take precedence over hits with lower priorities. Valid values for <em>hit_prior</em> are 1-7. Defaults to 4.</p>
<p><em>hit_type</em>, if specified, gives the priority class of the hit. Valid priority classes are Dodge, Hit, and Miss. The priority class determines the tiebreaking behavior when P1 and P2 hit each other simultaneously with equal priorities. The behavior for P1 vs. P2 is as follows:</p>
<ul class="simple">
<li>Hit vs. Hit: both P1 and P2 are hit</li>
<li>Hit vs. Miss: P1 hits, P2 misses</li>
<li>Hit vs. Dodge: Both miss</li>
<li>Dodge vs. Dodge: Both miss</li>
<li>Dodge vs. Miss: Both miss</li>
<li>Miss vs. Miss: Both miss</li>
</ul>
<p class="last">In the case of a no-hit tie, the respective HitDefs stay enabled. "Miss" or "Dodge" are typically used for throws, where P1 and P2 should not be able to simultaneously hit each other. The default for <em>hit_type</em> is "Hit".</p>
</dd>
<dt>damage = <em>hit_damage</em>, <em>guard_damage</em> (int, int)</dt>
<dd><em>hit_damage</em> is the damage that P2 takes when hit by P2. The
optional <em>guard_damage</em> parameter is the damage taken by P2 if the
hit is guarded. Both default to zero if omitted.</dd>
<dt>pausetime = <em>p1_pausetime</em>, <em>p2_shaketime</em> (int, int)</dt>
<dd>This is the time that each player will pause on the hit.
<em>p1_pausetime</em> is the time to freeze P1, measured in game-ticks.
<em>p2_pausetime</em> is the time to make P2 shake before recoiling from
the hit. Defaults to 0,0 if omitted.</dd>
<dt>guard.pausetime = <em>p1_pausetime</em>, <em>p2_shaketime</em> (int, int)</dt>
<dd>Similar to the "pausetime" parameter, these are the times
to pause each player if the hit was guarded.
Defaults to the same values as the "pausetime" parameter if
omitted.</dd>
<dt>sparkno = <em>action_no</em> (int)</dt>
<dd>This is the action number of the spark to display if the hit
is successful. To play a spark out of the player's .AIR file,
precede the action number with an S, e.g. "sparkno = S10".
Defaults to the value set in the player variables if omitted.</dd>
<dt>guard.sparkno = <em>action_no</em> (int)</dt>
<dd>This is the action number of the spark to display if the hit
was guarded. To play a spark out of the player's .AIR file,
precede the action number with an S.
Defaults to the value set in the player variables if omitted.</dd>
<dt>sparkxy = <em>spark_x</em>, <em>spark_y</em> (int, int)</dt>
<dd>This is where to make the hit/guard spark.
<em>spark_x</em> is a coordinate relative to the front of P2. A negative
value makes the spark deeper inside P2. "Front" refers to the x-
position at P2's axis offset towards P1 by the corresponding
width value in the [Size] group in P2's player variables.
<em>spark_y</em> is relative to P1. A negative value makes a spark higher
up. You can use a tool like AirView to determine this value by
positioning the cursor at the "attack spot" and reading off the
value of the y-position.
Defaults to 0,0 if omitted.</dd>
<dt>hitsound = <em>snd_grp</em>, <em>snd_item</em> (int, int)</dt>
<dd>This is the sound to play on hit (from common.snd). The included
fight.snd lets you choose from 5,0 (light hit sound) through to
5,4 (painful whack). To play a sound from the player's own SND
file, precede the first number with an "S". For example,
"hitsound = S1,0".
Defaults to the value set in the player variables if omitted.</dd>
<dt>guardsound = <em>snd_grp</em>, <em>snd_item</em> (int, int)</dt>
<dd>This is the sound to play on guard (from common.snd). Only 6,0 is
available at this time. To play a sound from the player's own SND
file, precede the first number with an "S". There is no facility
to play a sound from the opponent's SND file.
Defaults to the value set in the player variables if omitted.</dd>
<dt>ground.type = <em>attack_type</em> (string)</dt>
<dd><p>This is the kind of attack if P2 is on the ground. Choose from:
- "High": for attacks that make P2's head snap backwards.
- "Low": for attacks that hit P2 in the stomach.
- "Trip": for low sweep attacks. If you use "Trip" type, the ground.velocity parameter should have a non-zero y-velocity, and the fall parameter should be set to 1. A tripped opponent does not bounce upon falling on the ground.
- "None": for attacks that do nothing besides pause P1 and P2 for the duration in the pausetime parameter.</p>
<p class="last">If P2 is hit from behind, "High" will be displayed as "Low" and vice-versa. P2's animation for "High" and "Low" types will be superseded if the AnimType parameter is "Back". Defaults to "High" if omitted.</p>
</dd>
<dt>air.type = <em>attack_type</em> (string)</dt>
<dd>This is the kind of attack if P2 is in the air. Defaults to the
same value as "ground.type" if omitted.</dd>
<dt>ground.slidetime = <em>slide_time</em> (int)</dt>
<dd>This is the time in game-ticks that P2 will slide back for after
being hit (this time does not include the pausetime for P2).
Applicable only to hits that keep P2 on the ground.
Defaults to 0 if omitted.</dd>
<dt>guard.slidetime = <em>slide_time</em> (int)</dt>
<dd>Same as "ground.slidetime", but this is the value if P2 guards the
hit. Defaults to same value as "guard.hittime".</dd>
<dt>ground.hittime = <em>hit_time</em> (int)</dt>
<dd>Time that P2 stays in the hit state after being hit. Adjust this value carefully, to make combos possible. Applicable only to hits that keep P2 on the ground. Defaults to 0 if omitted.</dd>
<dt>guard.hittime = <em>hit_time</em> (int)</dt>
<dd>Same as "ground.hittime", but this is the value if P2 guards the
hit. Defaults to same value as "ground.hittime".</dd>
<dt>air.hittime = <em>hit_time</em> (int)</dt>
<dd>Time that p2 stays in the hit state after being hit in or into the
air, before being able to guard again. This parameter has no effect
if the "fall" parameter is set to 1. Defaults to 20 if omitted.</dd>
<dt>guard.ctrltime = <em>ctrl_time</em> (int)</dt>
<dd>This is the time before p2 regains control in the ground guard
state. Defaults to the same value as "guard.slidetime" if omitted.</dd>
<dt>guard.dist = <em>x_dist</em> (int)</dt>
<dd>This is the x-distance from P1 in which P2 will go into a guard
state if P2 is holding the direction away from P1. Defaults to
the value in the player variables if omitted. You normally do
not need to use this parameter.</dd>
<dt>yaccel = <em>accel</em> (float)</dt>
<dd>Specifies the y acceleration to impart to P2 if the hit connects.
Defaults to .35 in 240p, .7 in 480p, 1.4 in 720p.</dd>
<dt>ground.velocity = <em>x_velocity</em>, <em>y_velocity</em> (float, float)</dt>
<dd>Initial velocity to give P2 after being hit, if P2 is on the
ground. If <em>y_velocity</em> is not zero, P2 will be knocked into the
air. Both values default to 0 if omitted. You can leave out
the <em>y_velocity</em> if you want P2 to remain on the ground.</dd>
<dt>guard.velocity = <em>x_velocity</em> (float)</dt>
<dd>Velocity to give P2 if P2 guards the hit on the ground.
Defaults to the <em>x_velocity</em> value of the "ground.velocity"
parameter if omitted.</dd>
<dt>air.velocity = <em>x_velocity</em>, <em>y_velocity</em> (float, float)</dt>
<dd>Initial velocity to give P2 if P2 is hit in the air.
Defaults to 0,0 if omitted.</dd>
<dt>airguard.velocity = <em>x_velocity</em>, <em>y_velocity</em> (float float)</dt>
<dd>Velocity to give P2 if P2 guards the hit in the air. Defaults
to <em>x_velocity</em> * 1.5, <em>y_velocity</em> / 2, where <em>x_velocity</em> and <em>y_velocity</em>
are values of the "air.velocity" parameter.</dd>
<dt>ground.cornerpush.veloff = <em>x_velocity</em> (float)</dt>
<dd>Determines the additional velocity (velocity offset) to impart to
the player if he lands a ground hit in the corner. Setting this
to a higher value will cause the player to be "pushed back" farther
out of the corner. If omitted, default value depends on the attr
parameter. If arg1 of attr is "A", default value is 0. Otherwise,
defaults to 1.3 * guard.velocity.</dd>
<dt>air.cornerpush.veloff = <em>x_velocity</em> (float)</dt>
<dd>Determines the additional velocity (velocity offset) to impart to
the player if he lands a hit to an aerial opponent in the corner.
Setting this to a higher value will cause the player to be "pushed
back" farther out of the corner. Defaults to
ground.cornerpush.veloff if omitted.</dd>
<dt>down.cornerpush.veloff = <em>x_velocity</em> (float)</dt>
<dd>Determines the additional velocity (velocity offset) to impart to
the player if he lands a hit on a downed opponent in the corner.
Setting this to a higher value will cause the player to be "pushed
back" farther out of the corner. Defaults to
ground.cornerpush.veloff if omitted.</dd>
<dt>guard.cornerpush.veloff = <em>x_velocity</em> (float)</dt>
<dd>Determines the additional velocity (velocity offset) to impart to
the player if his hit is guarded in the corner. Setting this
to a higher value will cause the player to be "pushed back" farther
out of the corner. Defaults to ground.cornerpush.veloff if omitted.</dd>
<dt>airguard.cornerpush.veloff = <em>x_velocity</em> (float)</dt>
<dd>Determines the additional velocity (velocity offset) to impart to
the player if his hit is guarded in the corner. Setting this
to a higher value will cause the player to be "pushed back" farther
out of the corner. Defaults to guard.cornerpush.veloff if omitted.</dd>
<dt>airguard.ctrltime = <em>ctrl_time</em> (int)</dt>
<dd>This is the time before p2 regains control in the air guard state.
Defaults to the same value as "guard.ctrltime" if omitted.</dd>
<dt>air.juggle = <em>juggle_points</em> (int)</dt>
<dd>The amount of additional juggle points the hit requires. Not to be
confused with the "juggle" parameter in the StateDef.
You typically do not need this parameter, except for HitDefs of
projectiles. Defaults to 0 if omitted.</dd>
<dt>mindist = <em>x_pos</em>, <em>y_pos</em> (int, int)</dt>
<dd>See below.</dd>
<dt>maxdist = <em>x_pos</em>, <em>y_pos</em> (int, int)</dt>
<dd>These let you control the minimum and maximum distance of P2
relative to P1, after P2 has been hit. These parameters are not
commonly used.
Defaults to no change in P2's position if omitted.</dd>
<dt>snap = <em>x_pos</em>, <em>y_pos</em> (int, int)</dt>
<dd>This moves P2 to the specified position relative to P1 if hit. This parameter is not normally used. If you want to snap P2 to a particular position for a throw, it is recommended you use a "TargetBind" controller in P1's throwing state instead. Defaults to no change in P2's position if omitted.</dd>
<dt>p1sprpriority = <em>drawing_priority</em> (int)</dt>
<dd>This is the drawing priority of P1's sprite if the move hits or is guarded by P2. Together with the p2sprpriority parameter, it controls whether or not P1 is drawn in front of or behind P2. The default value is 1.</dd>
<dt>p2sprpriority = <em>drawing_priority</em> (int)</dt>
<dd>This is the drawing priority of P2's sprite if the move hits or is guarded by P2. The default value is 0.</dd>
<dt>p1facing = <em>facing</em> (int)</dt>
<dd>Set to -1 to make P1 turn around if the hit is successful.
The default value is no change in where P1 is facing.</dd>
<dt>p1getp2facing = <em>facing</em> (int)</dt>
<dd>Set to 1 to have P1 face in the same direction as P2 is facing
after the hit connects, and -1 to have P1 face the opposite
direction from P2. Defaults to 0 (no change). If nonzero, this
parameter takes precedence over p1facing.</dd>
<dt>p2facing = <em>facing</em> (int)</dt>
<dd>Set to 1 to make P2 face the same direction as P1 if the hit
is successful, -1 to make P2 face away.
The default value is 0, no change in where P2 is facing.</dd>
<dt>p1stateno = <em>state_no</em> (int)</dt>
<dd>This is the number of the state to set P1 to if the hit is successful. The state must be an attack state (movetype = A) for at least 1 tick. Used mainly for throws. Defaults to -1, no change.</dd>
<dt>p2stateno = <em>state_no</em> (int)</dt>
<dd>This is the number of the state to set P2 to if the hit is successful. P2 will get P1's state and animation data. P2 will retain P1's states and animation data until P2 is hit, or a SelfState controller is used to return P2 to his own states. The state must be a get-hit state (movetype = H) for at least 1 tick. Used mainly for throws; can also be used for custom hit reactions. Defaults to -1, no change.</dd>
<dt>p2getp1state = <em>bvalue</em> (boolean)</dt>
<dd>Set to 0 to prevent P2 from getting P1's state and animation
data, in case you do not want that default behaviour of the
"p2stateno" parameter. Defaults to 1 if the "p2stateno"
parameter is used. Ignored otherwise.</dd>
<dt>forcestand = <em>bvalue</em> (boolean)</dt>
<dd>Set to 1 to force P2 to a standing state-type if the hit is successful, and P2 is in a crouching state. Has no effect if P2 is in an air state. Normally defaults to 0, but if the y_velocity of the "ground.velocity" parameter is non-zero, it defaults to 1.</dd>
<dt>fall = <em>bvalue</em> (boolean)</dt>
<dd>Set to 1 if you want P2 to go into a "fall" state (where
P2 hits the ground without regaining control in the air).
Use if you want a move to "knock down" P2. Defaults to 0.</dd>
<dt>fall.xvelocity = <em>x_velocity</em> (float)</dt>
<dd>This is the x-velocity that P2 gets when bouncing off the ground
in the "fall" state. Defaults to no change if omitted.</dd>
<dt>fall.yvelocity = <em>y_velocity</em> (float)</dt>
<dd>This is the y-velocity that P2 gets when bouncing off the ground
in the "fall" state. Defaults to -4.5 in 240p, -9 in 480p, -18 in 720p.</dd>
<dt>fall.recover = <em>bvalue</em> (boolean)</dt>
<dd>Set to 0 if you do not want P2 to be able to recover from the
"fall" state. Defaults to 1 if omitted (can recover).</dd>
<dt>fall.recovertime = <em>recover_time</em> (int)</dt>
<dd>This is the time that must pass before P2 is able to recover from the "fall" state by inputting his recovery command. Does not include the time that P2 is paused for while shaking from the hit. Defaults to 4 if omitted.</dd>
<dt>fall.damage = <em>damage_amt</em> (int)</dt>
<dd>Indicates the amount of damage to deal when P2 hits the ground
out of a falling state. Defaults to 0 if omitted.</dd>
<dt>air.fall = <em>bvalue</em> (boolean)</dt>
<dd>Set to 1 if you want P2 to go into a "fall" state (where P2 hits the ground without regaining control in the air) if hit while P2 is in the air. Defaults to the same value as fall.</dd>
<dt>forcenofall = <em>bvalue</em> (boolean)</dt>
<dd>Set to 1 to force P2 out of a "fall" state, if he is in one. This parameter has no effect on P2 if he is not in a "fall" state. This parameter is ignored if the "fall" parameter is set to 1. Defaults to 0 if omitted.</dd>
<dt>down.velocity = <em>x_velocity</em>, <em>y_velocity</em> (float, float)</dt>
<dd>This is the velocity to assign P2 if P2 is hit while lying down.
If the <em>y_velocity</em> is non-zero, P2 will be hit into the air. If
it is zero, then P2 will slide back on the ground.
Defaults to the same values as the "air.velocity" parameter if
omitted.</dd>
<dt>down.hittime = <em>hit_time</em> (int)</dt>
<dd>This is the time that P2 will slide back for if P2 is hit while
lying down. This parameter is ignored if the <em>y_velocity</em> is non-
zero for the "down.velocity" parameter.</dd>
<dt>down.bounce = <em>bvalue</em> (boolean)</dt>
<dd>Set to 1 if you want P2 to bounce off the ground one time (using the fall.xvelocity and fall.yvelocity values) after hitting the ground from the hit. This parameter is ignored if the <em>y_velocity</em> is zero for the "down.velocity" parameter. Defaults to 0 if omitted (P2 hits the ground and stays there).</dd>
<dt>id = <em>id_number</em> (int)</dt>
<dd>Idetifier for the hit. Used for chain moves. You can use this number to
later detect if a player was last hit by this particular HitDef.
This number is called the targetID. It is used in controllers
such as TargetBind, or in the target(ID) redirection keyword.
Valid values are all values &gt;= 1. If omitted, defaults to 0 (no
ID). TargetID is not to be confused with PlayerID.</dd>
<dt>chainID = <em>id_number</em> (int)</dt>
<dd>Main use of this is for chain moves. If P2 was last hit by a
move by P1 with this ID, only then can he be hit by the HitDef
with this chainID. You can use this in the following parts of a
chain move. Note that chain moves are still possible even without
the use of the "id" and "chainid" parameters. Valid values are
all values &gt;= 1. If omitted, defaults to -1 (chain from any hit).</dd>
<dt>nochainID = <em>nochain_1</em>, <em>nochain_2</em> (int)</dt>
<dd>nochainID specifies up to 2 ID numbers of hits which cannot
be chained into this hit. If these are -1 (the default), then
chaining is not explicitly disabled for any hit ID numbers.
nochain_2 can be omitted. Except for -1, the values specified
must not coincide with the value for chainID. This parameter
has no effect if P2 is hit by a third party between P1's
previous HitDef and the current HitDef.</dd>
<dt>hitonce = <em>hitonce_flag</em> (boolean)</dt>
<dd>If set to 1, the HitDef only affects one opponent. If the hit is successful, all other targets will be dropped. Normally defaults to 0. The exception is if the "attr" parameter is a throw type, which makes it default to 1.</dd>
<dt>kill = <em>bvalue</em> (boolean)</dt>
<dd>Set to 0 if this hit should not be able to KO the opponent when
the hit is successful. Defaults to 1.</dd>
<dt>guard.kill = <em>bvalue</em> (boolean)</dt>
<dd>Set to 0 if this hit should not be able to KO the opponent when
the hit is guarded. Defaults to 1.</dd>
<dt>fall.kill = <em>bvalue</em> (boolean)</dt>
<dd>Set to 0 to prevent this attack from KO'ing the opponent
when he falls on the ground (see fall.damage). Defaults to 1.</dd>
<dt>numhits = <em>hit_count</em> (int)</dt>
<dd><em>hit_count</em> indicates how many hits this hitdef should add to the
combo counter. Must be 0 or greater. Defaults to 1.</dd>
<dt>getpower = <em>p1power</em>, <em>p1gpower</em> (int, int)</dt>
<dd>p1power specifies the amount of power to give P1 if this HitDef
connects successfully. p1gpower specifies the amount of power to
give P1 if this HitDef is guarded. If omitted, <em>p1power</em> defaults
to <em>hit_damage</em> (from "damage" parameter) multiplied by the value
of Default.Attack.LifeToPowerMul specified in data/mugen.cfg.
If <em>p1gpower</em> is omitted, it defaults to the value specified for
<em>p1power</em> divided by 2.</dd>
<dt>givepower = <em>p2power</em>, <em>p2gpower</em> (int, int)</dt>
<dd>p2power specifies the amount of power to give P2 if this HitDef
connects successfully. p2gpower specifies the amount of power to
give P2 if this HitDef is guarded. If omitted, p1power defaults
to <em>hit_damage</em> (from "damage" parameter) multiplied by the value
of Default.GetHit.LifeToPowerMul specified in data/mugen.cfg.
If <em>p1gpower</em> is omitted, it defaults to the value specified for
<em>p1power</em> divided by 2.</dd>
<dt>palfx.time = <em>palfx_time</em> (int)</dt>
<dd>See below.</dd>
<dt>palfx.mul = <em>r1</em>, <em>g1</em>, <em>b1</em> (int, int, int)</dt>
<dd>See below.</dd>
<dt>palfx.add = <em>r2</em>, <em>g2</em>, <em>b2</em> (int, int, int)</dt>
<dd>If included, this allows for palette effects on P2 if the hit is
successful. <em>palfx_time</em> is the time in game-ticks to apply palette
effects on P2. <em>palfx_time</em> is 0 by default (no effect). The rest
of the parameters are the same as in the PalFX controller.</dd>
<dt>envshake.time = <em>envshake_time</em> (int)</dt>
<dd>See below.</dd>
<dt>envshake.freq = <em>envshake_freq</em> (float)</dt>
<dd>See below.</dd>
<dt>envshake.ampl = <em>envshake_ampl</em> (int)</dt>
<dd>See below.</dd>
<dt>envshake.phase = <em>envshake_phase</em> (float)</dt>
<dd>If included, this shakes the screen if the hit is successful.
<em>envshake_time</em> is the time in game-ticks to shake the screen.
The rest of the parameters are the same as in the EnvShake
controller.</dd>
<dt>fall.envshake.time = <em>envshake_time</em> (int)</dt>
<dd>See below.</dd>
<dt>fall.envshake.freq = <em>envshake_freq</em> (float)</dt>
<dd>See below.</dd>
<dt>fall.envshake.ampl = <em>envshake_ampl</em> (int)</dt>
<dd>See below.</dd>
<dt>fall.envshake.phase = <em>envshake_phase</em> (float)</dt>
<dd>Similar to the envshake.* parameters, except the effects are
applied only when P2 hits the ground.</dd>
</dl>
</dd>
<dt>Notes:</dt>
<dd>The behavior of HitDef is undefined when executed from a
[Statedef -2] block while the player has another player's
state and animation data.</dd>
</dl>
    """
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
    set_if_tuple(result, "pausetime", pausetime, IntPairType)
    set_if_tuple(result, "guard.pausetime", guard_pausetime, IntPairType)
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
    """
<h2>HitFallDamage</h2>
<p>When the player has been hit and is in a falling state, apply damage
from the fall (specified in the hitdef) to the player.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd>none</dd>
</dl>
    """
    result = StateController()
    return result

@controller(value = [IntType, None], xvel = [FloatType, None], yvel = [FloatType, None])
def HitFallSet(value: Optional[ConvertibleExpression] = None, xvel: Optional[ConvertibleExpression] = None, yvel: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>HitFallSet</h2>
<p>When the player has been hit, sets the player's fall variables.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>value = <em>fallset_flag</em> (int)</dt>
<dd>If <em>fallset_flag</em> is -1, then this controller does not change
whether the player will fall or not. A <em>fallset_flag</em> of 0 means that
the player should not fall, and a 1 means that he should. Defaults
to -1.</dd>
<dt>xvel = <em>x_velocity</em> (float)</dt>
<dd>See below.</dd>
<dt>yvel = <em>y_velocity</em> (float)</dt>
<dd>If specified, sets the player's fall.xvel and fall.yvel
parameters, respectively. See HitDef for a description of these
parameters.</dd>
</dl>
</dd>
</dl>
    """
    result = StateController()

    set_if(result, "value", value)
    set_if(result, "xvel", xvel)
    set_if(result, "yvel", yvel)

    return result

@controller()
def HitFallVel(ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>HitFallVel</h2>
<p>If the player has been hit and is in a falling state, sets the player's velocities to the fall velocities (fall.xvel and fall.yvel) specified in the HitDef.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd>none</dd>
</dl>
    """
    result = StateController()
    return result

@controller(
    attr = [HitStringType],
    stateno = [StateNoType, IntType, StringType, None],
    slot = [IntType, None],
    time = [IntType, None],
    forceair = [BoolType, None]
)
def HitOverride(attr: TupleExpression, stateno: Optional[Union[Expression, str, int, Callable[..., None | StateController]]] = None, slot: Optional[ConvertibleExpression] = None, time: Optional[ConvertibleExpression] = None, forceair: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>HitOverride</h2>
<p>Defines a hit override. If the player is hit by an attack of the specified type, he will go to the specified state number instead of his default gethit behavior. Up to 8 hit overrides can be active at one time.</p>
<dl>
<dt>Required parameters:</dt>
<dd><dl>
<dt>attr = <em>attr_string</em> (string)</dt>
<dd>Standard hit attribute string specifying what types of hits to
override. See HitDef's description for the "attr" parameter.</dd>
<dt>stateno = <em>value</em> (int)</dt>
<dd>Specifies which state to go into if hit by a HitDef with the
specified attributes.</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>slot = <em>slot_no</em> (int)</dt>
<dd>Specifies a slot number (0 to 7) to place this hit override in.
Defaults to 0 if omitted.</dd>
<dt>time = <em>effective_time</em> (int)</dt>
<dd>Specifies how long this hit override should be active. Defaults to
1 (one tick). Set this to -1 to have this override last until
overwritten by another one.</dd>
<dt>forceair = <em>value</em> (boolean)</dt>
<dd>If set to 1, the player's gethit variables will be set as if he was
in an aerial state when hit. Useful if you want to force the player
to fall down from any hit. Defaults to 0 if omitted.</dd>
</dl>
</dd>
<dt>Notes:</dt>
<dd><p>If P1 has one or more active HitOverrides, P1 will not be affected by any
of P2's matching HitDefs that have any of the following characteristics:</p>
<ul class="last simple">
<li>p1stateno parameter value is not -1</li>
<li>p2getp1state parameter value is 1</li>
</ul>
</dd>
</dl>
    """
    result = StateController()

    set_if_tuple(result, "attr", attr, HitStringType)
    set_stateno(result, "stateno", stateno)
    set_if(result, "slot", slot)
    set_if(result, "time", time)
    set_if(result, "forceair", forceair)

    return result

@controller(x = [BoolType, None], y = [BoolType, None])
def HitVelSet(x: Optional[ConvertibleExpression] = None, y: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>HitVelSet</h2>
<p><strong>This controller is deprecated.</strong></p>
<p>When the player has been hit, sets the desired components of the player's velocity to the appropriate gethit velocities.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>x = <em>x_flag</em> (int)</dt>
<dd>A nonzero flag means to change that x-component of the player's
velocity to the gethit velocity.</dd>
<dt>y = <em>y_flag</em> (int)</dt>
<dd>A nonzero flag means to change that y-component of the player's
velocity to the gethit velocity.</dd>
</dl>
</dd>
<dt>Notes:</dt>
<dd>Obsolete.</dd>
</dl>
    """
    result = StateController()

    set_if(result, "x", x)
    set_if(result, "y", y)

    return result

@controller(value = [IntType], kill = [BoolType, None], absolute = [BoolType, None])
def LifeAdd(value: ConvertibleExpression, kill: Optional[ConvertibleExpression] = None, absolute: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>LifeAdd</h2>
<p>Adds the specified amount to the player's life, scaled by the player's defense multiplier if necessary.</p>
<dl>
<dt>Required parameters:</dt>
<dd><dl>
<dt>value = <em>add_amt</em> (int)</dt>
<dd>Specifies amount of life to add to the player's life bar.</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>kill = <em>kill_flag</em> (int)</dt>
<dd>If <em>kill_flag</em> is 0, then the addition will not take the player
below 1 life point. Defaults to 1.</dd>
<dt>absolute = <em>abs_flag</em> (int)</dt>
<dd>If <em>abs_flag</em> is 1, then exactly <em>add_amt</em> is added to the player's
life (the defense multiplier is ignored). Defaults to 0.</dd>
</dl>
</dd>
</dl>
    """
    result = StateController()

    set_if(result, "value", value)
    set_if(result, "kill", kill)
    set_if(result, "absolute", absolute)

    return result

@controller(value = [IntType])
def LifeSet(value: ConvertibleExpression, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>LifeSet</h2>
<p>Sets the player's life to the specified value.</p>
<dl>
<dt>Required parameters:</dt>
<dd><dl>
<dt>value = <em>life_amt</em> (int)</dt>
<dd>Specifies amount of life that the player will have after
execution.</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd>none</dd>
</dl>
    """
    result = StateController()

    set_if(result, "value", value)

    return result

@controller(pos = [IntPairType, None], pos2 = [FloatPairType, None], spacing = [IntType, None])
def MakeDust(pos: Optional[TupleExpression] = None, pos2: Optional[TupleExpression] = None, spacing: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>MakeDust</h2>
<p><strong>This controller is deprecated; use the Explod controller.</strong></p>
<p>Creates dust effects.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>pos = <em>x_pos</em>, <em>y_pos</em> (int)</dt>
<dd>Specifies the position that the dust should be drawn at, relative
to the player's axis. Defaults to 0,0.</dd>
<dt>pos2 = <em>x_pos</em>, <em>y_pos</em> (float)</dt>
<dd>Specifies the position to simultaneously draw a second dust cloud
at. If omitted, the second dust cloud is not drawn.</dd>
<dt>spacing = <em>value</em> (int)</dt>
<dd>Determines the number of frames to wait between drawing dust
clouds. For instance, spacing = 3 (the default) will draw a new
cloud of dust every third frame. spacing should be 1 or greater.</dd>
</dl>
</dd>
</dl>
    """
    result = StateController()

    set_if_tuple(result, "pos", pos, IntPairType)
    set_if_tuple(result, "pos2", pos2, FloatPairType)
    set_if(result, "spacing", spacing)

    return result

@controller(
    id = [IntType],
    pos = [FloatPairType, None],
    postype = [PosTypeT, None],
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
    alpha = [IntPairType, None],
    ignorehitpause = [BoolType, None],
    trans = [TransTypeT, None]
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
    alpha: Optional[TupleExpression] = None,
	ignorehitpause: Optional[ConvertibleExpression] = None, 
	persistent: Optional[ConvertibleExpression] = None
) -> StateController:
    """
<h2>ModifyExplod</h2>
<p>Modifies the parameters of an existing Explod. Syntax is basically
the same as Explod. However, this controller is subject to future
change. Any code relying on this controller is not guaranteed to
work in the future.</p>
    """
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
    set_if_tuple(result, "alpha", alpha, IntPairType)

    return result

@controller()
def MoveHitReset(ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>MoveHitReset</h2>
<p>Resets the movehit flag to 0. That is, after executing MoveHitReset, the triggers MoveContact, MoveGuarded, and MoveHit will all return 0.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd>none</dd>
</dl>
    """
    result = StateController()
    return result

@controller(value = [HitStringType, None], value2 = [HitStringType, None], time = [IntType, None])
def NotHitBy(value: Optional[TupleExpression] = None, value2: Optional[TupleExpression] = None, time: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>NotHitBy</h2>
<p>Temporarily specifies types of hits that are not allowed to hit the player.</p>
<dl>
<dt>Required parameters:</dt>
<dd><dl>
<dt>value = <em>attr_string</em>  OR  value2 = <em>attr_string</em></dt>
<dd>Only one of the above parameters can be specified. <em>attr_string</em>
should be a standard hit attribute string. See details.</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>time = <em>effective_time</em> (int)</dt>
<dd>Specifies the number of game ticks that these NotHitBy attributes
should be effective for. Defaults to 1.</dd>
</dl>
</dd>
<dt>Details:</dt>
<dd>The player has two hit attribute slots, which can be set using the
"value" or "value2" parameters to the NotHitBy controller. These
slots can also be set by the HitBy controller. When a slot is set,
it gets a timer (the effective time) which counts down toward zero.
If the timer has not yet reached zero, the slot is considered to be
active. The player can be hit by a HitDef only if that HitDef's
attribute appears in all currently active slots.
Using the NotHitBy controller sets the specified slot to contain all
hit attributes except those specified in the NotHitBy attribute
string.</dd>
</dl>
    """
    result = StateController()

    set_if_tuple(result, "value", value, HitStringType)
    set_if_tuple(result, "value2", value2, HitStringType)
    set_if(result, "time", time)

    return result

@controller()
def Null(ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>Null</h2>
<p>Does nothing. May be used for disabling other state controllers by changing their type to Null.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd>none</dd>
<dt>Notes:</dt>
<dd>Any triggers associated with the controller will still be evaluated.</dd>
</dl>
    """
    result = StateController()
    return result

@controller(x = [FloatType, None], y = [FloatType, None])
def Offset(x: Optional[ConvertibleExpression] = None, y: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>Offset</h2>
<p>Changes the player's display offset. The player is drawn shifted from his axis by this amount.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>x = <em>x_val</em> (float)</dt>
<dd>See below.</dd>
<dt>y = <em>y_val</em> (float)</dt>
<dd>Specifies the x and y offsets, respectively. You can specify one
or both of the optional parameters.</dd>
</dl>
</dd>
</dl>
    """
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
    """
<h2>PalFX</h2>
<p>Applies temporary effects the player's palette. These will also affect the palette of any explods and helpers the player owns, unless they have set ownpal to a nonzero value.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>time = <em>duration</em> (int)</dt>
<dd>Specifies the number of ticks that the palette effects should
last. Specify -1 to have the palette effects last indefinitely.
Specify 0 to stop any ongoing palette effects.</dd>
<dt>add = <em>add_r</em>, <em>add_g</em>, <em>add_b</em> (int, int, int)</dt>
<dd>See below.</dd>
<dt>mul = <em>mul_r</em>, <em>mul_g</em>, <em>mul_b</em> (int, int, int)</dt>
<dd>Each add component is added to the appropriate component of the
player's palette, and the result is multiplied by the appropriate
mul component divided by 256. For instance, if <em>pal_r</em> is the
red component of the character's original palette, then the new
red component is (<em>pal_r</em> + <em>add_r</em>) * <em>mul_r</em> / 256. The values for mul
must be &gt;= 0.
The defaults for these parameters are for no change,
i.e. add = 0,0,0 and mul = 256,256,256.</dd>
<dt>sinadd = ampl_r, ampl_g, ampl_b, period (int, int, int, int)</dt>
<dd>Creates an additional sine-wave palette addition effect. Period
specifies the period of the sine wave in game ticks, and the
amplitude parameters control the amplitude of the sine wave for
the respective components. For instance, if t represents the
number of ticks elapsed since the activation of the PalFX
controller, and <em>pal_r</em> is the red component of the character's
original palette, then the red component of the character's
palette at time t is
(<em>pal_r</em> + <em>add_r</em> + <em>ampl_r</em> * sin(2 * pi * t / <em>period</em>)) * <em>mul_r</em> / 256.</dd>
<dt>invertall = <em>bvalue</em> (bool)</dt>
<dd>If <em>bvalue</em> is non-zero, then the colors in the palette will be
inverted, creating a "film negative" effect. Color inversion
is applied before effects of add and mul. bvalue defaults to 0.</dd>
<dt>color = <em>value</em> (int)</dt>
<dd>This affects the color level of the palette. If value is 0,
the palette will be greyscale. If <em>value</em> is 256, there is no
change in palette. Values in between will have an intermediate
effect. This parameter's effects are applied before invertall,
add and mul. Values must be in range 0 to 256. Default value is
256.</dd>
</dl>
</dd>
</dl>
    """
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
    """
<h2>ParentVarAdd</h2>
<p>If the player is a helper, adds to one of the player's parent's working variables. Either a float variable or an int variable can be added to by this controller. If the player is not a helper, this controller does nothing.</p>
<dl>
<dt>Required parameters (int version):</dt>
<dd><dl>
<dt>v = <em>var_no</em> (int)</dt>
<dd><em>var_no</em> should evaluate to an integer between 0 and 59.</dd>
<dt>value = <em>int_expr</em> (int)</dt>
<dd><em>int_expr</em> is the value to add to the int variable indicated by
<em>var_no</em>.</dd>
</dl>
</dd>
<dt>Required parameters (float version):</dt>
<dd><dl>
<dt>fv = <em>var_no</em> (int)</dt>
<dd><em>var_no</em> should evaluate to an integer between 0 and 39.</dd>
<dt>value = <em>float_expr</em> (float)</dt>
<dd><em>float_expr</em> is the value to add to the float variable indexed by
<em>var_no</em>.</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd>none in both cases</dd>
<dt>Alternate syntax:</dt>
<dd><p>var(<em>var_no</em>) = <em>int_expr</em>  (int version)</p>
<p class="last">fvar(<em>var_no</em>) = <em>float_expr</em> (float version)</p>
</dd>
<dt>Notes:</dt>
<dd><p>Due to historical reasons, note that the alternate VarAdd
syntax listed above matches neither the syntax for variable
assignment within an expression, nor the syntax for variable
addition within an expression.</p>
<p>If you have placed P2 in a custom state through a successful hit, do
not use variable assignment within the custom states. Otherwise, you
will overwrite P2's parent's variables, which can cause unintended
malfunction of the opponent player.</p>
<dl class="last docutils">
<dt>Warning:  System variables (sysvar, sysfvar) cannot be used within this</dt>
<dd>controller.</dd>
</dl>
</dd>
</dl>
    """
    result = StateController()

    if var != None:
        set_if(result, var.exprn, value)

    return result

@controller(var = [IntType, FloatType, None], value = [IntType, FloatType, None])
def ParentVarSet(var: Optional[Expression] = None, value: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>ParentVarSet</h2>
<p>If the player is a helper, sets one of the parent's working variables. Either a float variable or an int variable can be set by this controller. Does nothing if the player is not a helper.</p>
<dl>
<dt>Required parameters (int version):</dt>
<dd><dl>
<dt>v = <em>var_no</em> (int)</dt>
<dd><em>var_no</em> should evaluate to an integer between 0 and 59.</dd>
<dt>value = <em>int_expr</em> (int)</dt>
<dd><em>int_expr</em> is the value to assign to the int variable indicated by
<em>var_no</em>.</dd>
</dl>
</dd>
<dt>Required parameters (float version):</dt>
<dd><dl>
<dt>fv = <em>var_no</em> (int)</dt>
<dd><em>var_no</em> should evaluate to an integer between 0 and 39.</dd>
<dt>value = <em>float_expr</em> (float)</dt>
<dd><em>float_expr</em> is the value to assign to the float variable indexed by
<em>var_no</em>.</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd>none in both cases</dd>
<dt>Alternate syntax:</dt>
<dd><p>var(<em>var_no</em>) = <em>int_expr</em>  (int version)</p>
<p class="last">fvar(<em>var_no</em>) = <em>float_expr</em> (float version)</p>
</dd>
<dt>Notes:</dt>
<dd><p>Due to historical reasons, note that the alternate variable
assignment syntax listed above does not exactly match the syntax for
variable assignment within an expression.</p>
<p>If you have placed P2 in a custom state through a successful hit, do
not use variable assignment within the custom states. Otherwise, you
will overwrite P2's parent's variables, which can cause unintended
malfunction of the opponent player.</p>
<dl class="last docutils">
<dt>Warning:  System variables (sysvar, sysfvar) cannot be used within this</dt>
<dd>controller.</dd>
</dl>
</dd>
</dl>
    """
    result = StateController()

    if var != None:
        set_if(result, var.exprn, value)

    return result

@controller(time = [IntType], endcmdbuftime = [IntType, None], movetime = [IntType, None], pausebg = [BoolType, None])
def Pause(time: ConvertibleExpression, endcmdbuftime: Optional[ConvertibleExpression] = None, movetime: Optional[ConvertibleExpression] = None, pausebg: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>Pause</h2>
<p>Pauses the game for the specified amount of time. Player and background updates are not carried out during this time.</p>
<dl>
<dt>Required parameters:</dt>
<dd><dl>
<dt>time = <em>t</em> (int)</dt>
<dd>This is the number of game ticks to pause for.
Valid values for <em>t</em> are all positive numbers, starting
from 0.</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>endcmdbuftime = <em>bt</em> (int)</dt>
<dd>This is the number of ticks during the end of the pause in which the player's move commands will be buffered. Buffered commands will be detected by the "command" trigger immediately after the pause ends. The buffering applies only to players who are unable to move during the pause (see movetime parameter). Valid values for endcmdbuftime are from 0 to <em>t</em>, where <em>t</em> is the value of the time parameter. Defaults to 0.</dd>
<dt>movetime = <em>mt</em> (int)</dt>
<dd>This is the number of ticks during the start of the pause in which
the player is allowed to move. Collision detection is carried out
during this time, so it is possible to hit other players.
Valid values for <em>mt</em> are from 0 to <em>t</em>, where <em>t</em> is the value of
the time parameter. Defaults to 0.</dd>
<dt>pausebg = <em>p</em> (boolean)</dt>
<dd>If set to 1, the background is stopped during the pause. If 0, the background continues updating during the pause. Defaults to 1.</dd>
</dl>
</dd>
<dt>Notes:</dt>
<dd>Executing a Pause controller during the pausetime of another
will cancel out the effect of the previous Pause controller.
Executing a Pause during a superpause will delay the effects
of the pause until after the superpause has ended.</dd>
</dl>
    """
    result = StateController()

    set_if(result, "time", time)
    set_if(result, "endcmdbuftime", endcmdbuftime)
    set_if(result, "movetime", movetime)
    set_if(result, "pausebg", pausebg)

    return result

@controller(value = [BoolType])
def PlayerPush(value: ConvertibleExpression, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>PlayerPush</h2>
<p>Disables the player's push checking for one tick. Push checking keeps players from overlapping one another. By temporarily disabling push checking, dodge-type moves in which the player passes through another (but can still be hit) can be implemented.</p>
<dl>
<dt>Required parameters:</dt>
<dd><dl>
<dt>value = <em>push_flag</em> (boolean)</dt>
<dd>If <em>push_flag</em> is nonzero, then push checking is enabled. If
<em>push_flag</em> is zero, then push checking is disabled.</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd>none</dd>
</dl>
    """
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
    """
<h2>PlaySnd</h2>
<p>Plays back a sound.</p>
<dl>
<dt>Required parameters:</dt>
<dd><dl>
<dt>value = <em>group_no</em>, <em>sound_no</em> (int, int)</dt>
<dd><em>group_no</em> and <em>sound_no</em> correspond to the identifying pair
that you assigned each sound in the player's snd file.
To play back a sound from "common.snd", precede group_no
with an "F".</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>volumescale = <em>volume_scale</em> (float)</dt>
<dd><em>volume_scale</em> controls the volume of the sound. A value of 100
specifies 100% volume, 50 for 50%, and so on. Valid values are from
0 to 100. Defaults to 100.</dd>
<dt>channel = <em>channel_no</em> (int)</dt>
<dd><em>channel_no</em> specifies which of the player's sound channels
the sound should play on. Only one voice may play on a particular
channel at a time. For example, if you play a sound on channel 2,
then play any sound on the same channel before the first sound is
done, then by default the first sound is stopped as the second one
plays. 0 is a special channel reserved for player voices. Channel
0 voices are stopped when the player is hit. It's recommended you
play your character's voice sounds on channel 0.
If omitted, <em>channel_no</em> defaults to -1, meaning the sound will play
on any free channel.</dd>
<dt>lowpriority = <em>pr</em> (int)</dt>
<dd>This is only valid if the channel is not -1. If <em>pr</em> is nonzero,
then a sound currently playing on this sound's channel (from a
previous PlaySnd call) cannot be interrupted by this sound.</dd>
<dt>freqmul = <em>f</em> (float)</dt>
<dd>The sound frequency will be multiplied by <em>f</em>. For example. Setting <em>f</em> to 1.1
will result in a higher-pitched sound. Defaults to 1.0 (no change
in frequency).</dd>
<dt>loop = <em>loop_flag</em> (int)</dt>
<dd>Set <em>loop_flag</em> to a nonzero value to have the sound sample loop
over and over. Defaults to 0.</dd>
<dt>pan = <em>p</em> (int)</dt>
<dd>This is the positional offset of the sound, measured in pixels.
If <em>p</em> &gt; 0, then the sound is offset to the front of the player.
If <em>p</em> &lt; 0, then sound is offset to the back.
Defaults to 0.
This parameter is mutually exclusive with abspan.</dd>
<dt>abspan = <em>p</em> (int)</dt>
<dd>Like pan, except the sound is panned from the center of the
screen, not from the player's position.
This parameter is mutually exclusive with pan.</dd>
</dl>
</dd>
</dl>
<p>Notes:</p>
<blockquote>
Prior to version 1.0 RC8, a volume parameter was used instead of
volumescale. The volume parameter is no longer supported and is
now ignored.</blockquote>
    """
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
    """
<h2>PosAdd</h2>
<p>Offsets the player's position by the specified amounts. The X coordinate is relative to the player's axis, with positive values moving in the direction that the player is facing. The Y coordinate
is relative to the player's axis, with negative values moving up.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>x = <em>x_value</em> (float)</dt>
<dd>Moves the player <em>x_value</em> pixels forward. Defaults to 0.</dd>
<dt>y = <em>y_value</em> (float)</dt>
<dd>Moves the player <em>y_value</em> pixels downwards. Defaults to 0.</dd>
</dl>
</dd>
</dl>
    """
    result = StateController()

    set_if(result, "x", x)
    set_if(result, "y", y)

    return result

@controller(value = [BoolType, None])
def PosFreeze(value: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>PosFreeze</h2>
<p>Temporarily freezes the player's position.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>value = <em>freeze_flag</em> (boolean)</dt>
<dd>If <em>freeze_flag</em> is non-zero, the player's position will be frozen,
else it will not be. Defaults to 1.</dd>
</dl>
</dd>
</dl>
    """
    result = StateController()

    set_if(result, "value", value)

    return result

@controller(x = [FloatType, None], y = [FloatType, None])
def PosSet(x: Optional[ConvertibleExpression] = None, y: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>PosSet</h2>
<p>Sets the player's position to the specified coordinates. The X coordinate is relative to the center of the screen, with positive values moving right. The Y coordinate is relative to the floor, with negative values moving up.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>x = <em>x_value</em> (float)</dt>
<dd>Specifies the new x-position of the player.</dd>
<dt>y = <em>y_value</em> (float)</dt>
<dd>Specifies the new y-position of the player.</dd>
</dl>
</dd>
</dl>
    """
    result = StateController()

    set_if(result, "x", x)
    set_if(result, "y", y)

    return result

@controller(value = [IntType])
def PowerAdd(value: ConvertibleExpression, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>PowerAdd</h2>
<p>Adds the specified amount to the player's power.</p>
<dl>
<dt>Required parameters:</dt>
<dd><dl>
<dt>value = <em>add_amt</em> (int)</dt>
<dd><em>add_amt</em> is the number to add to the player's power.</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd>none</dd>
</dl>
    """
    result = StateController()

    set_if(result, "value", value)

    return result

@controller(value = [IntType])
def PowerSet(value: ConvertibleExpression, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>PowerSet</h2>
<p>Sets the amount of power that the player has.</p>
<dl>
<dt>Required parameters:</dt>
<dd><dl>
<dt>value = <em>pow_amt</em> (int)</dt>
<dd><em>pow_amt</em> is the new value to set the player's power to.</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd>none</dd>
</dl>
    """
    result = StateController()

    set_if(result, "value", value)

    return result

@controller(
    projid = [IntType, None],
    projanim = [IntType, None],
    projhitanim = [IntType, None],
    projremanim = [IntType, None],
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
    postype = [PosTypeT, None],
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
    afterimage_trans = [TransTypeT, None],
    attr = [HitStringType],
    hitflag = [HitFlagTypeF, None],
    guardflag = [GuardFlagTypeF, None],
    affectteam = [TeamTypeT, None],
    animtype = [HitAnimTypeT, None],
    air_animtype = [HitAnimTypeT, None],
    fall_animtype = [HitAnimTypeT, None],
    priority = [PriorityPairType, None],
    damage = [IntPairType, None],
    pausetime = [IntPairType, None],
    guard_pausetime = [IntPairType, None],
    sparkno = [SpriteType, IntType, None],
    guard_sparkno = [SpriteType, IntType, None],
    sparkxy = [IntPairType, None],
    hitsound = [SoundPairType, None],
    guardsound = [SoundPairType, None],
    ground_type = [AttackTypeT, None],
    air_type = [AttackTypeT, None],
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
def Projectile(
    attr: TupleExpression,
    projid: Optional[ConvertibleExpression] = None,
    projanim: Optional[ConvertibleExpression] = None,
    projhitanim: Optional[ConvertibleExpression] = None,
    projremanim: Optional[ConvertibleExpression] = None,
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
    p1stateno: Optional[Union[Expression, str, int, Callable[..., None | StateController]]] = None,
    p2stateno: Optional[Union[Expression, str, int, Callable[..., None | StateController]]] = None,
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
    """
<h2>Projectile</h2>
<p>Creates a projectile for the player. The Projectile controller takes all the parameters of the HitDef controller, which control the HitDef for the projectile. In addition, Projectile has the following additional parameters:</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>ProjID = <em>id_no</em> (int)</dt>
<dd>Specifies an ID number to refer to this projectile by. Should be
positive, if specified.</dd>
<dt>projanim = <em>anim_no</em> (int)</dt>
<dd>Specifies the animation action number to use for the projectile's
animation. Defaults to 0 if omitted.</dd>
<dt>projhitanim = <em>anim_no</em> (int)</dt>
<dd>Specifies the animation action number to play when the projectile
hits the opponent. Defaults to -1 (no change in animation) if
omitted.</dd>
<dt>projremanim = <em>anim_no</em> (int)</dt>
<dd>Specifies the animation action number to play when the projectile
is removed (due to its time expiring or hitting the its removal
boundaries, etc.) If omitted, projhitanim is used instead.</dd>
<dt>projcancelanim = <em>anim_no</em> (int)</dt>
<dd>Specifies the animation action number to play when the projectile
is cancelled by hitting another projectile. If omitted,
projremanim is used instead.</dd>
<dt>projscale = <em>x_scale</em>, <em>y_scale</em> (float, float)</dt>
<dd>Specifies the scale factor of the projectile. The final scale of
the projectile is affected by both this parameter and the
"proj.doscale" parameter in the [Size] group of p1's constants
file. Defaults to 1,1 (normal size) if omitted.</dd>
<dt>projremove = <em>remove_flag</em> (boolean)</dt>
<dd>Set to a non-zero value to have the projectile be removed after it
hits, or to 0 to disable this behavior. Defaults to 1.</dd>
<dt>projremovetime = <em>remove_time</em> (int)</dt>
<dd>Specifies the number of ticks after which the projectile should be
removed from the screen. If -1, the projectile will not be removed.
Defaults to -1.</dd>
<dt>velocity = <em>x_vel</em>, <em>y_vel</em> (float, float)</dt>
<dd>Specifies the initial x and y velocities for the projectile to
travel at. Defaults to 0,0 if omitted.</dd>
<dt>remvelocity = <em>x_vel</em>, <em>y_vel</em> (float, float)</dt>
<dd>Specifies the x and y velocities at which the projectile should
travel while being removed. Defaults to 0,0 if omitted.</dd>
<dt>accel = <em>x_accel</em>, <em>y_accel</em> (float, float)</dt>
<dd>Specifies the acceleration to apply to the projectile in the x and
y directions. Defaults to 0,0 if omitted.</dd>
<dt>velmul = <em>x_mul</em>, <em>y_mul</em> (float, float)</dt>
<dd>Specifies x and y velocity multipliers. The projectile's velocity
is multiplied by these multipliers on every tick. The multipliers
default to 1 if omitted.</dd>
<dt>projhits = <em>num_hits</em> (int)</dt>
<dd>Specifies the number of hits that the projectile can impart on
an opponent before it is removed. Defaults to 1.</dd>
<dt>projmisstime = <em>miss_time</em> (int)</dt>
<dd>If the projectile is configured for multiple hits, <em>miss_time</em> specifies the number
of ticks after each hit before the projectile can hit again. Defaults to 0.</dd>
<dt>projpriority = <em>proj_priority</em> (int)</dt>
<dd>Specifies the projectile priority. If the projectile collides with
another projectile of equal priority, they will cancel. If it
collides with another of lower priority, it will cancel the lower-
priority projectile, and the higher-priority one will have its
priority decreased by 1.
Defaults to 1.</dd>
<dt>projsprpriority = <em>priority</em> (int)</dt>
<dd>Specifies the sprite priority of the projectile. Higher-priority
sprites are drawn on top of lower-priority sprites. Defaults to 3.</dd>
<dt>projedgebound = <em>value</em> (int)</dt>
<dd>Specifies the distance off the edge of the screen before
the projectile is automatically removed. Units are in pixels.
Defaults to 40 in 240p, 80 in 480p, 160 in 720p.</dd>
<dt>projstagebound = <em>value</em> (int)</dt>
<dd>Specifies the greatest distance the projectile can travel off the
edge of the stage before being it is automatically removed.
Defaults to 40 in 240p, 80 in 480p, 160 in 720p.</dd>
<dt>projheightbound = <em>lowbound</em>, <em>highbound</em> (int, int)</dt>
<dd>Specifies the least and greatest y values the projectile is
allowed to reach. If the projectile leaves these boundaries, it is
automatically removed. Note: since y values decrease with increasing height on
the screen, lowbound actually specifies the greatest height the
projectile can attain.
<em>lowbound</em> defaults to -240 in 240p, -480 in 480p, -960 in 720p.
<em>highbound</em> defaults to 1 in 240p, 2 in 480p, 4 in 720p.</dd>
<dt>offset = <em>off_x</em>, <em>off_y</em> (int, int)</dt>
<dd>Specifies the x and y offsets at which the projectile should be
created. Both parameters default to 0 if omitted.
Projectiles are always created facing the same direction as
the player.  <em>off_x</em> is in relation to the direction the projectile
is facing.
The exact behavior of the offset parameters is dependent on the postype.</dd>
<dt>postype = <em>postype_string</em> (string)</dt>
<dd><p><em>postype_string</em> specifies the postype -- how to interpret the pos
parameters.
In all cases, a positive y offset means a downward displacement.
In all cases, <em>off_y</em> is relative to the position of the player.</p>
<p>Valid values for <em>postype_string</em> are the following:</p>
<dl class="last docutils">
<dt>p1</dt>
<dd>Interprets offset relative to p1's axis. A positive <em>off_x</em> is
toward the front of p1. This is the default value for postype.</dd>
<dt>p2</dt>
<dd>Interprets offset relative to p2's axis. A positive <em>off_x</em> is
toward the front of p1.  If p2 does not exist, the position is
calculated with respect to p1 and a warning is logged.</dd>
<dt>front</dt>
<dd>Interprets <em>off_x</em> relative to the edge of the screen that p1 is
facing toward. A positive <em>off_x</em> is toward the front of p1.</dd>
<dt>back</dt>
<dd>Interprets <em>off_x</em> relative to the edge of the screen that p1 is
facing away from. A positive <em>off_x</em> is toward the front of p1.</dd>
<dt>left</dt>
<dd>Interprets <em>off_x</em> relative to the left edge of
the screen. A positive <em>off_x</em> is toward the front of p1.</dd>
<dt>right</dt>
<dd>Interprets <em>off_x</em> relative to the right edge of
the screen. A positive <em>off_x</em> is toward the front of p1.</dd>
</dl>
</dd>
<dt>projshadow = <em>shadow</em> (int)</dt>
<dd>If <em>shadow</em> is not 0, a shadow will be drawn for the explod,
else no shadow will be drawn.  Defaults to 0.</dd>
<dt>supermovetime = <em>move_time</em> (int)</dt>
<dd>Specifies the number of ticks that the projectile will be
unfrozen during a SuperPause. Defaults to 0.</dd>
<dt>pausemovetime = <em>move_time</em> (int)</dt>
<dd>Specifies the number of ticks that the projectile will be
unfrozen during a Pause. Defaults to 0.</dd>
<dt>ownpal = <em>ownpal_flag</em> (boolean)</dt>
<dd><p>If <em>ownpal_flag</em> is 0, the projectile will be affected by subsequent
execution of its owner's PalFX and RemapPal controllers. This
is the default.</p>
<p class="last">If <em>ownpal_flag</em> is 1, the projectile will not be affected by its
owner's PalFX and RemapPal controllers.</p>
</dd>
<dt>remappal = <em>dst_pal_grp</em>, <em>dst_pal_item</em> (int, int)</dt>
<dd>Forces a palette remap of the projectile's indexed-color sprites to the specified palette.
This parameter is used only if <em>ownpal_flag</em> is non-zero.
If <em>dst_pal_grp</em> is -1, this parameter will be ignored.
Defaults to -1, 0.</dd>
<dt>afterimage.time = <em>aftimg_time</em> (int)</dt>
<dd>See below.</dd>
<dt>afterimage.length</dt>
<dd>See below.</dd>
<dt>afterimage....</dt>
<dd>If included, these parameters add afterimage effects to the projectile.
The parameters are the same as in the AfterImage controller,
except these are all prepended with "afterimage."</dd>
</dl>
</dd>
<dt>Notes:</dt>
<dd><p>All projectiles created by helpers immediately become owned by the root.</p>
<p class="last">The behavior of a projectile's HitDef is undefined when executed from a
[Statedef -2] block while the player has another player's
state and animation data.</p>
</dd>
</dl>
    """
    result = StateController()

    set_if(result, "projid", projid)
    set_if(result, "projanim", projanim)
    set_if(result, "projhitanim", projhitanim)
    set_if(result, "projremanim", projremanim)
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

    ## from HitDef
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

@controller(source = [IntPairType], dest = [IntPairType])
def RemapPal(source: TupleExpression, dest: TupleExpression, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>RemapPal</h2>
<p>Changes one of the player's palettes to another.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>source = <em>src_pal_grp</em>, <em>src_pal_item</em></dt>
<dd>See below.</dd>
<dt>dest = <em>dst_pal_grp</em>, <em>dst_pal_item</em></dt>
<dd><p>All of the player sprites that use the source palette will be drawn using the dest palette instead.
The source and dest palettes must exist within the player's sprites, and both must be of the same color depth.</p>
<p>If <em>src_pal_grp</em> is -1, all indexed-color sprites will be remapped to the dest palette.
This only affects sprites of the same color depth as the dest palette.
All other existing mappings will be removed.</p>
<p>If <em>dst_pal_grp</em> is -1, the mapping for the source is removed.
Setting the dest pair to the same values as the source pair has the same effect.</p>
<p class="last">The default value for source is -1,0.
The default value for dest is -1,0.</p>
</dd>
</dl>
</dd>
<dt>Notes:</dt>
<dd><p>Palette mappings are not transitive; i.e. mapping 1,0 to 2,0 and 2,0 to 3,0
will not map 1,0 to 3,0.</p>
<p class="last">In 1.1 and newer, each player is allowed up to 8 different palette mappings
at the same time.
Subsequent calls of RemapPal will fail if the source pair is not already
being mapped.  Unused mappings can be removed by setting <em>dst_pal_grp</em> to -1
for a given source pair.</p>
</dd>
</dl>
    """
    result = StateController()

    set_if_tuple(result, "source", source, IntPairType)
    set_if_tuple(result, "dest", dest, IntPairType)

    return result

@controller(id = [IntType, None])
def RemoveExplod(id: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>RemoveExplod</h2>
<p>Removes all of a player's explods, or just the explods with a specified ID number.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>ID = <em>remove_id</em> (int)</dt>
<dd><em>remove_id</em> is the ID number of the explods to remove. If omitted,
removes all explods owned by the player.</dd>
</dl>
</dd>
</dl>
    """
    result = StateController()

    set_if(result, "id", id)

    return result

@controller(
    reversal_attr = [HitStringType],
    hitflag = [HitFlagTypeF, None],
    pausetime = [IntPairType, None],
    sparkno = [SpriteType, IntType, None],
    guard_sparkno = [SpriteType, IntType, None],
    sparkxy = [IntPairType, None],
    hitsound = [SoundPairType, None],
    guardsound = [SoundPairType, None],
    p1stateno = [IntType, None],
    p2stateno = [IntType, None],
    p1sprpriority = [IntType, None],
    p2sprpriority = [IntType, None]
)
def ReversalDef(
    reversal_attr: TupleExpression, 
    hitflag: Optional[ConvertibleExpression] = None,
    pausetime: Optional[TupleExpression] = None, 
    sparkno: Optional[ConvertibleExpression] = None,
    guard_sparkno: Optional[ConvertibleExpression] = None, 
    hitsound: Optional[TupleExpression] = None, 
    guardsound: Optional[TupleExpression] = None, 
    p1stateno: Optional[Union[Expression, str, int, Callable[..., None | StateController]]] = None, 
    p2stateno: Optional[Union[Expression, str, int, Callable[..., None | StateController]]] = None, 
    p1sprpriority: Optional[ConvertibleExpression] = None, 
    p2sprpriority: Optional[ConvertibleExpression] = None, 
    sparkxy: Optional[TupleExpression] = None, 
	ignorehitpause: Optional[ConvertibleExpression] = None, 
	persistent: Optional[ConvertibleExpression] = None
) -> StateController:
    """
<h2>ReversalDef</h2>
<p>Defines a reversal. If one of P2's Clns1 boxes comes in contact with one of P1's Clsn1 boxes and a ReversalDef is active, then P1 will reverse P2's attack. Use with p1stateno (and optionally p2stateno) for creating reversal attacks.</p>
<p>ReversalDefs take the HitDef parameters pausetime, sparkno, hitsound, p1stateno, and p2stateno, plus:</p>
<dl>
<dt>Required parameters:</dt>
<dd><dl>
<dt>reversal.attr = <em>attr_string</em></dt>
<dd><em>attr_string</em> specifies the list of attack attributes that can be
reversed by this ReversalDef. It is a standard hit attribute
string. For instance,
<tt class="docutils literal">reversal.attr = SA,NA,SA</tt>
means stand+air, normal attack, special attack.</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd>none</dd>
<dt>Notes:</dt>
<dd>The sparkxy parameter is treated as an offset to P2's hitdef's sparkxy. The MoveHit trigger can be used to detect if P1 successfully reversed P2.</dd>
</dl>
    """
    result = StateController()

    set_if_tuple(result, "reversal.attr", reversal_attr, HitStringType)
    set_if(result, "hitflag", hitflag)
    set_if_tuple(result, "pausetime", pausetime, IntPairType)
    set_if(result, "sparkno", sparkno)
    set_if(result, "guard.sparkno", guard_sparkno)
    set_if_tuple(result, "hitsound", hitsound, IntPairType)
    set_if_tuple(result, "guardsound", guardsound, IntPairType)
    set_stateno(result, "p1stateno", p1stateno)
    set_stateno(result, "p2stateno", p2stateno)
    set_if(result, "p1sprpriority", p1sprpriority)
    set_if(result, "p2sprpriority", p2sprpriority)
    set_if_tuple(result, "sparkxy", sparkxy, IntPairType)

    return result

@controller(value = [BoolType, None], movecamera = [BoolPairType, None])
def ScreenBound(value: Optional[ConvertibleExpression] = None, movecamera: Optional[TupleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>ScreenBound</h2>
<p>Specifies whether or not the player's movement should be constrained to the screen or not. Also determines whether the camera should move to follow the player or not. The results of this controller are valid for 1 tick.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>value = <em>bound_flag</em> (boolean)</dt>
<dd>If <em>bound_flag</em> is 0, the player will be allowed to move off the
screen. If 1, the player is constrained within the screen. Defaults to 0 if omitted.</dd>
<dt>movecamera = <em>move_x_flag</em>, <em>move_y_flag</em> (boolean, boolean)</dt>
<dd>If 1, specifies that camera should pan to follow the player in
the x direction and in the y direction, respectively. Defaults to
0 in both instances if omitted.</dd>
</dl>
</dd>
</dl>
    """
    result = StateController()

    set_if(result, "value", value)
    set_if_tuple(result, "movecamera", movecamera, BoolPairType)

    return result

@controller(value = [StateNoType, StringType, IntType], ctrl = [BoolType, None], anim = [IntType, None])
def SelfState(value: ConvertibleExpression, ctrl: Optional[ConvertibleExpression] = None, anim: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>SelfState</h2>
<p>Like ChangeState, except that this changes a player back to a state in his own state data. Use this when you have placed an opponent player in a custom state via an attack, and wish to restore the opponent to his own states.</p>
    """
    result = StateController()

    set_if(result, "value", value)
    set_if(result, "ctrl", ctrl)
    set_if(result, "anim", anim)

    return result

@controller(value = [IntType])
def SprPriority(value: ConvertibleExpression, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>SprPriority</h2>
<p>Changes the player's sprite priority. Higher-priority sprites are drawn on top of lower-priority sprites.</p>
<dl>
<dt>Required arguments:</dt>
<dd><dl>
<dt>value = <em>priority_level</em> (int)</dt>
<dd>Valid values are -5 to 5.</dd>
</dl>
</dd>
<dt>Optional arguments:</dt>
<dd>none</dd>
</dl>
    """
    result = StateController()

    set_if(result, "value", value)

    return result

@controller(statetype = [StateTypeT, None], movetype = [MoveTypeT, None], physics = [PhysicsTypeT, None])
def StateTypeSet(statetype: Optional[ConvertibleExpression] = None, movetype: Optional[ConvertibleExpression] = None, physics: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>StateTypeSet</h2>
<p>Changes the current state type and move type. Useful for states that go from the ground into the air, etc.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>statetype = <em>state_type</em> (string)</dt>
<dd>Set <em>state_type</em> to A for air, C for crouch, S for stand, or L
for liedown. Defaults to no change.</dd>
<dt>movetype = <em>move_type</em> (string)</dt>
<dd>Set <em>move_type</em> to I for idle, A for attack, or H for gethit.
Defaults to no change.</dd>
<dt>physics = <em>physics</em> (string)</dt>
<dd>Set <em>physics</em> to A for air, C for crouch, S for stand, or N
for none. Defaults to no change.</dd>
</dl>
</dd>
</dl>
    """
    result = StateController()

    set_if(result, "statetype", statetype)
    set_if(result, "movetype", movetype)
    set_if(result, "physics", physics)

    return result

@controller(channel = [IntType], pan = [IntType], abspan = [IntType])
def SndPan(channel: ConvertibleExpression, pan: ConvertibleExpression, abspan: ConvertibleExpression, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>SndPan</h2>
<p>Changes the panning of a currently playing sound. This controller may be continually triggered to smoothly move a sound across the sound field or to have a sound follow the player.</p>
<dl>
<dt>Required parameters:</dt>
<dd><dl>
<dt>channel = <em>chan_no</em> (int)</dt>
<dd>Specifies the channel number of the sound to pan.</dd>
<dt>pan = <em>p</em> OR abspan = <em>p</em> (int)</dt>
<dd>These parameters cannot both be specified at the same time. p
determines the sound offset in pixels from the player (in the
case of pan) or from the center of the screen (in the case of
abspan). See PlaySnd for a description of the panning parameters.</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd>none</dd>
</dl>
    """
    result = StateController()

    set_if(result, "channel", channel)
    set_if(result, "pan", pan)
    set_if(result, "abspan", abspan)

    return result

@controller(channel = [IntType])
def StopSnd(channel: ConvertibleExpression, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>StopSnd</h2>
<p>Stops any sound which is playing on the specified channel.</p>
<dl>
<dt>Required parameters:</dt>
<dd><dl>
<dt>channel = <em>chan_no</em> (int)</dt>
<dd>Stops playback of any sound on <em>chan_no</em>. If <em>chan_no</em> is -1, then all
sounds are stopped, including those belonging to other players.</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd>none</dd>
</dl>
    """
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
    """
<h2>SuperPause</h2>
<p>Freezes the gameplay and darkens the screen. While each player is frozen, no time passes for them. Use for a dramatic pause during the start of hyper attacks.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd><p>SuperPause accepts all optional parameters that the Pause controller does. In addition, SuperPause also takes the following parameters:</p>
<dl class="last docutils">
<dt>time = <em>pause_time</em> (int)</dt>
<dd>Specifies the number of ticks that the pause should last. Default
is 30 ticks (half a second at default speed).</dd>
<dt>anim = <em>anim_no</em> (int)</dt>
<dd>Specifies the animation number (from fightfx.air) to play during the
SuperPause. The default is 30, which is a charging effect. If anim
is -1, no animation will be played. If you prepend "S" to <em>anim_no</em>,
the animation used will be from the player's AIR file. For example,
<tt class="docutils literal">anim = S10</tt>.</dd>
<dt>sound = <em>snd_grp</em>, <em>snd_no</em> (int, int)</dt>
<dd>Specifies a sound to play (from common.snd) during SuperPause. The default
is -1, which means no sound is played. If you prepend "S" to
<em>snd_grp</em>, then the sound used will be from the player's own SND
file. For example, <tt class="docutils literal">sound = S10,0</tt>.</dd>
<dt>pos = <em>x_pos</em>, <em>y_pos</em> (float)</dt>
<dd>Specifies the offset (from the player axis) at which the super
anim is to be displayed. Defaults to 0,0.</dd>
<dt>darken = <em>bvalue</em> (boolean)</dt>
<dd>If this is 1, the screen will darken during the SuperPause.
Set this to 0 to disable this effect. The default value is 1.</dd>
<dt>p2defmul = <em>def_mul</em> (float)</dt>
<dd>This is the amount in which to temporarily multiply the defence of
any targets the player has. This is used to make chaining into
supers less damaging. Setting this at 1 will make no changes
to the targets' defence. 0 is a special value that will set the
defence to the number set in Super.TargetDefenceMul in the [Rules]
section of mugen.cfg. The default value is 0. Valid values are all
positive numbers, including zero.</dd>
<dt>poweradd = <em>value</em> (int)</dt>
<dd>This is the amount to add to the player's power. Defaults to 0.</dd>
<dt>unhittable = <em>bvalue</em> (boolean)</dt>
<dd>If set to 1, the player cannot be hit during the SuperPause. Set to
0 to disable this. Defaults to 1.</dd>
</dl>
</dd>
<dt>Notes:</dt>
<dd>If the Pause controller was previously executed, and the action is
still paused, executing a SuperPause will preempt the Pause
controller's effects. During the SuperPause, the time left until
the Pause controller's effects expires will not count down.</dd>
</dl>
    """
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
    """
<h2>TargetBind</h2>
<p>Binds the player's specified targets to a specified location relative to the player's axis.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>time = <em>bind_time</em> (int)</dt>
<dd>Specifies number of ticks that this binding should be in effect.
Defaults to 1.</dd>
<dt>ID = <em>bind_id</em> (int)</dt>
<dd>Specifies the desired target ID to bind. Only targets with this
target ID will be bound. Defaults to -1 (bind all targets.)</dd>
<dt>pos = <em>x_pos</em>, <em>y_pos</em> (float)</dt>
<dd>Specifies the offset from the player's axis to bind the target to.
Defaults to 0,0 if omitted.</dd>
</dl>
</dd>
</dl>
    """
    result = StateController()

    set_if(result, "time", time)
    set_if(result, "id", id)
    set_if_tuple(result, "pos", pos, FloatPairType)

    return result

@controller(excludeid = [IntType, None], keepone = [BoolType, None])
def TargetDrop(excludeid: Optional[ConvertibleExpression] = None, keepone: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>TargetDrop</h2>
<p>Drops all targets from the player's target list, except possibly for those having a specified target ID number. Useful for applying effects to only certain targets.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>excludeID = <em>id_no</em> (int)</dt>
<dd>Any targets with target ID number not equal to id_no will be
dropped from the player's target list. Defaults to -1 (drop all
targets).</dd>
<dt>keepone = <em>keep_flag</em> (boolean)</dt>
<dd>If <em>keep_flag</em> is non-zero, then at most one target is kept on the
player's target list. If there are multiple targets whose target
ID number is the same as id_no, one will be picked at random and
the rest will be dropped. This behavior is useful in throws, to
keep from throwing multiple opponents simultaneously. If <em>keep_flag</em> is
0, then all targets with the appropriate ID number will be kept.
<em>keep_flag</em> defaults to 1.</dd>
</dl>
</dd>
</dl>
    """
    result = StateController()

    set_if(result, "excludeid", excludeid)
    set_if(result, "keepone", keepone)

    return result

@controller(value = [IntType], id = [IntType, None])
def TargetFacing(value: ConvertibleExpression, id: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>TargetFacing</h2>
<p>Turns all targets to face a specified direction relative to the player.</p>
<dl>
<dt>Required parameters:</dt>
<dd><dl>
<dt>value = <em>facing_val</em> (int)</dt>
<dd>If <em>facing_val</em> is positive, all targets will turn to face the same
direction as the player. If <em>facing_val</em> is negative, all targets
will turn to face the opposite direction as the player.</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>ID = <em>target_id</em> (int)</dt>
<dd>Specifies the desired target ID to affect. Only targets with this
target ID will be affected. Defaults to -1 (affects all targets.)</dd>
</dl>
</dd>
</dl>
    """
    result = StateController()

    set_if(result, "value", value)
    set_if(result, "id", id)

    return result

@controller(value = [IntType], id = [IntType, None], kill = [BoolType, None], absolute = [BoolType, None])
def TargetLifeAdd(value: ConvertibleExpression, id: Optional[ConvertibleExpression] = None, kill: Optional[ConvertibleExpression] = None, absolute: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>TargetLifeAdd</h2>
<p>Adds the specified amount to all targets' life, scaled by the targets' defense multipliers if necessary.</p>
<dl>
<dt>Required parameters:</dt>
<dd><dl>
<dt>value = <em>add_amt</em> (int)</dt>
<dd><em>add_amt</em> is added toe ach target's life.</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>ID = <em>target_id</em> (int)</dt>
<dd>Specifies the desired target ID to affect. Only targets with this
target ID will be affected. Defaults to -1 (affects all targets.)</dd>
<dt>kill = <em>kill_flag</em> (boolean)</dt>
<dd>If kill_flag is 0, then the addition will not take any player
below 1 life point. Defaults to 1.</dd>
<dt>absolute = <em>abs_flag</em> (boolean)</dt>
<dd>If <em>abs_flag</em> is 1, then <em>add_amt</em> will not be scaled (i.e. attack and
defense multipliers will be ignored). Defaults to 0.</dd>
</dl>
</dd>
</dl>
    """
    result = StateController()

    set_if(result, "value", value)
    set_if(result, "id", id)
    set_if(result, "kill", kill)
    set_if(result, "absolute", absolute)

    return result

@controller(value = [IntType], id = [IntType, None])
def TargetPowerAdd(value: ConvertibleExpression, id: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>TargetPowerAdd</h2>
<p>Adds the specified amount to all targets' power.</p>
<dl>
<dt>Required parameters:</dt>
<dd><dl>
<dt>value = <em>add_amt</em> (int)</dt>
<dd><em>add_amt</em> is added to each target's power.</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>ID = <em>target_id</em> (int)</dt>
<dd>Specifies the desired target ID to affect. Only targets with this
target ID will be affected. Defaults to -1 (affects all targets.)</dd>
</dl>
</dd>
</dl>
    """
    result = StateController()

    set_if(result, "value", value)
    set_if(result, "id", id)

    return result

@controller(value = [StateNoType, StringType, IntType], id = [IntType, None])
def TargetState(value: Union[Expression, str, int, Callable[..., None | StateController]], id: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>TargetState</h2>
<p>Makes all targets change to the specified state number.</p>
<dl>
<dt>Required parameters:</dt>
<dd><dl>
<dt>value = <em>state_no</em> (int)</dt>
<dd>Specifies the number of the state to change the targets to.</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>ID = <em>target_id</em> (int)</dt>
<dd>Specifies the desired target ID to affect. Only targets with this
target ID will be affected. Defaults to -1 (affects all targets.)</dd>
</dl>
</dd>
</dl>
    """
    result = StateController()

    set_stateno(result, "value", value)
    set_if(result, "id", id)

    return result

@controller(x = [FloatType, None], y = [FloatType, None], id = [IntType, None])
def TargetVelAdd(x: Optional[ConvertibleExpression] = None, y: Optional[ConvertibleExpression] = None, id: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>TargetVelAdd</h2>
<p>Adds the specified amounts to all targets' velocities. A positive x velocity is in the direction that the target is facing, while a positive y velocity is downward on the screen.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>x = <em>x_value</em> (float)</dt>
<dd>Specifies the value to add to the x-velocity of the target.</dd>
<dt>y = <em>y_value</em> (float)</dt>
<dd>Specifies the value to add to the y-velocity of the target.</dd>
<dt>ID = <em>target_id</em> (int)</dt>
<dd>Specifies the desired target ID to affect. Only targets with this
target ID will be affected. Defaults to -1 (affects all targets.)</dd>
</dl>
</dd>
</dl>
    """
    result = StateController()

    set_if(result, "x", x)
    set_if(result, "y", y)
    set_if(result, "id", id)

    return result

@controller(x = [FloatType, None], y = [FloatType, None], id = [IntType, None])
def TargetVelSet(x: Optional[ConvertibleExpression] = None, y: Optional[ConvertibleExpression] = None, id: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>TargetVelSet</h2>
<p>Sets all targets' velocities to the specified values. A positive x velocity is in the direction that the player is facing, while a positive y velocity is downward on the screen.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>x = <em>x_value</em> (float)</dt>
<dd>Specifies the value to set the x-velocity of the target to</dd>
<dt>y = <em>y_value</em> (float)</dt>
<dd>Specifies the value to set the y-velocity of the target to.</dd>
<dt>ID = <em>target_id</em> (int)</dt>
<dd>Specifies the desired target ID to affect. Only targets with this
target ID will be affected. Defaults to -1 (affects all targets.)</dd>
</dl>
</dd>
</dl>
    """
    result = StateController()

    set_if(result, "x", x)
    set_if(result, "y", y)
    set_if(result, "id", id)

    return result

@controller(trans = [TransTypeT], alpha = [IntPairType, None])
def Trans(trans: ConvertibleExpression, alpha: Optional[TupleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>Trans</h2>
<p>Overrides the player's animation transparency parameters for current game tick. Useful for special effects.</p>
<dl>
<dt>Required parameters:</dt>
<dd><dl>
<dt>trans = <em>trans_type</em> (string)</dt>
<dd><p><em>trans_type</em> must be one of the following:</p>
<ul class="last simple">
<li>default  - does nothing</li>
<li>none     - disables transparency</li>
<li>add      - draws with additive transparency (alpha defaults to 256,256)</li>
<li>addalpha - deprecated in 1.1; draws with additive transparency (alpha defaults to 256,0)</li>
<li>add1     - deprecated in 1.1; draws with additive transparency (alpha defaults to 256,128)</li>
<li>sub      - draws with full subtractive transparency (alpha is fixed at 256,256)</li>
</ul>
</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>alpha = <em>source_alpha</em>, <em>dest_alpha</em> (int, int)</dt>
<dd>These are the source and destination alpha values for the add
trans types. Valid values are from 0 (low) to 256 (high). If omitted,
default depends on <em>trans_type</em>.</dd>
</dl>
</dd>
</dl>
    """
    result = StateController()

    set_if(result, "trans", trans)
    set_if_tuple(result, "alpha", alpha, IntPairType)

    return result

@controller()
def Turn(ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>Turn</h2>
<p>Instantly turns the player to face the opposite direction. Does not play a turning animation.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd>none</dd>
</dl>
    """
    result = StateController()
    return result

@controller(var = [IntType, FloatType, None], value = [IntType, FloatType, None])
def VarAdd(var: Optional[Expression] = None, value: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>VarAdd</h2>
<p>Adds to one of the player's working variables. Either a float variable or an int variable can be added to by this controller.</p>
<dl>
<dt>Required parameters (int version):</dt>
<dd><dl>
<dt>v = <em>var_no</em> (int)</dt>
<dd><em>var_no</em> specifies the number of the variable to affect.
It must evaluate to an integer between 0 and 59.</dd>
<dt>value = <em>int_expr</em> (int)</dt>
<dd><em>int_expr</em> specifies the value to add to the int variable indexed by
<em>var_no</em>.</dd>
</dl>
</dd>
<dt>Required parameters (float version):</dt>
<dd><dl>
<dt>fv = <em>var_no</em> (int)</dt>
<dd><em>var_no</em> specifies the number of the variable to affect.
It must evaluate to an integer between 0 and 39.</dd>
<dt>value = <em>float_expr</em> (float)</dt>
<dd><em>float_expr</em> is the value to add to the float variable indexed by
<em>var_no</em>.</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd>none in both cases</dd>
<dt>Alternate syntax:</dt>
<dd><p>var(<em>var_no</em>) = <em>int_expr</em>  (int version)</p>
<p class="last">fvar(<em>var_no</em>) = <em>float_expr</em> (float version)</p>
</dd>
<dt>Notes:</dt>
<dd><p>Due to historical reasons, note that the alternate VarAdd
syntax listed above matches neither the syntax for variable
assignment within an expression, nor the syntax for variable
addition within an expression.</p>
<p class="last">If you have placed P2 in a custom state through a successful hit, do
not use variable assignment within the custom states. Otherwise, you
will overwrite P2's variables, which can cause unintended
malfunction of the opponent player.</p>
</dd>
</dl>
    """
    result = StateController()

    if var != None:
        set_if(result, var.exprn, value)

    return result

@controller(var = [IntType, FloatType, None], value = [IntType, FloatType, None])
def VarSet(var: Optional[Expression] = None, value: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<p>Sets one of the player's working variables. Either a float variable or an int variable can be set by this controller, but not both at the same time.</p>
<dl>
<dt>Required parameters (int version):</dt>
<dd><dl>
<dt>v = <em>var_no</em> (int)</dt>
<dd><em>var_no</em> specifies the number of the variable to affect.
It must evaluate to an integer between 0 and 59.</dd>
<dt>value = <em>int_expr</em> (int)</dt>
<dd><em>int_expr</em> specifies the value to assign to the int variable indexed by
<em>var_no</em>.</dd>
</dl>
</dd>
<dt>Required parameters (float version):</dt>
<dd><dl>
<dt>fv = <em>var_no</em> (int)</dt>
<dd><em>var_no</em> specifies the number of the variable to affect.
It must evaluate to an integer between 0 and 39.</dd>
<dt>value = <em>float_expr</em> (float)</dt>
<dd><em>float_expr</em> is the value to assign to the float variable indexed by
<em>var_no</em>.</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd>none in both cases</dd>
<dt>Alternate syntax:</dt>
<dd><p>var(<em>var_no</em>) = <em>int_expr</em>  (int version)</p>
<p class="last">fvar(<em>var_no</em>) = <em>float_expr</em> (float version)</p>
</dd>
<dt>Notes:</dt>
<dd><p>Due to historical reasons, note that the alternate variable
assignment syntax listed above does not exactly match the syntax for
variable assignment within an expression.</p>
<p class="last">If you have placed P2 in a custom state through a successful hit, do
not use variable assignment within the custom states. Otherwise, you
will overwrite P2's variables, which can cause unintended
malfunction of the opponent player.</p>
</dd>
</dl>
    """
    result = StateController()

    if var != None:
        set_if(result, var.exprn, value)

    return result

@controller(v = [IntType], range = [IntPairType, None])
def VarRandom(v: ConvertibleExpression, range: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>VarRandom</h2>
<p>Sets the specified int variable to a random value. Float variables cannot be set by this controller.</p>
<dl>
<dt>Required parameters:</dt>
<dd><dl>
<dt>v = <em>var_no</em> (int)</dt>
<dd><em>var_no</em> is the index of the int variable to affect. It must evaluate
to an integer between 0 and 59.</dd>
</dl>
</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>range = <em>least_val</em>, <em>greatest_val</em> (int)</dt>
<dd><em>least_val</em> and <em>greatest_val</em> specify the least and greatest values
which can be assigned by this controller, respectively. The value
assigned to the variable will be a randomly chosen integer from
this range.
range defaults to 0,1000. If only one argument is specified, that
is considered to specify the range 0,(argument).</dd>
</dl>
</dd>
<dt>Notes:</dt>
<dd>If you have placed P2 in a custom state through a successful hit, do
not use variable assignment within the custom states. Otherwise, you
will overwrite P2's variables, which can cause unintended
malfunction of the opponent player.</dd>
</dl>
    """
    result = StateController()

    set_if(result, "v", v)
    set_if(result, "range", range)

    return result

@controller(value = [IntType], fvalue = [FloatType], first = [IntType, None], last = [IntType, None])
def VarRangeSet(value: ConvertibleExpression, fvalue: ConvertibleExpression, first: Optional[ConvertibleExpression] = None, last: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>VarRangeSet</h2>
<p>Sets a contiguous range of the player's working variables to the same value. Either float variables or int variables can be set by this controller, but not both at the same time.</p>
<dl>
<dt>Required parameters (int version):</dt>
<dd><dl>
<dt>value = <em>int_expr</em> (int)</dt>
<dd><em>int_expr</em> is evaluated once to give the value that is assigned to
all int variables in the range.</dd>
</dl>
</dd>
<dt>Required parameters (float version):</dt>
<dd><dl>
<dt>fvalue = <em>float_expr</em> (float)</dt>
<dd><em>float_expr</em> is evaluated once to give the value that is assigned to
all float variables in the range.</dd>
</dl>
</dd>
<dt>Optional parameters (both versions):</dt>
<dd><dl>
<dt>first = <em>first_idx</em> (int)</dt>
<dd>Specifies the lower end of the range of variables to set. Defaults
to 0 (first variable).</dd>
<dt>last = <em>last_idx</em> (int)</dt>
<dd>Specifies the higher end of the range of variables to set.
Defaults to 59 for int variables, or 39 for float variables (this
is the last available variable in both cases).</dd>
</dl>
</dd>
<dt>Notes:</dt>
<dd>If you have placed P2 in a custom state through a successful hit, do
not use variable assignment within the custom states. Otherwise, you
will overwrite P2's variables, which can cause unintended
malfunction of the opponent player.</dd>
</dl>
    """
    result = StateController()

    set_if(result, "value", value)
    set_if(result, "fvalue", fvalue)
    set_if(result, "first", first)
    set_if(result, "last", last)

    return result

@controller(x = [FloatType, None], y = [FloatType, None])
def VelAdd(x: Optional[ConvertibleExpression] = None, y: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>VelAdd</h2>
<p>Adds the specified amounts to the player's velocity. A positive x velocity is in the direction that the player is facing, while a positive y velocity is downward on the screen.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>x = <em>x_value</em> (float)</dt>
<dd>Specifies the value to add to the player's x-velocity.</dd>
<dt>y = <em>y_value</em> (float)</dt>
<dd>Specifies the value to add to the player's y-velocity.</dd>
</dl>
</dd>
</dl>
    """
    result = StateController()

    set_if(result, "x", x)
    set_if(result, "y", y)

    return result

@controller(x = [FloatType, None], y = [FloatType, None])
def VelMul(x: Optional[ConvertibleExpression] = None, y: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>VelMul</h2>
<p>Multiplies the player's velocity by the specified amounts. A positive x velocity is in the direction that the player is facing, while a positive y velocity is downward on the screen.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>x = <em>x_value</em> (float)</dt>
<dd>Specifies the value to multiply the player's x-velocity with.</dd>
<dt>y = <em>y_value</em> (float)</dt>
<dd>Specifies the value to multiply the player's y-velocity with.</dd>
</dl>
</dd>
</dl>
    """
    result = StateController()

    set_if(result, "x", x)
    set_if(result, "y", y)

    return result

@controller(x = [FloatType, None], y = [FloatType, None])
def VelSet(x: Optional[ConvertibleExpression] = None, y: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>VelSet</h2>
<p>Sets the player's velocity to the specified values. A positive x velocity is in the direction that the player is facing, while a positive y velocity is downward on the screen.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>x = <em>x_value</em> (float)</dt>
<dd>Specifies the value to assign to the player's x-velocity.</dd>
<dt>y = <em>y_value</em> (float)</dt>
<dd>Specifies the value to assign to the player's y-velocity.</dd>
</dl>
</dd>
</dl>
    """
    result = StateController()

    set_if(result, "x", x)
    set_if(result, "y", y)

    return result

@controller(value = [IntType, None])
def VictoryQuote(value: Optional[ConvertibleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>VictoryQuote</h2>
<p>Selects a victory quote from the player to display in the next victory screen.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>value = <em>quote_index</em> (int)</dt>
<dd>Specifies the index of the quote to use.  Valid index values are from 0 to 99.
If <em>quote_index</em> evaluates to an invalid index, a random quote will be selected.
Defaults to -1.</dd>
</dl>
</dd>
<dt>Notes:</dt>
<dd>This controller can be called by any player at any time during a match; however
only the winning player will affect the quote that is shown.
This controller only affects the victory screen immediately following the current match.
This controller has no effect if executed by a helper.
The actual victory quotes are specified in the [Quotes] group of the player's constants file.</dd>
</dl>
    """
    result = StateController()

    set_if(result, "value", value)

    return result

@controller(edge = [IntPairType, None], player = [IntPairType, None], value = [IntPairType, None])
def Width(edge: Optional[TupleExpression] = None, player: Optional[TupleExpression] = None, value: Optional[TupleExpression] = None, ignorehitpause: Optional[ConvertibleExpression] = None, persistent: Optional[ConvertibleExpression] = None) -> StateController:
    """
<h2>Width</h2>
<p>Temporarily changes the size of the player's width bar for 1 tick. Useful for controlling the "pushing" behavior when the player makes contact with another or with the sides of the screen.</p>
<dl>
<dt>Required parameters:</dt>
<dd>none</dd>
<dt>Optional parameters:</dt>
<dd><dl>
<dt>edge = <em>edgewidth_front</em>, <em>edgewidth_back</em> (int, int)</dt>
<dd>Sets the player's edge width in front and behind. Edge width
determines how close the player can get to the edge of the screen.
These parameters default to 0,0 if omitted.</dd>
<dt>player = <em>playwidth_front</em>, <em>playwidth_back</em> (int, int)</dt>
<dd>Sets the player width in front and behind. Player width determines
how close the player can get to other players. These parameters
default to 0,0 if omitted.</dd>
</dl>
</dd>
<dt>Alternate syntax:</dt>
<dd><dl>
<dt>value = <em>width_front</em>, <em>width_back</em> (int, int)</dt>
<dd>This is a shorthand syntax for setting both edge width and player
width simultaneously. This may only be used if the edge and player
parameters are not specified.</dd>
</dl>
</dd>
<dt>Notes:</dt>
<dd>When collision box display is enabled, the edge width bar is
displayed in orange, and the player width bar is displayed in
yellow. Where they overlap, the overlapping region is displayed in
bright yellow.</dd>
</dl>
    """
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
    "VelAdd", "VelMul", "VelSet", "VictoryQuote", "Width", "BGPalFX", "AllPalFX", "DisplayToClipboard", "AppendToClipboard"
]