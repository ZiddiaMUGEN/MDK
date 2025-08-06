from io import BufferedWriter, BufferedReader
from typing import Optional

from mtl.types.shared import Location
from mtl.types.trigger import TriggerTree, TriggerTreeNode

def write_integer(val: int, f: BufferedWriter):
    f.write(val.to_bytes(length = 4, byteorder = 'little', signed = True))

def write_short(val: int, f: BufferedWriter):
    f.write(val.to_bytes(length = 2, byteorder = 'little', signed = True))

def write_byte(val: int, f: BufferedWriter):
    f.write(val.to_bytes(length = 1, byteorder = 'little', signed = True))

def write_string(val: str, f: BufferedWriter):
    write_short(len(val), f)
    f.write(val.encode("utf-8"))

def write_tree(val: TriggerTree, f: BufferedWriter):
    write_byte(val.node.value, f)
    write_string(val.operator, f)
    write_byte(len(val.children), f)
    for child in val.children:
        write_tree(child, f)

def read_integer(f: BufferedReader) -> int:
    return int.from_bytes(f.read(4), byteorder='little', signed=True)

def read_short(f: BufferedReader) -> int:
    return int.from_bytes(f.read(2), byteorder='little', signed=True)

def read_byte(f: BufferedReader) -> int:
    return int.from_bytes(f.read(1), byteorder='little', signed=True)

def read_string(f: BufferedReader) -> str:
    length = read_short(f)
    return f.read(length).decode("utf-8")

def read_tree(f: BufferedReader, l: Location) -> Optional[TriggerTree]:
    cat_value = read_byte(f)
    if cat_value == -2: return None
    category = TriggerTreeNode(cat_value)
    operator = read_string(f)
    child_count = read_byte(f)
    children: list[TriggerTree] = []
    for _ in range(child_count):
        result = read_tree(f, l)
        if result != None: children.append(result)
    return TriggerTree(category, operator, children, l)