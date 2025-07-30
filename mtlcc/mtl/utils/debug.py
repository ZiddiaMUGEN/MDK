from typing import Any

from mtl.types.shared import Location
from mtl.types.translation import AllocationTable, TypeParameter, TypeDefinition, TriggerDefinition, TemplateDefinition
from mtl.types.debug import DebugCategory
from mtl.types.builtins import BUILTIN_FLOAT

from mtl.utils.func import mask_variable

def debuginfo(cat: DebugCategory, data: Any) -> list[str]:
    if cat == DebugCategory.VERSION_HEADER:
        return debuginfo_header(data)
    elif cat == DebugCategory.VARIABLE_TABLE:
        return debuginfo_table(data)
    elif cat == DebugCategory.VARIABLE_ALLOCATION:
        return debuginfo_allocation(data)
    elif cat == DebugCategory.TYPE_DEFINITION:
        return debuginfo_type(data)
    elif cat == DebugCategory.TRIGGER_DEFINITION:
        return debuginfo_trigger(data)
    elif cat == DebugCategory.LOCATION:
        return debuginfo_location(data)
    else:
        raise Exception(f"Can't handle debuginfo for category {cat}, data {data}")
    
def debuginfo_header(data: str) -> list[str]:
    return [f";!mtl-debug VERSION_HEADER {data}"]

def debuginfo_location(data: Location) -> list[str]:
    return [f";!mtl-debug LOCATION {data}"]

def debuginfo_type(data: TypeDefinition) -> list[str]:
    results: list[str] = []
    category = str(data.category).replace("TypeCategory.", "")
    results.append(f";!mtl-debug TYPE_DEFINITION {data.name} {category} {data.size} {data.location}")
    if len(data.members) > 0:
        for member in data.members:
            results.append(f";!mtl-debug-next {member}")
    return results

def debuginfo_trigger(data: TriggerDefinition) -> list[str]:
    results: list[str] = []
    results.append(f";!mtl-debug TRIGGER_DEFINITION {data.name} {data.type.name} {data.location}")
    if len(data.params) > 0:
        for param in data.params:
            results.append(f";!mtl-debug-next {param.name} {param.type}")
    return results

def debuginfo_table(data: dict) -> list[str]:
    results: list[str] = []
    results.append(f";!mtl-debug VARIABLE_TABLE {data['scope'].type} {data['scope'].target} {data['allocations'].max_size}")
    for alloc in data['allocations'].data:
        results.append(f";!mtl-debug-next {alloc} {data['allocations'].data[alloc]}")
    return results

def debuginfo_allocation(data: TypeParameter) -> list[str]:
    results: list[str] = []
    results.append(f";!mtl-debug VARIABLE_ALLOCATION {data.name} {data.type.name} {data.location}")
    for alloc in data.allocations:
        results.append(f";!mtl-debug-next {alloc[0]} {alloc[1]} {mask_variable(alloc[0], alloc[1], data.type.size, data.type == BUILTIN_FLOAT)}")
    return results