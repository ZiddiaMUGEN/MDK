import sys

if len(sys.argv) < 4:
    raise Exception("need source, target, target_name arguments")

source = sys.argv[1]
target = sys.argv[2]
target_name = sys.argv[3]

with open(target, mode="w") as f:
    f.write(f"{target_name} = [\n")

    with open(source, mode="rb") as f2:
        indata = f2.read()

    index = 0
    for byte in indata:
        if index == 0:
            f.write('\t')
        f.write(hex(byte).upper() + ', ')
        index += 1
        if index == 8:
            index = 0
            f.write('\n')

    f.write("\n]")