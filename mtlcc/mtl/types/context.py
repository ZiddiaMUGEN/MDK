from dataclasses import dataclass
from enum import Enum

from mtl.types.ini import *
from mtl.types.translation import *
from mtl.types.debugging import *

class TranslationMode(Enum):
    MTL_MODE = 0
    CNS_MODE = 1

@dataclass
class CompilerConfiguration:
    ## if enabled, implicit conversion between fundamental types is disabled.
    ## this will still allow int -> float as the type-checker marks any number without decimal as `int`.
    no_implicit_conversion: bool = False
    ## if enabled, the numeric union type is disabled.
    no_numeric: bool = False
    ## if enabled, implicit conversion from `int` to `bool` (for triggers) is disabled.
    no_implicit_bool: bool = False
    ## if enabled, the typechecker will not attempt to 'guess' enum types in trigger arguments.
    no_implicit_enum: bool = False
    ## if enabled, the typechecker will not allow expressions to be used as the target of ChangeState and ChangeState-like properties.
    no_changestate_expression: bool = False
    ## if enabled, the debugger will not emit debuginfo string or compiler-internal locations (improves compilation speed)
    no_compiler_internal: bool = True
    ## if enabled, scope checking will permit a state change from any state to a TARGET state.
    allow_changestate_target: bool = False

@dataclass
class LoadContext:
    filename: str
    ini_context: INIParserContext
    state_definitions: list[StateDefinitionSection]
    templates: list[TemplateSection]
    triggers: list[TriggerSection]
    type_definitions: list[TypeDefinitionSection]
    struct_definitions: list[StructureDefinitionSection]
    includes: list[INISection]
    mode: TranslationMode
    global_forwards: list[ForwardParameter]
    compiler_flags: CompilerConfiguration

    def __init__(self, fn: str, cc: CompilerConfiguration):
        self.filename = fn
        self.ini_context = INIParserContext(fn, Location(self.filename, 0))
        self.state_definitions = []
        self.templates = []
        self.triggers = []
        self.type_definitions = []
        self.struct_definitions = []
        self.includes = []
        self.global_forwards = []
        self.compiler_flags = cc

@dataclass
class TranslationContext:
    filename: str
    types: list[TypeDefinition]
    triggers: list[TriggerDefinition]
    templates: list[TemplateDefinition]
    statedefs: list[StateDefinition]
    globals: list[TypeParameter]
    allocations: dict[StateDefinitionScope, tuple[AllocationTable, AllocationTable, AllocationTable, AllocationTable]]
    compiler_flags: CompilerConfiguration
    debugging: DebuggingContext

    def __init__(self, filename: str, cc: CompilerConfiguration):
        self.filename = filename
        self.types = []
        self.triggers = []
        self.templates = []
        self.statedefs = []
        self.globals = []
        self.allocations = {}
        self.compiler_flags = cc
        self.debugging = DebuggingContext()

@dataclass
class ProjectContext:
    filename: str
    source_files: list[str]
    common_file: str
    anim_file: str
    snd_file: str
    spr_file: str
    cns_file: str
    ai_file: Optional[str]
    constants: list[INISection]
    commands: list[INISection]
    contents: list[INISection]
    global_forwards: list[ForwardParameter]
    compiler_flags: CompilerConfiguration

    def __init__(self, filename: str):
        self.filename = filename
        self.source_files = []
        self.common_file = ""
        self.contents = []
        self.anim_file = ""
        self.snd_file = ""
        self.spr_file = ""
        self.cns_file = ""
        self.ai_file = None
        self.constants = []
        self.commands = []
        self.global_forwards = []
        self.compiler_flags = CompilerConfiguration()
