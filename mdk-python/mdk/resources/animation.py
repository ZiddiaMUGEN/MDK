## this module provides a wrapper around animations in MUGEN.
## MDK will compile each animation to an AIR definition and then merge these definitions with the provided AIR file, if one is provided.

from __future__ import annotations

from typing import Callable
from enum import Flag, Enum
from copy import deepcopy

from mdk.types.context import CompilerContext

class AnimationFlip(Flag):
    NONE = 0
    VERTICAL = 1
    HORIZONTAL = 2
    BOTH = 3

def get_flip(flip: AnimationFlip):
    if flip == AnimationFlip.BOTH: return "VH"
    if flip == AnimationFlip.HORIZONTAL: return "H"
    if flip == AnimationFlip.VERTICAL: return "V"
    return ""

class Clsn:
    _xmin: int
    _ymin: int
    _xmax: int
    _ymax: int
    _default: bool

    def __init__(self, xmin: int, ymin: int, xmax: int, ymax: int, default: bool = False):
        self._xmin = xmin
        self._ymin = ymin
        self._xmax = xmax
        self._ymax = ymax
        self._default = default

class Frame:
    _group: int
    _index: int
    _length: int = -1
    _offset: tuple[int, int] = (0, 0)
    _flip: AnimationFlip = AnimationFlip.NONE
    _trans: str | None = None
    _scale: tuple[float, float] = (1, 1)
    _rotate: int = 0
    _loopstart: bool = False
    _clsn1: list[Clsn] = []
    _clsn2: list[Clsn] = []
    _last_clsn: Clsn | None = None

    def __init__(self, 
                 group: int, index: int, length: int = -1, 
                 offset: tuple[int, int] = (0, 0), flip: AnimationFlip = AnimationFlip.NONE, trans: str | None = None,
                 scale: tuple[float, float] = (1, 1), rotate: int = 0):
        self._group = group
        self._index = index
        self._length = length
        self._offset = offset
        self._flip = flip
        self._trans = trans
        self._scale = scale
        self._rotate = rotate
        self._loopstart = False
        self._clsn1 = []
        self._clsn2 = []
        self._last_clsn = None

    def compile(self):
        """Compiles the current Frame, returning a single line of an animation."""
        result = ""
        
        ## Clsn1Default
        clsns = [c for c in self._clsn1 if c._default]
        if len(clsns) != 0: result = f"{result}Clsn1Default: {len(clsns)}\n"
        for index in range(len(clsns)):
            clsn = clsns[index]
            result = f"{result}  Clsn1[{index}] = {clsn._xmin}, {clsn._ymin}, {clsn._xmax}, {clsn._ymax}\n"
        ## Clsn2Default
        clsns = [c for c in self._clsn2 if c._default]
        if len(clsns) != 0: result = f"{result}Clsn2Default: {len(clsns)}\n"
        for index in range(len(clsns)):
            clsn = clsns[index]
            result = f"{result}  Clsn2[{index}] = {clsn._xmin}, {clsn._ymin}, {clsn._xmax}, {clsn._ymax}\n"
        ## Clsn1
        clsns = [c for c in self._clsn1 if not c._default]
        if len(clsns) != 0: result = f"{result}Clsn1: {len(clsns)}\n"
        for index in range(len(clsns)):
            clsn = clsns[index]
            result = f"{result}  Clsn1[{index}] = {clsn._xmin}, {clsn._ymin}, {clsn._xmax}, {clsn._ymax}\n"
        ## Clsn2
        clsns = [c for c in self._clsn2 if not c._default]
        if len(clsns) != 0: result = f"{result}Clsn2: {len(clsns)}\n"
        for index in range(len(clsns)):
            clsn = clsns[index]
            result = f"{result}  Clsn2[{index}] = {clsn._xmin}, {clsn._ymin}, {clsn._xmax}, {clsn._ymax}\n"

        ## Loopstart
        if self._loopstart:
            result = f"{result}Loopstart\n"

        result = f"{result}{self._group}, {self._index}, {self._offset[0]}, {self._offset[1]}, {self._length}"

        ## early exit if no extra params are set.
        if self._flip == AnimationFlip.NONE and self._trans == None and self._scale[0] == 1 and self._scale[1] == 1 and self._rotate == 0:
            return result
        result += f", {get_flip(self._flip)}"
        result += f", {self._trans if self._trans != None else ''}"
        result += f", {self._scale[0]}, {self._scale[1]}"
        result += f", {self._rotate}"
        return result
    
    def python(self, indent: int = 0) -> str:
        indents = "    " * (indent + 1)

        result = f"Frame({self._group}, {self._index}, length = {self._length})"

        if self._offset != (0, 0): result += f"\n{indents}.offset({self._offset})"
        if self._flip != AnimationFlip.NONE: result += f"\n{indents}.flip({self._flip})"
        if self._trans != None: result += f"\n{indents}.trans(\"{self._trans}\")"
        if self._scale != (1, 1): result += f"\n{indents}.scale({self._scale})"
        if self._rotate != 0: result += f"\n{indents}.rotate({self._rotate})"
        if self._loopstart: result += f"\n{indents}.loop()"
        
        for clsn in self._clsn1:
            result += f"\n{indents}.clsn1(Clsn({clsn._xmin}, {clsn._ymin}, {clsn._xmax}, {clsn._ymax}))"
            if clsn._default: result += ".default()"

        for clsn in self._clsn2:
            result += f"\n{indents}.clsn2(Clsn({clsn._xmin}, {clsn._ymin}, {clsn._xmax}, {clsn._ymax}))"
            if clsn._default: result += ".default()"

        return result
    
    def seq(self) -> Sequence:
        """Converts this Frame into a Sequence containing the frame."""
        return Sequence([self])
    
    def dup(self) -> Frame:
        """Returns a new Frame which is a duplicate of this Frame."""
        return deepcopy(self)
    
    def clsn1(self, clsn: Clsn) -> Frame:
        """Attaches a Clsn1 (hitbox) to the character."""
        self._clsn1.append(deepcopy(clsn))
        self._last_clsn = self._clsn1[-1]
        return self
    
    def clsn2(self, clsn: Clsn) -> Frame:
        """Attaches a Clsn2 (hurtbox) to the character."""
        self._clsn2.append(deepcopy(clsn))
        self._last_clsn = self._clsn2[-1]
        return self
    
    def default(self) -> Frame:
        """Makes the most recently applied Clsn into a default Clsn."""
        if self._last_clsn == None:
            raise Exception("Can only call `default` if a Clsn has been defined!")
        self._last_clsn._default = True
        return self
    
    def length(self, length: int) -> Frame:
        """Updates the duration of the frame to the provided length."""
        self._length = length
        return self
    
    def flip(self, flip: AnimationFlip) -> Frame:
        """Adds the provided flip type(s) to the frame."""
        self._flip = self._flip | flip
        return self
    
    def rotate(self, rotate: int) -> Frame:
        """Applies the provided angle of rotation to the frame."""
        self._rotate = rotate
        return self
        
    def offset(self, offset: tuple[int, int]) -> Frame:
        """Applies the provided offset to the frame."""
        self._offset = offset
        return self
    
    def translate(self, offset: tuple[int, int]) -> Frame:
        """Translates the frame, adding the provided offset to its internal offset."""
        self._offset = (self._offset[0] + offset[0], self._offset[1] + offset[1])
        return self
    
    def scale(self, scale: tuple[float, float]) -> Frame:
        """Applies the provided scale to the frame."""
        self._scale = scale
        return self
    
    def loop(self) -> Frame:
        """Indicates that the sequence's loop-time should begin on this frame."""
        self._loopstart = True
        return self
    
