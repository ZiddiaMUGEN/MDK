from lark import Lark, Token
from lark.visitors import Visitor_Recursive
from lark.tree import Tree

from mtl.utils.compiler import TranslationError
from mtl.types.trigger import TriggerTree, TriggerTreeNode
from mtl.types.shared import Location

trigger_grammar = Lark(
    """
    start: unary (COMMA unary)*
    unary: UNARY_OP? exponent
    exponent: multi
        | exponent EXP_OP multi
    multi: add
        | multi MULTI_OP add
    add: comp
        | add ADD_OP comp
    comp: eq
        | comp COMP_OP eq
    eq: assign
        | eq EQ_OP assign
        | OPEN_INTERVAL eq COMMA assign CLOSE_INTERVAL
    assign: and_op
        | assign WALRUS and_op
    and_op: xor
        | and_op AND_OP xor
    xor: or_op
        | xor XOR_OP or_op
    or_op: log_and
        | or_op OR_OP log_and
    log_and: log_xor
        | log_and LOG_AND_OP log_xor
    log_xor: log_or
        | log_xor LOG_XOR_OP log_or
    log_or: function
        | log_or LOG_OR_OP function
    function: atom
        | TOKEN LBRACKET (atom (COMMA atom)*)? RBRACKET

    atom: NUMBER
        | TOKEN
        | STRING
        |
        | unary
        | LBRACKET unary RBRACKET

    UNARY_OP: "!" | "~" | "-"
    EXP_OP: "**"
    MULTI_OP: "*" | "/" | "%"
    ADD_OP: "+" | "-"
    COMP_OP: ">" | ">=" | "<" | "<="
    EQ_OP: "=" | "!="
    WALRUS: ":="
    AND_OP: "&"
    XOR_OP: "^"
    OR_OP: "|"
    LOG_AND_OP: "&&"
    LOG_XOR_OP: "^^"
    LOG_OR_OP: "||"

    OPEN_INTERVAL: "(" | "["
    CLOSE_INTERVAL: ")" | "]"

    LBRACKET: "("
    RBRACKET: ")"
    COMMA: ","
    TOKEN: (CNAME) (CNAME|"-"|"+"|" "|".")*
    STRING: QUOTE CNAME QUOTE

    QUOTE: "\\""
    
    %import common.NUMBER
    %import common.CNAME
    %ignore " "
    """
)

def recursiveReverse(tree: TriggerTree):
    tree.children.reverse()
    for child in tree.children:
        recursiveReverse(child)

def parseTrigger(line: str, location: Location) -> TriggerTree:
    try:
        tree = trigger_grammar.parse(line)
        flattened = TriggerVisitor(location)
        flattened.visit(tree)
        if len(flattened.stack) != 1:
            raise TranslationError("Failed to identify a single node from trigger input.", location)
        result = flattened.stack[0]
        recursiveReverse(result)
        return result
    except TranslationError as te:
        raise te
    except:
        raise TranslationError("Failed to parse trigger to a syntax tree.", location)
    
class TriggerVisitor(Visitor_Recursive[Token]):
    def __init__(self, location: Location):
        self.stack: list[TriggerTree] = []
        self.location = location
        super().__init__()

    def start(self, tree: Tree[Token]):
        values: list[TriggerTree] = []
        while len(self.stack) != 0:
            values.append(self.stack.pop())
        self.stack.append(TriggerTree(TriggerTreeNode.MULTIVALUE, "", values, self.location))

    def unary(self, tree: Tree[Token]):
        if len(tree.children) == 2 and isinstance(tree.children[0], Token):
            if len(self.stack) < 1:
                raise TranslationError("Trigger parsing encountered unary operator with less than 1 operand.", self.location)
            operator = tree.children[0]
            self.stack.append(TriggerTree(TriggerTreeNode.UNARY_OP, str(operator), [self.stack.pop()], self.location))

    def parse_binary(self, tree: Tree[Token]):
        if len(tree.children) == 3 and isinstance(tree.children[1], Token):
            if len(self.stack) < 2:
                raise TranslationError("Trigger parsing encountered binary operator with less than 2 operands.", self.location)
            operator = tree.children[1]
            self.stack.append(TriggerTree(TriggerTreeNode.BINARY_OP, str(operator), [self.stack.pop(), self.stack.pop()], self.location))

    def exponent(self, tree: Tree[Token]):
        self.parse_binary(tree)

    def multi(self, tree: Tree[Token]):
        self.parse_binary(tree)

    def add(self, tree: Tree[Token]):
        self.parse_binary(tree)

    def comp(self, tree: Tree[Token]):
        self.parse_binary(tree)

    def eq(self, tree: Tree[Token]):
        if len(tree.children) == 5 and isinstance(tree.children[0], Token) and isinstance(tree.children[2], Token) and isinstance(tree.children[4], Token):
            if len(self.stack) < 2:
                raise TranslationError("Trigger parsing encountered interval operator with less than 2 operands.", self.location)
            operator = tree.children[0] + tree.children[4]
            self.stack.append(TriggerTree(TriggerTreeNode.INTERVAL_OP, str(operator), [self.stack.pop(), self.stack.pop()], self.location))
        else:
            self.parse_binary(tree)

    def assign(self, tree: Tree[Token]):
        self.parse_binary(tree)

    def and_op(self, tree: Tree[Token]):
        self.parse_binary(tree)

    def xor(self, tree: Tree[Token]):
        self.parse_binary(tree)

    def or_op(self, tree: Tree[Token]):
        self.parse_binary(tree)

    def log_and(self, tree: Tree[Token]):
        self.parse_binary(tree)

    def log_xor(self, tree: Tree[Token]):
        self.parse_binary(tree)
    
    def log_or(self, tree: Tree[Token]):
        self.parse_binary(tree)

    def function(self, tree: Tree[Token]):
        ## function will take 0 or more `atom` tokens as inputs.
        ## need to pop a tree from stack for each atom.
        if isinstance(tree.children[0], Token) and tree.children[0].type == "TOKEN":
            operands: list[TriggerTree] = []
            for child in tree.children:
                if isinstance(child, Tree) and child.data == "atom":
                    operands.append(self.stack.pop())
            self.stack.append(TriggerTree(TriggerTreeNode.FUNCTION_CALL, tree.children[0].value.strip(), operands, self.location))

    def atom(self, tree: Tree[Token]):
        if len(tree.children) == 0:
            self.stack.append(TriggerTree(TriggerTreeNode.ATOM, "", [], self.location))
        elif len(tree.children) == 3 and isinstance(tree.children[0], Token) and isinstance(tree.children[2], Token):
            ## atom carries the rule `LBRACKET unary RBRACKET` so we handle here.
            ## but the brackets are just to enforce precedence in the parser, we essentially don't need to do anything here!
            pass
        elif isinstance(tree.children[0], Token):
            ## structure access is separated by a space character.
            ## we want to be able to identify struct accesses.
            if " " in tree.children[0].value.strip():
                self.stack.append(TriggerTree(TriggerTreeNode.STRUCT_ACCESS, tree.children[0].value.strip(), [], self.location))
            else:
                self.stack.append(TriggerTree(TriggerTreeNode.ATOM, tree.children[0].value.strip(), [], self.location))