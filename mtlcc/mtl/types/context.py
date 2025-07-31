from dataclasses import dataclass
from enum import Enum

from mtl.types.ini import *
from mtl.types.translation import *

class TranslationMode(Enum):
    MTL_MODE = 0
    CNS_MODE = 1

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

    def __init__(self, fn: str):
        self.filename = fn
        self.ini_context = INIParserContext(fn, Location(self.filename, 0))
        self.state_definitions = []
        self.templates = []
        self.triggers = []
        self.type_definitions = []
        self.struct_definitions = []
        self.includes = []

@dataclass
class TranslationContext:
    filename: str
    types: list[TypeDefinition]
    triggers: list[TriggerDefinition]
    templates: list[TemplateDefinition]
    statedefs: list[StateDefinition]
    globals: list[TypeParameter]
    allocations: dict[StateDefinitionScope, tuple[AllocationTable, AllocationTable]]

    def __init__(self, filename: str):
        self.filename = filename
        self.types = []
        self.triggers = []
        self.templates = []
        self.statedefs = []
        self.globals = []
        self.allocations = {}

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

    def __init__(self, filename: str):
        self.filename = filename
        self.source_files = []
        self.common_file = ""
        self.contents = []
        self.anim_file = ""
        self.snd_file = ""
        self.spr_file = ""
        self.ai_file = None
        self.constants = []
        self.commands = []
    