class SequenceModifier:
    """A special class used to modify properties across a range of Frames."""
    _frames: list[Frame]
    _prop: str
    _slice: slice
    
    def __init__(self, frames: list[Frame], prop: str, sl: slice | None = None):
        self._frames = deepcopy(frames)
        self._prop = prop
        self._slice = sl if sl != None else slice(0, len(frames))

    def python(self, name: str | None = None):
        return self.seq().python(name)

    def seq(self):
        """Converts this modified Sequence into a real Sequence object."""
        return Sequence(self._frames)
    
    def set(self, val: int | Enum, filter: Callable[[Frame], bool] | None = None) -> SequenceModifier:
        """Sets the provided value to the target property on all frames (or frames which pass the provided filter function)."""
        for frame in self._frames[self._slice]:
            if filter == None or filter(frame):
                setattr(frame, self._prop, val)
        return self
    
    def add(self, val: int | Enum, filter: Callable[[Frame], bool] | None = None) -> SequenceModifier:
        """Adds the provided value to the target property on all frames (or frames which pass the provided filter function)."""
        for frame in self._frames[self._slice]:
            if filter == None or filter(frame):
                setattr(frame, self._prop, getattr(frame, self._prop) + val)
        return self
    
    def mul(self, val: int | Enum, filter: Callable[[Frame], bool] | None = None) -> SequenceModifier:
        """Multiplies the provided value to the target property on all frames (or frames which pass the provided filter function)."""
        for frame in self._frames[self._slice]:
            if filter == None or filter(frame):
                setattr(frame, self._prop, getattr(frame, self._prop) * val)
        return self
    
    def transform(self, transformer: Callable[[Frame, int], int]) -> SequenceModifier:
        """Uses the provided transformer function to transform the property on all frames."""
        for frame in self._frames[self._slice]:
            setattr(frame, self._prop, transformer(frame, getattr(frame, self._prop)))
        return self
    
    def extend(self, frames: Frame | list[Frame] | Sequence | SequenceModifier | FrameSequenceModifier | TupleSequenceModifier) -> Sequence:
        """Adds the provided frame or frames to this Sequence and returns a new Sequence containing those frames."""
        return self.seq().extend(frames)
    
    def __getitem__(self, key: int | slice) -> SequenceModifier:
        if type(key) == slice:
            self._slice = key
            return self
        else:
            self._slice = slice(key, key + 1)
            return self
    
    ### below this is all the Sequence properties re-applied here. this is for convenience to avoid needing to call `seq()` every time.
    def compile(self):
        return self.seq().compile()

    @property
    def frames(self):
        """Returns a modifiable Sequence which can apply generic transformations across all contained frames."""
        return FrameSequenceModifier(self._frames, self._slice)
        
    @property
    def group(self):
        """Returns a modifiable Sequence which can apply transformations to the `group` property of all contained frames."""
        return SequenceModifier(self._frames, "_group", self._slice)
    
    @property
    def index(self):
        """Returns a modifiable Sequence which can apply transformations to the `index` property of all contained frames."""
        return SequenceModifier(self._frames, "_index", self._slice)
    
    @property
    def length(self):
        """Returns a modifiable Sequence which can apply transformations to the `length` property of all contained frames."""
        return SequenceModifier(self._frames, "_length", self._slice)
    
    @property
    def rotation(self):
        """Returns a modifiable Sequence which can apply transformations to the `rotate` property of all contained frames."""
        return SequenceModifier(self._frames, "_rotate", self._slice)
    
    @property
    def offset(self):
        """Returns a modifiable Sequence which can apply transformations to the `offset` property of all contained frames."""
        return TupleSequenceModifier(self._frames, "_offset", self._slice)
    
    @property
    def scale(self):
        """Returns a modifiable Sequence which can apply transformations to the `scale` property of all contained frames."""
        return TupleSequenceModifier(self._frames, "_scale", self._slice)
    
    @property
    def flip(self):
        """Returns a modifiable Sequence which can apply transformations to the `flip` property of all contained frames."""
        return SequenceModifier(self._frames, "_flip", self._slice)
    
