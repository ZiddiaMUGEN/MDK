from mdk.types.specifier import TypeCategory, TypeSpecifier

## these are builtin types which must be available to all characters.
AnyType = TypeSpecifier("any", TypeCategory.BUILTIN) ## note: this is used for DTC and ATC. it's not intended for normal use.
IntType = TypeSpecifier("int", TypeCategory.BUILTIN)
FloatType = TypeSpecifier("float", TypeCategory.BUILTIN)
BoolType = TypeSpecifier("bool", TypeCategory.BUILTIN)
ShortType = TypeSpecifier("short", TypeCategory.BUILTIN)
ByteType = TypeSpecifier("byte", TypeCategory.BUILTIN)
CharType = TypeSpecifier("char", TypeCategory.BUILTIN)
## this is a type for an unquoted string. it basically is still a string,
## but instructs the compiler to not quote its output.
UStringType = TypeSpecifier("string", TypeCategory.BUILTIN)
StringType = TypeSpecifier("string", TypeCategory.BUILTIN)

StateNoType = TypeSpecifier("stateno", TypeCategory.BUILTIN)
AnimType = TypeSpecifier("anim", TypeCategory.BUILTIN)
SoundType = TypeSpecifier("sound", TypeCategory.BUILTIN)
SpriteType = TypeSpecifier("sprite", TypeCategory.BUILTIN)

__all__ = [
    "AnyType", "IntType", "FloatType", "BoolType", "ShortType", "ByteType", "CharType", "StringType",
    "StateNoType", "AnimType", "SoundType", "SpriteType", "UStringType"
]