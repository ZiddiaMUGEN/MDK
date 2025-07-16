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

@dataclass
class StateDefinitionSection:
    name: str
    props: List[INIProperty]
    states: List[StateControllerSection]

    def __init__(self, name: str, props: List[INIProperty]):
        self.name = name
        self.states = []
        self.props = props

@dataclass
class TemplateSection:
    name: str
    states: List[StateControllerSection]
    params: Optional[INISection]

    def __init__(self, name: str):
        self.states = []
        self.params = None
        self.name = name

@dataclass
class TriggerSection:
    name: str
    type: str
    value: str
    params: Optional[INISection]

    def __init__(self, name: str, type: str, value: str):
        self.params = None
        self.name = name
        self.type = type
        self.value = value

@dataclass
class StructureDefinitionSection:
    name: str
    members: INISection

@dataclass
class TranslationContext:
    filename: str
    ini_context: INIParserContext
    state_definitions: List[StateDefinitionSection]
    templates: List[TemplateSection]
    triggers: List[TriggerSection]
    type_definitions: List[INISection]
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
