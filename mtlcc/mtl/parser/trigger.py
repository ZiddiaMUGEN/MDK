from typing import Optional

from mtl.types.trigger import TriggerTree, TriggerTreeNode
from mtl.types.shared import Location, TranslationError

PRECEDENCE = {
    "**": 2,
    "*": 3,
    "/": 3,
    "%": 3,
    "+": 4,
    "-": 4,
    ">": 5,
    ">=": 5,
    "<": 5,
    "<=": 5,
    "=": 6,
    "!=": 6,
    ":=": 7,
    "&": 8,
    "^": 9,
    "|": 10,
    "&&": 11,
    "^^": 12,
    "||": 13
}

def parseTrigger(line: str, location: Location) -> TriggerTree:
    try:
        result = parseExpression(line, location)
        return result[1]
    except TranslationError as te:
        raise te
    except:
        raise TranslationError("Failed to parse trigger to a syntax tree.", location)
    
def consumeWhitespace(line: str, index: int) -> int:
    while index < len(line) and line[index] in [" ", "\t"]: index += 1
    return index

def buildStructAccess(fields: list[str], location: Location) -> TriggerTree:
    if len(fields) == 2:
        return TriggerTree(TriggerTreeNode.STRUCT_ACCESS, "", [
            TriggerTree(TriggerTreeNode.ATOM, fields[0], [], location),
            TriggerTree(TriggerTreeNode.ATOM, fields[1], [], location)
        ], location)
    return TriggerTree(TriggerTreeNode.STRUCT_ACCESS, "", [
        buildStructAccess(fields[:-1], location),
        TriggerTree(TriggerTreeNode.ATOM, fields[-1], [], location)
    ], location)

def parseToken(line: str, index: int, location: Location, nested: bool = False) -> tuple[int, Optional[TriggerTree]]:
    # attempt to read a token. token is anything which is not an operator.
    token = ""
    index = consumeWhitespace(line, index)
    while index < len(line) and line[index] not in ["!", "~", "-", "+", "*", "/", "%", ">", "<", "=", ":", "&", "^", "|", "(", "[", "]", ")", ",", "'", "\""]:
        token += line[index]
        index += 1
        #index = consumeWhitespace(line, index)
    ## no token read? empty expression OR starts with an operator
    token = token.strip()
    if token == "":
        return (index, None)
    ## potential struct access
    if " " in token:
        splitted = token.split(" ")
        result = buildStructAccess(splitted, location)
        return (index, result)
    return (index, TriggerTree(TriggerTreeNode.ATOM, token, [], location))

def parseUnary(line: str, index: int, location: Location, nested: bool = False) -> tuple[int, Optional[TriggerTree]]:
    index = consumeWhitespace(line, index)
    ## only care about unary operators.
    if line[index] not in ["!", "~", "-"]:
        return (index, None)
    ## fetch the operator.
    operator = line[index]
    index += 1
    ## parse the expression under the operator.
    (index, nextExprn) = parseExpression(line, location, index, nested)
    if nextExprn == None:
        raise TranslationError(f"Trigger parser failed to resolve a trigger for unary operator {operator}.", location)
    if nextExprn.node == TriggerTreeNode.MULTIVALUE:
        # move the unary inside the multivalue.
        nextExprn.children[0] = TriggerTree(TriggerTreeNode.UNARY_OP, operator, [nextExprn.children[0]], location)
        return (index, nextExprn)
    elif nextExprn.node == TriggerTreeNode.BINARY_OP:
        # move the unary inside the binary op.
        nextExprn.children[0] = TriggerTree(TriggerTreeNode.UNARY_OP, operator, [nextExprn.children[0]], location)
        return (index, nextExprn)
    return (index, TriggerTree(TriggerTreeNode.UNARY_OP, operator, [nextExprn], location))

