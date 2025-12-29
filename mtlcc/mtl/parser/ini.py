## simple INI parser. reads sections and properties and pushes them into a list.
## because CNS allows duplicates of section and property names, this parser must also permit this.
from typing import List, Optional

from mtl.types.ini import *
from mtl.types.shared import TranslationError

# find any comment (delimited by `;`) and produce a line with it removed.
def remove_comment(line: str, ctx: INIParserContext) -> str:
    result = ""

    index = 0
    in_string = False
    while index < len(line):
        c = line[index]

        if c == ";" and not in_string:
            break
        elif c == "\\" and line[index+1] == "\"":
            result += "\\\""
            index += 2
            continue
        elif c == "\"":
            in_string = not in_string

        result += c
        index += 1
    
    if in_string:
        raise TranslationError("String literals must be terminated on the same line with a closing quote character.", ctx.location)

    return result

# INI section name and comment are separated by a comma.
def read_header(line: str, ctx: INIParserContext) -> tuple[str, str]:
    if "," not in line: return (line, "")
    return (line.split(",")[0].strip(), ",".join(line.split(",")[1:]).strip())

# INI property name and value are separated by equals.
def read_pair(line: str, ctx: INIParserContext) -> tuple[str, str]:
    if "=" not in line: raise TranslationError("Properties must contain a key and a value separated by an equals character.", ctx.location)
    return (line.split("=")[0].strip(), "=".join(line.split("=")[1:]).strip())

def parse(content: str, ctx: INIParserContext) -> List[INISection]:
    result: List[INISection] = []
    current: Optional[INISection] = None

    lines = content.replace("\r\n", "\n").split("\n")
    for line in lines:
        ctx.location.line += 1
        line = remove_comment(line, ctx).strip().strip('\xef\xbb\xbf')
        if len(line) == 0: continue
        
        if line.startswith("[") and line.endswith("]"):
            if current != None: result.append(current)
            line = line[1:-1]
            (section_name, section_comment) = read_header(line, ctx)
            current = INISection(section_name, section_comment, [], Location(ctx.location.filename, ctx.location.line))
        elif current != None:
            (property_name, property_value) = read_pair(line, ctx)
            current.properties.append(INIProperty(property_name, property_value, Location(ctx.location.filename, ctx.location.line)))
        else:
            raise TranslationError("INI files must begin with a section header enclosed in square braces.", ctx.location)

    if current != None: result.append(current)

    return result