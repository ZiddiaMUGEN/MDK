;; Standard include file for MTL. This is used by mtlcc to build CNS files.
;; libmtl.inc is included by default by mtlcc.
;; there are many built-ins which are exposed in `mtl/builtins.py` instead.
;; This file is mostly for useful functions and operators which we want to make available in MTL.

;;;;; Fundamental Type Conversion
;; Specific conversions between fundamental types receive trigger definitions.
[Define Trigger]
name = parseBool
type = bool
value = !!input

[Define Parameters]
input = int