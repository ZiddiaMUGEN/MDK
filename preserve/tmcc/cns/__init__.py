## parses a CNS file containing statedef/controller data.
def parse_cns(path):
    with open(path) as f:
        content = f.read()
    