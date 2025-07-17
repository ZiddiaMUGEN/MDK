from typing import List

from lark import Lark, Token
from lark.visitors import Visitor_Recursive
from lark.tree import Tree

from mtl.error import TranslationError
from mtl.shared import TriggerTree, TriggerTreeNode

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

def parseTrigger(line: str, filename: str, lineno: int) -> TriggerTree:
    try:
        tree = trigger_grammar.parse(line)
        flattened = TriggerVisitor(filename, lineno)
        flattened.visit(tree)
        if len(flattened.stack) != 1:
            raise TranslationError("Failed to identify a single node from trigger input.", filename, lineno)
        return flattened.stack[0]
    except TranslationError as te:
        raise te
    except:
        raise TranslationError("Failed to parse trigger to a syntax tree.", filename, lineno)
    
class TriggerVisitor(Visitor_Recursive[Token]):
    def __init__(self, filename: str, lineno: int):
        self.stack: List[TriggerTree] = []
        self.filename = filename
        self.lineno = lineno
        super().__init__()

    def start(self, tree: Tree[Token]):
        values: List[TriggerTree] = []
        while len(self.stack) != 0:
            values.append(self.stack.pop())
        self.stack.append(TriggerTree(TriggerTreeNode.MULTIVALUE, "", values))

    def unary(self, tree: Tree[Token]):
        #print(tree)
        if len(tree.children) == 2 and isinstance(tree.children[0], Token):
            if len(self.stack) < 1:
                raise TranslationError("Trigger parsing encountered unary operator with less than 1 operand.", self.filename, self.lineno)
            operator = tree.children[0]
            self.stack.append(TriggerTree(TriggerTreeNode.UNARY_OP, str(operator), [self.stack.pop()]))

    def parse_binary(self, tree: Tree[Token]):
        if len(tree.children) == 3 and isinstance(tree.children[1], Token):
            if len(self.stack) < 2:
                raise TranslationError("Trigger parsing encountered binary operator with less than 2 operands.", self.filename, self.lineno)
            operator = tree.children[1]
            self.stack.append(TriggerTree(TriggerTreeNode.BINARY_OP, str(operator), [self.stack.pop(), self.stack.pop()]))

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
                raise TranslationError("Trigger parsing encountered interval operator with less than 2 operands.", self.filename, self.lineno)
            operator = tree.children[0] + tree.children[4]
            self.stack.append(TriggerTree(TriggerTreeNode.INTERVAL_OP, str(operator), [self.stack.pop(), self.stack.pop()]))
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
            operands: List[TriggerTree] = []
            for child in tree.children:
                if isinstance(child, Tree) and child.data == "atom":
                    operands.append(self.stack.pop())
            self.stack.append(TriggerTree(TriggerTreeNode.FUNCTION_CALL, tree.children[0].value, operands))

    def atom(self, tree: Tree[Token]):
        if len(tree.children) == 0:
            self.stack.append(TriggerTree(TriggerTreeNode.ATOM, "", []))
        elif len(tree.children) == 3 and isinstance(tree.children[0], Token) and isinstance(tree.children[2], Token):
            ## atom carries the rule `LBRACKET unary RBRACKET` so we handle here.
            ## but the brackets are just to enforce precedence in the parser, we essentially don't need to do anything here!
            pass
        elif isinstance(tree.children[0], Token):
            self.stack.append(TriggerTree(TriggerTreeNode.ATOM, tree.children[0].value, []))