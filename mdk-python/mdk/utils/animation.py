from mdk.resources.animation import Animation, Sequence, Frame, AnimationFlip, Clsn

def read_animations(anim_path: str) -> list[Animation]:
    animations: list[Animation] = []
    with open(anim_path) as f:
        content = f.readlines()
        current_anim: Animation | None = None
        next_loop: bool = False
        clsns: list[dict] = []
        clsns_default: bool = False
        for line in content:
            # skip/eliminate comments
            if line.strip().startswith(";"):
                continue
            line = line.strip().split(';')[0]
            
            if line.strip().lower().startswith("[begin action "):
                target_index = line.strip().lower()[14:].split(']')[0].strip()
                print(f"Discovered new external animation with ID {target_index}")
                if current_anim != None and current_anim._id != None:
                    animations.append(current_anim)
                current_anim = Animation(frames = [], id = int(target_index), external = False)
                next_loop = False
                clsns_default = False
                clsns = []
            elif line.strip().lower() == "loopstart":
                next_loop = True
            elif line.strip().lower().startswith("clsn1default:") or line.strip().lower().startswith("clsn2default:"):
                ## mark upcoming CLSNs as default
                clsns_default = True
            elif line.strip().lower().startswith("clsn1:") or line.strip().lower().startswith("clsn2:"):
                ## mark upcoming CLSNs as non-default
                clsns_default = False
            elif line.strip().lower().startswith("clsn1["):
                ## read clsn
                data = [int(x.strip()) for x in line.strip().split("=")[1].split(",")]
                clsns.append({
                    "data": data,
                    "default": clsns_default,
                    "type": 1
                })
            elif line.strip().lower().startswith("clsn2["):
                ## read clsn
                data = [int(x.strip()) for x in line.strip().split("=")[1].split(",")]
                clsns.append({
                    "data": data,
                    "default": clsns_default,
                    "type": 2
                })
            elif "," in line and current_anim != None and current_anim._frames != None:
                params = [s.strip().lower() for s in line.split(",")]
                if len(params) < 5: continue
                next_frame = Frame(int(params[0]), int(params[1]))
                next_frame.offset((int(params[2]), int(params[3])))
                next_frame.length(int(params[4]))
                if len(params) >= 6 and params[5] != "":
                    flip = AnimationFlip.NONE
                    if params[5] == "H": flip = AnimationFlip.HORIZONTAL
                    if params[5] == "V": flip = AnimationFlip.VERTICAL
                    if params[5] == "VH" or params[5] == "HV": flip = AnimationFlip.BOTH
                    if flip != AnimationFlip.NONE: next_frame.flip(flip)
                if len(params) >= 7 and params[6] != "":
                    next_frame._trans = params[6]
                if len(params) >= 9 and params[7] != "" and params[8] != "":
                    next_frame.scale((float(params[7]), float(params[8])))
                if len(params) >= 10 and params[9] != "":
                    next_frame.rotate(int(params[9]))
                if next_loop:
                    next_frame.loop()
                    next_loop = False
                for clsn in clsns:
                    if clsn['type'] == 1:
                        next_frame.clsn1(Clsn(clsn['data'][0], clsn['data'][1], clsn['data'][2], clsn['data'][3], clsn['default']))
                    elif clsn['type'] == 2:
                        next_frame.clsn2(Clsn(clsn['data'][0], clsn['data'][1], clsn['data'][2], clsn['data'][3], clsn['default']))
                    else:
                        raise Exception(f"Unrecognized external clsn type {clsn['type']}")
                current_anim._frames._frames.append(next_frame)
                clsns_default = False
                clsns = []
        if current_anim != None and current_anim._id != None:
            animations.append(current_anim)
    return animations