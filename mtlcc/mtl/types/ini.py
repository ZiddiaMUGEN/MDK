from dataclasses import dataclass
from typing import Optional

from mtl.types.shared import Location
from mtl.types.trigger import TriggerTree

@dataclass
class INIProperty:
    key: str
    value: str
    location: Location

@dataclass
class INISection:
    name: str
    comment: str
    properties: list[INIProperty]
    location: Location

@dataclass
class INIParserContext:
    location: Location

    def __init__(self, fn: str, location: Location):
        self.location = location

@dataclass
class StateControllerProperty:
    key: str
    value: TriggerTree
    location: Location

@dataclass
class StateControllerSection:
    properties: list[StateControllerProperty]
    location: Location

@dataclass
class StateDefinitionSection:
    name: str
    props: list[INIProperty]
    states: list[StateControllerSection]
    location: Location
    is_common: bool

    def __init__(self, name: str, props: list[INIProperty], location: Location):
        self.name = name
        self.states = []
        self.props = props
        self.location = location
        self.is_common = False

@dataclass
class TemplateSection:
    name: str
    namespace: Optional[str]
    states: list[StateControllerSection]
    params: Optional[INISection]
    locals: list[INIProperty]
    location: Location

    def __init__(self, name: str, location: Location):
        self.states = []
        self.params = None
        self.name = name
        self.namespace = None
        self.location = location
        self.locals = []

@dataclass
class TriggerSection:
    name: str
    type: str
    value: TriggerTree
    params: Optional[INISection]
    namespace: Optional[str]
    location: Location

    def __init__(self, name: str, type: str, value: TriggerTree, location: Location):
        self.params = None
        self.name = name
        self.type = type
        self.value = value
        self.namespace = None
        self.location = location

@dataclass
class StructureDefinitionSection:
    name: str
    members: INISection
    location: Location
    template: Optional[str] = None
    namespace: Optional[str] = None

@dataclass
class TypeDefinitionSection:
    name: str
    type: str
    properties: list[INIProperty]
    location: Location
    namespace: Optional[str] = None