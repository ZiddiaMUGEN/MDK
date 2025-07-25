;; Standard include file for MTL. This is used by mtlcc to build CNS files.
;; libmtl.inc is included by default by mtlcc.
;; We try to put as many definitions as we can in this file. However there are many built-ins which are exposed in `mtl/builtins.py` instead.

;;;;; Fundamental Type Definitions
;; The int, float, short, byte, char, and bool types are built-in. Some aliases and unions are defined here.
[Define Type]
name = bool8
type = alias
source = byte

[Define Type]
name = SparkIndex
type = union
member = int
member = cint

[Define Type]
name = HitString
type = alias
source = HitType,HitAttr...?

;;;;; Fundamental Type Conversion
;; Specific conversions between fundamental types receive trigger definitions.
[Define Trigger]
name = parseBool
type = bool
value = !!input

[Define Parameters]
input = int

;;;;; Reflection Const Triggers
;; These provide access into compiler state and type information.
;[Define Trigger]