class TupleSequenceModifier(SequenceModifier):
    """A custom SequenceModifier used to apply transformations to the tuple fields, offset and scale."""

    def set(self, val: tuple[int, int], filter: Callable[[Frame], bool] | None = None) -> TupleSequenceModifier: # type: ignore
        """Sets the provided value to the target property on all frames (or frames which pass the provided filter function)."""
        for frame in self._frames[self._slice]:
            if filter == None or filter(frame):
                setattr(frame, self._prop, val)
        return self
    
    def add(self, val: tuple[int, int], filter: Callable[[Frame], bool] | None = None) -> TupleSequenceModifier: # type: ignore
        """Adds the provided value to the target property on all frames (or frames which pass the provided filter function)."""
        for frame in self._frames[self._slice]:
            if filter == None or filter(frame):
                current: tuple[int, int] = getattr(frame, self._prop)
                setattr(frame, self._prop, (current[0] + val[0], current[1] + val[1]))
        return self
    
    def mul(self, val: tuple[int, int], filter: Callable[[Frame], bool] | None = None) -> TupleSequenceModifier: # type: ignore
        """Multiplies the provided value to the target property on all frames (or frames which pass the provided filter function)."""
        for frame in self._frames[self._slice]:
            if filter == None or filter(frame):
                current: tuple[int, int] = getattr(frame, self._prop)
                setattr(frame, self._prop, (current[0] * val[0], current[1] * val[1]))
        return self
    
    def transform(self, transformer: Callable[[Frame, tuple[int, int]], tuple[int, int]]) -> TupleSequenceModifier: # type: ignore
        """Uses the provided transformer function to transform the property on all frames."""
        for frame in self._frames[self._slice]:
            setattr(frame, self._prop, transformer(frame, getattr(frame, self._prop)))
        return self
    