def parseBracketed(line: str, index: int, location: Location, nested: bool = False, fn: bool = False) -> tuple[int, Optional[TriggerTree]]:
    index = consumeWhitespace(line, index)
    ## only care about interval/subexpression
    if line[index] not in ["(", "["]:
        return (index, None)
    ## fetch the operator.
    operator = line[index]
    index += 1
    ## parse the expression under the operator.
    (index, nextExprn) = parseExpression(line, location, index, nested = True)
    if nextExprn == None:
        raise TranslationError(f"Trigger parser failed to resolve a trigger for interval/subexpression operator {operator}.", location)
    ## now confirm the operator was closed.
    if line[index] not in [")", "]"]:
        raise TranslationError(f"Trigger parser bracketed expression was not closed correctly.", location)
    operator += line[index]
    index += 1
    
    ## MULTIVALUE implies expr1, expr2 (so interval)
    if nextExprn.node == TriggerTreeNode.MULTIVALUE and not fn:
        return (index, TriggerTree(TriggerTreeNode.INTERVAL_OP, operator, nextExprn.children, location))
    if operator != "()":
        raise TranslationError(f"Couldn't determine type of bracketed operator: operator is {operator}, but child node is {nextExprn.node}.", location)
    nextExprn.precedence = True
    return (index, nextExprn)

def parseBinary(line: str, index: int, location: Location, lhs: TriggerTree, nested: bool = False) -> tuple[int, Optional[TriggerTree]]:
    index = consumeWhitespace(line, index)
    ## only care about binary operators.
    if line[index] not in ["!", "-", "+", "*", "/", "%", ">", "<", "=", ":", "&", "^", "|"]:
        return (index, None)
    ## fetch the operator
    operator = line[index]
    index += 1
    ## handle each multi-character binary operator.
    if operator == "!" and line[index] != "=":
        return (index, None)
    elif operator == "!" and line[index] == "=":
        operator = "!="
        index += 1
    if operator == "*" and line[index] == "*":
        operator = "**"
        index += 1
    if operator == ">" and line[index] == "=":
        operator = ">="
        index += 1
    if operator == "<" and line[index] == "=":
        operator = "<="
        index += 1
    if operator == ":" and line[index] != "=":
        return (index, None)
    elif operator == ":" and line[index] == "=":
        operator = ":="
        index += 1
    if operator == "&" and line[index] == "&":
        operator = "&&"
        index += 1
    if operator == "|" and line[index] == "|":
        operator = "||"
        index += 1
    if operator == "^" and line[index] == "^":
        operator = "^^"
        index += 1
    ## parse the expression under the operator.
    (index, nextExprn) = parseExpression(line, location, index, nested)
    if nextExprn == None:
        raise TranslationError(f"Trigger parser failed to resolve the right hand side of binary operator {operator}.", location)
    
    ## we must apply precedence rules.
    ## this means the tree needs to be rebalanced depending on precedence levels of the nested operator.
    ## because this gets called for each tree, we can just deal with the direct children.
    my_precedence = PRECEDENCE[operator] if operator in PRECEDENCE else 99
    rhs_precedence = 99
    if nextExprn.node == TriggerTreeNode.BINARY_OP:
        rhs_precedence = PRECEDENCE[nextExprn.operator] if nextExprn.operator in PRECEDENCE else 99
    elif nextExprn.node == TriggerTreeNode.INTERVAL_OP:
        rhs_precedence = 6
    elif nextExprn.node == TriggerTreeNode.UNARY_OP:
        rhs_precedence = -1
    elif nextExprn.node == TriggerTreeNode.ATOM:
        rhs_precedence = 0
    
    if nextExprn.precedence:
        rhs_precedence = 0
    if lhs.precedence:
        my_precedence = 0

    if lhs.precedence and nextExprn.precedence:
        return (index, TriggerTree(TriggerTreeNode.BINARY_OP, operator, [lhs, nextExprn], location))

    ## if this node has higher precedence, rebalance.
    ## TODO: need to support other ops here?
    if my_precedence <= rhs_precedence and nextExprn.node == TriggerTreeNode.BINARY_OP:
        new_child = TriggerTree(TriggerTreeNode.BINARY_OP, operator, [lhs, nextExprn.children[0]], location)
        new_root = TriggerTree(TriggerTreeNode.BINARY_OP, nextExprn.operator, [new_child, nextExprn.children[1]], location)
        return (index, new_root)
    elif nextExprn.node == TriggerTreeNode.MULTIVALUE:
        if lhs.node == TriggerTreeNode.ATOM and lhs.operator.lower() == "hitdefattr":
            ## special case: this is the ONLY builtin trigger which returns a tuple.
            ## if we ever implement user-defined triggers which return a tuple, something smarter will need to be added.
            return (index, TriggerTree(TriggerTreeNode.BINARY_OP, operator, [lhs, nextExprn], location))
        else:
            new_child = TriggerTree(TriggerTreeNode.BINARY_OP, operator, [lhs, nextExprn.children[0]], location)
            new_root = TriggerTree(TriggerTreeNode.MULTIVALUE, nextExprn.operator, [new_child] + nextExprn.children[1:], location)
        return (index, new_root)

    return (index, TriggerTree(TriggerTreeNode.BINARY_OP, operator, [lhs, nextExprn], location))

