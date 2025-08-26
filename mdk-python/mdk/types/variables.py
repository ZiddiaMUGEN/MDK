import traceback
import functools
import copy
from typing import Optional

from mdk.types.expressions import Expression, ConvertibleExpression
from mdk.types.specifier import TypeSpecifier
from mdk.types.context import CompilerContext, ParameterDefinition, StateController, StateScope
from mdk.types.builtins import IntType, FloatType, ShortType, ByteType, BoolType

from mdk.utils.shared import generate_random_string, convert, format_bool

## a special type of Expression which represents a variable access.
## generally speaking this is just treated differently so that we can
## detect variable initialization and scope in the state/template code.
class VariableExpression(Expression):
    def __init__(self, type: TypeSpecifier, scope: Optional[StateScope] = None, system: bool = False):
        self.type = type
        self.exprn = ""
        self.system = system

        ## in order to determine a name for this variable, we need to walk through the backtrace
        ## and find calling code which originates from a statedef or template function, or
        ## from the top level of a module (other than this one).
        context = CompilerContext.instance()
        traceback.extract_tb(None)
        for frame in traceback.extract_stack():
            function_name = frame.name
            if function_name in context.statedefs and frame.line != None and len(frame.line.split("=")) == 2:
                ## means this is a line from a statedef or template function, so we should check the assignment
                self.exprn = frame.line.split("=")[0].strip()
                if next(filter(lambda k: k.name == self.exprn, context.statedefs[function_name].locals), None) != None:
                    raise Exception(f"Attempted to create 2 local variables with the same name {self.exprn} in state definition {function_name}.")
                context.statedefs[function_name].locals.append(ParameterDefinition(self.type, self.exprn))
                break
            elif function_name in context.templates and frame.line != None and len(frame.line.split("=")) == 2:
                ## means this is a line from a statedef or template function, so we should check the assignment
                self.exprn = frame.line.split("=")[0].strip()
                if next(filter(lambda k: k.name == self.exprn, context.templates[function_name].locals), None) != None:
                    raise Exception(f"Attempted to create 2 local variables with the same name {self.exprn} in template definition {function_name}.")
                context.templates[function_name].locals.append(ParameterDefinition(self.type, self.exprn))
            elif context.current_state == None and context.current_template == None and function_name == "<module>" and frame.line != None and len(frame.line.split("=")) >= 2:
                ## means this is a line from a global scope
                self.exprn = frame.line.split("=")[0].strip()
                if next(filter(lambda k: k.name == self.exprn, context.globals), None) != None:
                    raise Exception(f"Attempted to create 2 global variables with the same name {self.exprn}.")
                context.globals.append(ParameterDefinition(self.type, self.exprn, scope = scope, is_system = self.system))
        
        ## if it could not be found, print a warning and assign a variable name.
        if context.current_state != None and self.exprn == "":
            self.exprn = f"_anon_{generate_random_string(8)}"
            print(f"Warning: Could not automatically identify the name of a variable in {context.current_state.fn.__name__}, assigning anonymous name {self.exprn}.")
        elif context.current_template != None and self.exprn == "":
            self.exprn = f"_anon_{generate_random_string(8)}"
            print(f"Warning: Could not automatically identify the name of a variable in {context.current_template.fn.__name__}, assigning anonymous name {self.exprn}.")
        elif context.current_template == None and context.current_state == None and self.exprn == "":
            self.exprn = f"_anon_{generate_random_string(8)}"
            print(f"Warning: Could not automatically identify the name of a variable in global state, assigning anonymous name {self.exprn}.")

    def make_expression(self, exprn: str):
        return Expression(exprn, self.type)
    
    def set(self, val: ConvertibleExpression):
        context = CompilerContext.instance()
        new_value = convert(val)
        new_controller = StateController()
        new_controller.type = "VarSet"
        new_controller.params = {}
        new_controller.params[self.exprn] = new_value
        if len(context.trigger_stack) != 0 or len(context.if_stack) != 0:
            new_controller.triggers = copy.deepcopy(context.trigger_stack)
            if len(context.if_stack) != 0:
                new_controller.triggers.append(Expression(f"mdk_internalTrigger = {context.if_stack[-1]}", BoolType))
            if len(context.check_stack) != 0:
                new_controller.triggers = copy.deepcopy(context.check_stack) + new_controller.triggers
                context.check_stack = []
        else:
            new_controller.triggers = [format_bool(True)]
        ## i believe this should always be right, since it flows from <callsite> -> .set
        callsite = traceback.extract_stack()[-2]
        new_controller.location = (callsite.filename, callsite.lineno if callsite.lineno != None else 0)

        if context.default_state[0] != None: new_controller.params["ignorehitpause"] = context.default_state[0]
        if context.default_state[1] != None: new_controller.params["persistent"] = context.default_state[1]

        if context.current_state != None:
            context.current_state.controllers.append(new_controller)
        elif context.current_template != None:
            context.current_template.controllers.append(new_controller)

    def add(self, val: ConvertibleExpression):
        context = CompilerContext.instance()
        new_value = convert(val)
        new_controller = StateController()
        new_controller.type = "VarAdd"
        new_controller.params = {}
        new_controller.params[self.exprn] = new_value
        if len(context.trigger_stack) != 0 or len(context.if_stack) != 0:
            new_controller.triggers = copy.deepcopy(context.trigger_stack)
            if len(context.if_stack) != 0:
                new_controller.triggers.append(Expression(f"mdk_internalTrigger = {context.if_stack[-1]}", BoolType))
            if len(context.check_stack) != 0:
                new_controller.triggers = copy.deepcopy(context.check_stack) + new_controller.triggers
                context.check_stack = []
        else:
            new_controller.triggers = [format_bool(True)]
        ## i believe this should always be right, since it flows from <callsite> -> .set
        callsite = traceback.extract_stack()[-2]
        new_controller.location = (callsite.filename, callsite.lineno if callsite.lineno != None else 0)

        if context.default_state[0] != None: new_controller.params["ignorehitpause"] = context.default_state[0]
        if context.default_state[1] != None: new_controller.params["persistent"] = context.default_state[1]

        if context.current_state != None:
            context.current_state.controllers.append(new_controller)
        elif context.current_template != None:
            context.current_template.controllers.append(new_controller)
    
## these are helpers for creating variables from commonly-used built-in types.
IntVar = functools.partial(VariableExpression, type = IntType)
ShortVar = functools.partial(VariableExpression, type = ShortType)
ByteVar = functools.partial(VariableExpression, type = ByteType)
BoolVar = functools.partial(VariableExpression, type = BoolType)
FloatVar = functools.partial(VariableExpression, type = FloatType)

__all__ = ["VariableExpression", "IntVar", "FloatVar", "ShortVar", "ByteVar", "BoolVar"]