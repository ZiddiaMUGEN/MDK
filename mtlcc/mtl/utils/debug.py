from typing import Any, Optional

from mtl.types.shared import Location, DebugCategory
from mtl.types.translation import AllocationTable, TypeParameter, TypeDefinition, TriggerDefinition, TemplateDefinition, StateDefinition
from mtl.types.builtins import BUILTIN_FLOAT
from mtl.types.context import DebuggingContext, DebugStateInfo, CompilerConfiguration

from mtl.utils.func import mask_variable, get_all

def get_state_by_id(id: int, ctx: DebuggingContext) -> Optional[DebugStateInfo]:
    matches = get_all(ctx.states, lambda k: k.id == id)
    if len(matches) == 0:
        return None
    if len(matches) > 2:
        return None
    if len(matches) == 1:
        return matches[0]
    return next(filter(lambda k: not k.is_common, matches), None)

def debuginfo(cat: DebugCategory, data: Any, cc: CompilerConfiguration) -> list[str]:
    if cc.no_compiler_internal: return []
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
    elif cat == DebugCategory.STATEDEF:
        return debuginfo_statedef(data)
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

def debuginfo_statedef(data: StateDefinition) -> list[str]:
    results: list[str] = []
    results.append(f";!mtl-debug STATEDEF {data.name} {data.parameters.id}")
    return results