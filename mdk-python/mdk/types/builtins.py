from mdk.types.specifier import TypeCategory, TypeSpecifier

## these are builtin types which must be available to all characters.
IntType = TypeSpecifier("int", TypeCategory.BUILTIN)
FloatType = TypeSpecifier("float", TypeCategory.BUILTIN)
BoolType = TypeSpecifier("bool", TypeCategory.BUILTIN)
ShortType = TypeSpecifier("short", TypeCategory.BUILTIN)
ByteType = TypeSpecifier("byte", TypeCategory.BUILTIN)
CharType = TypeSpecifier("char", TypeCategory.BUILTIN)
StringType = TypeSpecifier("string", TypeCategory.BUILTIN)

StateNoType = TypeSpecifier("stateno", TypeCategory.BUILTIN)
AnimType = TypeSpecifier("anim", TypeCategory.BUILTIN)
SoundType = TypeSpecifier("sound", TypeCategory.BUILTIN)
SpriteType = TypeSpecifier("sprite", TypeCategory.BUILTIN)

__all__ = [
    "IntType", "FloatType", "BoolType", "ShortType", "ByteType", "CharType", "StringType",
    "StateNoType", "AnimType", "SoundType", "SpriteType"
]