class FrameSequenceModifier(SequenceModifier):
    """A custom SequenceModifier used to apply transformations across the frame sequence, instead of to frame properties."""

    def __init__(self, frames: list[Frame], sl: slice | None = None):
        self._frames = deepcopy(frames)
        self._slice = sl if sl != None else slice(0, len(frames))

    def set(self, val: int | Enum, filter: Callable[[Frame], bool] | None = None) -> SequenceModifier:
        raise Exception("SequenceModifier `set` cannnot be used for the `frames` modifiable sequence.")
    def add(self, val: int | Enum, filter: Callable[[Frame], bool] | None = None) -> SequenceModifier:
        raise Exception("SequenceModifier `add` cannnot be used for the `frames` modifiable sequence.")
    def mul(self, val: int | Enum, filter: Callable[[Frame], bool] | None = None) -> SequenceModifier:
        raise Exception("SequenceModifier `mul` cannnot be used for the `frames` modifiable sequence.")
    
    def reverse(self) -> FrameSequenceModifier:
        """Reverses the Frames contained in this modifiable Sequence.
        This function does not consider the current slice, and will reverse ALL frames in the sequence."""
        self._frames = list(reversed(self._frames))
        return self
    
    def transform(self, transformer: Callable[[Frame], Frame]) -> FrameSequenceModifier: # type: ignore
        """Applies the provided transformation function to all Frames in the sequence, updating the Frames with the returned value."""
        newframes: list[Frame] = []
        for frame in self._frames:
            if frame in self._frames[self._slice]:
                newframes.append(transformer(frame))
            else:
                newframes.append(frame)
        self._frames = newframes
        return self
    
    def clsn1(self, clsn: Clsn, filter: Callable[[Frame], bool] | None = None) -> FrameSequenceModifier:
        """Applies the provided Clsn1 box to all frames which match the provided filter."""
        for frame in self._frames[self._slice]:
            if filter == None or filter(frame):
                frame.clsn1(clsn)
        return self
    
    def clsn2(self, clsn: Clsn, filter: Callable[[Frame], bool] | None = None) -> FrameSequenceModifier:
        """Applies the provided Clsn1 box to all frames which match the provided filter."""
        for frame in self._frames[self._slice]:
            if filter == None or filter(frame):
                frame.clsn2(clsn)
        return self
    
    def default(self, filter: Callable[[Frame], bool] | None = None) -> FrameSequenceModifier:
        """Makes the most recently applied Clsn box default for all frames which match the provided filter."""
        for frame in self._frames[self._slice]:
            if filter == None or filter(frame):
                frame.default()
        return self

