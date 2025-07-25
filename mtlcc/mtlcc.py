import argparse
import traceback

from mtl import loader, translator
from mtl.utils.compiler import TranslationError

if __name__ == "__main__":
    ## TODO: need a project file. need to be able to parse AIR, SPR, SND and multiple MTL/CNS files.
    parser = argparse.ArgumentParser(prog='mtlcc', description='Translation tool from MTL templates into CNS character code')
    parser.add_argument('input', help='Path to the MTL template to translate')

    args = parser.parse_args()
    ## note: the spec states that translation of included files should stop at step 3.
    ## this is guaranteed by having steps up to 3 in `loadFile`, and remaining steps handled in `translateContext`.
    try:
        loadContext = loader.loadFile(args.input, [])
        translated = translator.translateContext(loadContext)
    except TranslationError as exc:
        py_exc = traceback.format_exc().split("\n")[-4].strip()
        print("Translation terminated with an error.")
        print(f"\t{exc.message}")
        print(f"mtlcc exception source: {py_exc}")