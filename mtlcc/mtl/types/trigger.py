from dataclasses import dataclass
from enum import Enum

from mtl.types.shared import Location

class TriggerTreeNode(Enum):
    MULTIVALUE = -1
    UNARY_OP = 0
    BINARY_OP = 1
    INTERVAL_OP = 2
    FUNCTION_CALL = 3
    ATOM = 4
    STRUCT_ACCESS = 5

@dataclass
class TriggerTree:
    node: TriggerTreeNode
    operator: str
    children: list['TriggerTree']
    location: Location

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
        return result

    def __repr__(self) -> str:
        return self._string(0)