class Sequence:
    """Represents a sequence of animation elements (or Frames).
    A Sequence is immutable, but there are multiple utility methods to create a modified copy of a Sequence."""
    _frames: list[Frame]

    def __init__(self, frames: list[Frame]):
        self._frames = frames

    def compile(self):
        """Compiles the frames contained in this Sequence, returning a collection of animation elements in AIR format."""
        result = ""
        for frame in self._frames:
            result += frame.compile() + "\n"
        return result
    
    def python(self, name: str | None = None) -> str:
        if name == None:
            name = "(Anonymous Member)"

        result = f"{name} = Sequence([\n"

        for frame in self._frames:
            result += f"        {frame.python(2)},\n"

        result += "])"
        
        return result
    
    def extend(self, frames: Frame | list[Frame] | Sequence | SequenceModifier | FrameSequenceModifier | TupleSequenceModifier) -> Sequence:
        """Adds the provided frame or frames to this Sequence and returns a new Sequence containing those frames."""
        newframes = deepcopy(self._frames)

        if type(frames) == FrameSequenceModifier or type(frames) == TupleSequenceModifier:
            frames = frames.seq()

        if type(frames) == Frame:
            return Sequence(newframes + [frames])
        elif type(frames) == list and all(isinstance(n, Frame) for n in frames):
            return Sequence(newframes + frames)
        elif type(frames) == Sequence:
            return Sequence(newframes + deepcopy(frames._frames))
        elif type(frames) == SequenceModifier:
            return self.extend(frames.seq())
        raise Exception(f"Unexpected input type {type(frames)} to Sequence extension")
    
    def __getitem__(self, key: int | slice) -> Sequence:
        if type(key) == slice:
            if key.step != None:
                raise Exception("Can only handle simple slices in Sequence.")
            return Sequence(deepcopy(self._frames[key.start:key.stop]))
        else:
            return Sequence([deepcopy(self._frames[key])])
    
    @property
    def frames(self):
        """Returns a modifiable Sequence which can apply generic transformations across all contained frames."""
        return FrameSequenceModifier(self._frames)
    
    @property
    def group(self):
        """Returns a modifiable Sequence which can apply transformations to the `group` property of all contained frames."""
        return SequenceModifier(self._frames, "_group")
    
    @property
    def index(self):
        """Returns a modifiable Sequence which can apply transformations to the `index` property of all contained frames."""
        return SequenceModifier(self._frames, "_index")
    
    @property
    def length(self):
        """Returns a modifiable Sequence which can apply transformations to the `length` property of all contained frames."""
        return SequenceModifier(self._frames, "_length")
    
    @property
    def rotation(self):
        """Returns a modifiable Sequence which can apply transformations to the `rotate` property of all contained frames."""
        return SequenceModifier(self._frames, "_rotate")
    
    @property
    def offset(self):
        """Returns a modifiable Sequence which can apply transformations to the `offset` property of all contained frames."""
        return TupleSequenceModifier(self._frames, "_offset")
    
    @property
    def scale(self):
        """Returns a modifiable Sequence which can apply transformations to the `scale` property of all contained frames."""
        return TupleSequenceModifier(self._frames, "_scale")
    
    @property
    def flip(self):
        """Returns a modifiable Sequence which can apply transformations to the `flip` property of all contained frames."""
        return SequenceModifier(self._frames, "_flip")

class Animation:
    """Represents an animation in a character's AIR file.
    Animations are immutable, once an animation has been defined it should not be modified."""
    _frames: Sequence | None
    _id: int | None
    _external: bool

    def __init__(self, frames: Sequence | SequenceModifier | list[Frame] | Frame | None = None, id: int | None = None, external: bool = False):
        if frames != None and external:
            raise Exception("External animation must not provide a frames parameter.")
        
        self._external = False
        
        if frames == None or external:
            self._frames = None
            self._external = True
        elif type(frames) == list and all(isinstance(n, Frame) for n in frames):
            self._frames = Sequence(frames)
        elif type(frames) == Frame:
            self._frames = Sequence([frames])
        elif type(frames) == SequenceModifier or type(frames) == FrameSequenceModifier or type(frames) == TupleSequenceModifier:
            self._frames = frames.seq()
        elif type(frames) == Sequence:
            self._frames = frames
        else:
            raise Exception("frames must be None, a Sequence, or a list of Frame objects.")

        self._id = id

        matching = [x for x in CompilerContext.instance().animations if x._id == self._id and not x._external]
        if self._id != None and not self._external and len(matching) != 0:
            raise Exception(f"An animation with ID {self._id} was already declared!")
        CompilerContext.instance().animations.append(self)

    @property
    def sequence(self):
        """Returns a modifiable Sequence object which can be used to transform and obtain a new Sequence."""
        return deepcopy(self._frames) if self._frames != None else Sequence([])

    def compile(self):
        """Compiles the animation, returning a string in AIR format."""

        ## assign an animation ID based on the IDs which have already been used
        if self._id == None:
            self._id = CompilerContext.instance().get_next_anim_id()
        
        ## build the AIR output from the animation ID and the contained sequence
        result = f"[Begin Action {self._id}]\n"
        result += self._frames.compile() if self._frames != None else ""

        return result
    
    def python(self, name: str | None = None) -> str:
        if name == None:
            name = "(Anonymous Member)"
        
        result = f"{name} = Animation(\n"
        if self._id != None:
            result += f"    id = {self._id},\n"
        result += f"    frames = Sequence([\n"

        if self._frames != None:
            for frame in self._frames._frames:
                result += f"        {frame.python(2)},\n"

        result += "    ])\n"
        result += ")"

        return result
    
    def __str__(self):
        return self.compile()
    
    def __repr__(self):
        return self.compile()
    
__all__ = ["Animation", "Sequence", "Frame", "AnimationFlip"]