from typing import Optional

from mdk.types.specifier import TypeSpecifier

## this is based on the MTL type conversion function in mtl.utils.compiler.
def check_types_assignable(spec1: TypeSpecifier, spec2: TypeSpecifier) -> Optional[TypeSpecifier]:
    ## if types match, t1 return the type.
    if spec1 == spec2: return spec1

    ## `int` is implicitly convertible to `float`
    if spec1.name == "int" and spec2.name == "float":
        return spec2
    
    ## allow this, because Python is pretty permissive with numerics.
    if spec1.name == "float" and spec2.name == "int":
        return spec1
        #raise Exception("Conversion from float to int may result in loss of precision. If this is intended, use functions like ceil or floor to convert, or explicitly cast one side of the expression.")
    
    ## widening
    if spec1.name == "bool" and spec2.name in ["byte", "short", "int"]:
        return spec2
    if spec1.name == "byte" and spec2.name in ["short", "int"]:
        return spec2
    if spec1.name == "short" and spec2.name in ["int"]:
        return spec2
    
    ## implicit char -> byte
    if spec1.name == "char" and spec2.name in ["byte"]:
        return spec2

    return None

def check_any_assignable(spec1: TypeSpecifier, spec2: list[TypeSpecifier]) -> Optional[TypeSpecifier]:
    for s in spec2:
        if (assgn := check_types_assignable(spec1, s)) != None:
            return assgn
    return None