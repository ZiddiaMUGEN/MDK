MDK = MUGEN Development Kit.
Offers several alternative development experiences for MUGEN characters.

tMUGEN - Templated MUGEN. The compiler source is provided under `tmcc`. Syntactically similar to CNS but with additional constructs such as loops, imports, and custom state controller types. Is also type-checked at compilation to help identify issues.
pyMUGEN - MUGEN code written in Python. The underlying MDK implementation compiles first to tMUGEN, and then invokes the tMUGEN compiler to generate CNS.
