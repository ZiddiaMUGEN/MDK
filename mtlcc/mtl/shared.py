from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

@dataclass
class INIProperty:
    key: str
    value: str
    filename: str
    line: int

@dataclass
class INISection:
    name: str
    comment: str
    properties: List[INIProperty]
    filename: str
    line: int

@dataclass
class INIParserContext:
    filename: str
    line: int

    def __init__(self, fn: str):
        self.filename = fn
        self.line = 0

class TriggerTreeNode(Enum):
    MULTIVALUE = -1
    UNARY_OP = 0
    BINARY_OP = 1
    INTERVAL_OP = 2
    FUNCTION_CALL = 3
    ATOM = 4

@dataclass
class TriggerTree:
    node: TriggerTreeNode
    operator: str
    children: List['TriggerTree']

    def _string(self, indent: int) -> str:
        result = "\t" * indent
        result += str(self.node)

        if self.node == TriggerTreeNode.MULTIVALUE:
            if len(self.children) == 1:
                return self.children[0]._string(0)
            result += " ("
            for child in self.children:
                result += "\n" + child._string(indent + 1)
            result += "\n)"
        if self.node == TriggerTreeNode.UNARY_OP:
            result += f" {self.operator}\n{self.children[0]._string(indent + 1)}"
        elif self.node == TriggerTreeNode.BINARY_OP:
            result += f" {self.operator}\n{self.children[0]._string(indent + 1)}\n{self.children[1]._string(indent + 1)}"
        elif self.node == TriggerTreeNode.INTERVAL_OP:
            result += f" {self.operator[0]}\n{self.children[0]._string(indent + 1)}\n{self.children[1]._string(indent + 1)}\n"
            result += "\t" * indent
            result += f"{self.operator[1]}"
        elif self.node == TriggerTreeNode.FUNCTION_CALL:
            result += f" {self.operator} ("
            for child in self.children:
                result += "\n" + child._string(indent + 1)
            result += "\n" + "\t" * indent + ")"
        elif self.node == TriggerTreeNode.ATOM:
            result += " " + self.operator
        return result

    def __repr__(self) -> str:
        return self._string(0)

@dataclass
class StateControllerProperty:
    key: str
    value: TriggerTree

@dataclass
class StateControllerSection:
    properties: List[StateControllerProperty]
    filename: str
    line: int

@dataclass
class StateDefinitionSection:
    name: str
    props: List[INIProperty]
    states: List[StateControllerSection]
    filename: str
    line: int

    def __init__(self, name: str, props: List[INIProperty], filename: str, line: int):
        self.name = name
        self.states = []
        self.props = props
        self.filename = filename
        self.line = line

@dataclass
class TemplateSection:
    name: str
    namespace: Optional[str]
    states: List[StateControllerSection]
    params: Optional[INISection]
    filename: str
    line: int

    def __init__(self, name: str, filename: str, line: int):
        self.states = []
        self.params = None
        self.name = name
        self.namespace = None
        self.filename = filename
        self.line = line

@dataclass
class TriggerSection:
    name: str
    type: str
    value: TriggerTree
    params: Optional[INISection]
    namespace: Optional[str]
    filename: str
    line: int

    def __init__(self, name: str, type: str, value: TriggerTree, filename: str, line: int):
        self.params = None
        self.name = name
        self.type = type
        self.value = value
        self.namespace = None
        self.filename = filename
        self.line = line

@dataclass
class StructureDefinitionSection:
    name: str
    members: INISection
    filename: str
    line: int
    template: Optional[str] = None
    namespace: Optional[str] = None

@dataclass
class TypeDefinitionSection:
    name: str
    type: str
    properties: List[INIProperty]
    filename: str
    line: int
    namespace: Optional[str] = None

@dataclass
class LoadContext:
    filename: str
    ini_context: INIParserContext
    state_definitions: List[StateDefinitionSection]
    templates: List[TemplateSection]
    triggers: List[TriggerSection]
    type_definitions: List[TypeDefinitionSection]
    struct_definitions: List[StructureDefinitionSection]
    includes: List[INISection]

    def __init__(self, fn: str):
        self.filename = fn
        self.ini_context = INIParserContext(fn)
        self.state_definitions = []
        self.templates = []
        self.triggers = []
        self.type_definitions = []
        self.struct_definitions = []
        self.includes = []

class TranslationMode(Enum):
    MTL_MODE = 0
    CNS_MODE = 1

class TypeCategory(Enum):
    INVALID = -1
    ALIAS = 0
    UNION = 1
    ENUM = 2
    FLAG = 3
    STRING_FLAG = 97 # special builtin type for things such as hitdefattr where the flag identifier is preserved in the output.
    STRING_ENUM = 98 # special builtin type for things such as movetype, statetype, etc where the enum identifier is preserved in the output.
    BUILTIN = 99 # special builtin types (int, float, etc) which need to exist for type-checking.

@dataclass
class TypeDefinition:
    name: str
    category: TypeCategory
    ## size is expressed in bits (to support 1-bit bool)
    size: int
    # valid values for 'members' depends on the category.
    # - for ALIAS, there must be exactly 1 member, matching another type name.
    # - for UNION, there can be as many members as needed, with matching sizes.
    # - for ENUM, the members define the valid values the enumeration can take; enumeration IDs are assigned in order.
    # - for FLAG, the members define the valid flag values which can be set; a maximum of 32 members can be added.
    members: List[str]
    filename: str
    line: int

@dataclass
class TranslationContext:
    filename: str
    types: List[TypeDefinition]

    def __init__(self, filename: str):
        self.filename = filename
        self.types = []
