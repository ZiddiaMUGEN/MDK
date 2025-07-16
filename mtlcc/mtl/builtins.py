from typing import List

from mtl.shared import TypeDefinition, TypeCategory

def getBaseTypes() -> List[TypeDefinition]:
    return [
        TypeDefinition("int", TypeCategory.BUILTIN, 32, [], "stdlib/builtins.inc", 0),
        TypeDefinition("float", TypeCategory.BUILTIN, 32, [], "stdlib/builtins.inc", 0),
        TypeDefinition("short", TypeCategory.BUILTIN, 16, [], "stdlib/builtins.inc", 0),
        TypeDefinition("byte", TypeCategory.BUILTIN, 8, [], "stdlib/builtins.inc", 0),
        TypeDefinition("char", TypeCategory.BUILTIN, 8, [], "stdlib/builtins.inc", 0),
        TypeDefinition("bool", TypeCategory.BUILTIN, 1, [], "stdlib/builtins.inc", 0),
        TypeDefinition("StateType", TypeCategory.STRING_ENUM, 32, ["S", "C", "A", "L", "U"], "stdlib/builtins.inc", 0),
        TypeDefinition("MoveType", TypeCategory.STRING_ENUM, 32, ["A", "I", "H", "U"], "stdlib/builtins.inc", 0),
        TypeDefinition("PhysicsType", TypeCategory.STRING_ENUM, 32, ["S", "C", "A", "N", "U"], "stdlib/builtins.inc", 0),
        TypeDefinition("HitType", TypeCategory.STRING_FLAG, 32, ["S", "C", "A"], "stdlib/builtins.inc", 0),
        TypeDefinition("HitAttr", TypeCategory.STRING_FLAG, 32, ["N", "S", "H", "A", "T"], "stdlib/builtins.inc", 0),
    ]