def parseString(line: str, index: int, location: Location, nested: bool = False) -> tuple[int, Optional[TriggerTree]]:
    index = consumeWhitespace(line, index)
    ## only care about quoted tokens.
    if line[index] not in ["\"", "'"]:
        return (index, None)
    ## skip the operator.
    index += 1
    ## read until finding closing quote.
    string = ""
    while index < len(line):
        if line[index] == "\\" and index + 1 < len(line) and line[index + 1] == "\"":
            string += line[index]
            string += line[index + 1]
            index += 2
            continue
        if line[index] == "\"":
            break
        string += line[index]
        index += 1
    if line[index] != "\"":
        raise TranslationError("Encountered an unterminated string during parsing.", location)
    index += 1

    return (index, TriggerTree(TriggerTreeNode.ATOM, f"\"{string}\"", [], location))

def parseMultiValue(line: str, index: int, location: Location, lhs: TriggerTree, nested: bool = False) -> tuple[int, Optional[TriggerTree]]:
    index = consumeWhitespace(line, index)
    if index >= len(line):
        return (index, None)
    ## only care about interval/subexpression
    if line[index] != ",":
        return (index, None)
    ## fetch the operator.
    operator = line[index]
    index += 1
    ## parse the expression under the operator.
    (index, nextExprn) = parseExpression(line, location, index, nested = True)
    if nextExprn == None:
        raise TranslationError(f"Trigger parser failed to resolve a trigger for interval/subexpression operator {operator}.", location)
    
    ## this needs to also handle redirects.
    if (lhs.node == TriggerTreeNode.ATOM and lhs.operator.lower() in ["parent", "root", "helper", "target", "partner", "enemy", "enemynear"]) or \
       (lhs.node == TriggerTreeNode.FUNCTION_CALL and lhs.operator.lower() in ["helper", "target", "enemy", "enemynear", "playerid", "rescope"]):
        if nextExprn.node == TriggerTreeNode.ATOM or nextExprn.node == TriggerTreeNode.FUNCTION_CALL or nextExprn.node == TriggerTreeNode.STRUCT_ACCESS:
            return (index, TriggerTree(TriggerTreeNode.REDIRECT, "", [lhs, nextExprn], location))
        elif nextExprn.node == TriggerTreeNode.BINARY_OP:
            redirected = TriggerTree(TriggerTreeNode.REDIRECT, "", [lhs, nextExprn.children[0]], location)
            return (index, TriggerTree(TriggerTreeNode.BINARY_OP, nextExprn.operator, [redirected] + nextExprn.children[1:], location))
        elif nextExprn.node == TriggerTreeNode.MULTIVALUE:
            ## this can happen in e.g. a Cond expression:
            ## Cond(NumHelper(16000), Helper(16000),SpyStorage_AnimationSearchState, -1)
            redirected = TriggerTree(TriggerTreeNode.REDIRECT, "", [lhs, nextExprn.children[0]], location)
            return (index, TriggerTree(TriggerTreeNode.MULTIVALUE, "", [redirected] + nextExprn.children[1:], location))
        else:
            raise Exception(f"Target of trigger redirection must be function, atom, or binary operator, not {nextExprn.node}")
    
    if nextExprn.node == TriggerTreeNode.MULTIVALUE:
        nextExprn.children.insert(0, lhs)
        return (index, nextExprn)
    return (index, TriggerTree(TriggerTreeNode.MULTIVALUE, "", [lhs, nextExprn], location))

