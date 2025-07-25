# MDK: MUGEN Development Kit

MDK is a specification which describes extensions to MUGEN's character code (CNS). Specific implementations of the MDK specification then allow character authors to use the new features provided by the specification to build their characters.

An important part of MDK is that it is language-agnostic, and although examples in the MDK spec use MUGEN's default CNS syntax, implementations of the MDK spec can be provided in any language.

This repo provides 2 implementations of the MDK spec:

- MTL, standing for MUGEN Template Language, which is a direct extension of the CNS syntax
- mdk-python, an implementation of the MDK specification in Python

Character authors can use MTL to write in the familiar CNS/INI syntax while also taking advantage of new features from the MDK spec; or, they can choose to write in Python, offering a more developer-friendly experience.

Reference `SPEC.md` for the details of the MDK spec.