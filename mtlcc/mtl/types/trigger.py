from dataclasses import dataclass
from enum import Enum

from mtl.types.shared import Location

class TriggerTreeNode(Enum):
    EMPTY = -2
    MULTIVALUE = -1
    UNARY_OP = 0
    BINARY_OP = 1
    INTERVAL_OP = 2
    FUNCTION_CALL = 3
    ATOM = 4
    STRUCT_ACCESS = 5
    REDIRECT = 6

@dataclass
class TriggerTree:
    node: TriggerTreeNode
    operator: str
    children: list['TriggerTree']
    location: Location
    precedence: bool = False

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TriggerTree):
            return False
        if self.node != other.node or self.operator.lower() != other.operator.lower():
            return False
        if len(self.children) != len(other.children):
            return False
        for subindex in range(len(self.children)):
            if self.children[subindex] != other.children[subindex]:
                return False
        return True

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
            result += f" {self.operator} (\n"
            for child in self.children:
                result += child._string(indent + 1) + "\n"
            result += "\t" * indent
            result += ")"
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
        elif self.node == TriggerTreeNode.STRUCT_ACCESS:
            result += f" {self.operator} (\n"
            result += self.children[0]._string(indent + 1)
            for child in self.children[1:]:
                result += " -> " + child._string(indent)
            result += ")"
        elif self.node == TriggerTreeNode.REDIRECT:
            result += f" {self.operator} (\n"
            for child in self.children:
                result += "\n" + child._string(indent + 1)
            result += ")"
        return result

    def __repr__(self) -> str:
        return self._string(0)