def parseExpression(line: str, location: Location, index: int = 0, nested: bool = False) -> tuple[int, TriggerTree]:
    stack: list[TriggerTree] = []
    # strip leading whitespace
    index = consumeWhitespace(line, index)
    ## there are a few possible cases at the start of parsing:
    ## token
    ## unary expression
    ## interval/subexpression (bracketed)
    ## string expression (quoted)
    ## we start by checking token, then determine unary vs bracketed.
    while index < len(line):
        # special handling: if we reach a ']' or ')' and the expression is nested, exit.
        if line[index] in ["]", ")"] and nested:
            break

        (index, nextToken) = parseToken(line, index, location, nested)
        if nextToken != None: stack.append(nextToken)

        # early exit if we reached the end.
        if index >= len(line):
            break

        # if the token was None, then no token was parsed.
        # handle the unary and interval expressions.
        if nextToken == None:
            (index, nextOperator) = parseUnary(line, index, location, nested)
            if nextOperator != None: 
                stack.append(nextOperator)
            else:
                function_call = len(stack) == 1 and stack[0].node == TriggerTreeNode.ATOM
                (index, nextExpression) = parseBracketed(line, index, location, nested, fn = function_call)
                if nextExpression != None and function_call:
                    ## special case: function call. ATOM (BRACKETED)
                    if nextExpression.node in [TriggerTreeNode.MULTIVALUE]:
                        children = nextExpression.children
                    else:
                        children = [nextExpression]
                    ## special case for the `rescope` function, which will often have a REDIRECT expression as its sole child
                    ## that REDIRECT needs to be converted to two arguments.
                    if stack[0].operator.lower() == "rescope" and len(children) == 1 and children[0].node == TriggerTreeNode.REDIRECT:
                        children = [children[0].children[0], children[0].children[1]]
                    stack.append(TriggerTree(TriggerTreeNode.FUNCTION_CALL, stack.pop().operator, children, location))
                elif nextExpression != None: 
                    stack.append(nextExpression)
                else:
                    (index, nextExpression) = parseString(line, index, location, nested)
                    if nextExpression != None: 
                        stack.append(nextExpression)
                    else:
                        raise TranslationError("Could not determine type of trigger; tried atom, unary, interval, subexpr, string.", location)

        # early exit if we reached the end.
        if index >= len(line):
            break

        # read a potential binary operator
        (index, nextOperator) = parseBinary(line, index, location, stack[-1], nested)
        if nextOperator != None:
            stack.pop()
            stack.append(nextOperator)

        # read a potential redirect OR multivalue operator
        (index, nextOperator) = parseMultiValue(line, index, location, stack[-1], nested)
        if nextOperator != None:
            stack.pop()
            stack.append(nextOperator)

        # skip to next token
        index = consumeWhitespace(line, index)
    if len(stack) > 1:
        raise TranslationError("Trigger parser failed to resolve a single trigger.", location)
    if len(stack) == 0:
        stack.append(TriggerTree(TriggerTreeNode.ATOM, "", [], location))
    return (index, stack.pop())