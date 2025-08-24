#!/bin/env python3

# Script Calc.py

import math
import decimal
import sys
import typing
import os
import string
import itertools

APP_VERSION_MAJOR = 3
APP_VERSION_MINOR = 8
APP_SCRIPT_VERSION = 6

CUSTOM_SCRIPT_VERSION = False

variables = {"script_version": APP_SCRIPT_VERSION}
iterator_arrays = {} # {str: list[decimal.Decimal]}

PROGRAM_LICENSE = """
Copyright 2025 CoreTurboBoost

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
def print_program_license():
    print(PROGRAM_LICENSE)

def log10(x):
    return math.log(x, 10)
def log2(x):
    return math.log(x, 2)
def cosec(x):
    return 1/math.sin(x)
def sec(x):
    return 1/math.cos(x)
def cot(x):
    return 1/math.tan(x)

def negate(x):
    return -x

def product(array: list) -> decimal.Decimal:
    if len(array) == 0:
        return 0
    val = 1
    for a in array:
        val *= a
    return val

comparison_operators = {"==": lambda a,b: a==b, "!=": lambda a,b: a!=b,
        ">=": lambda a,b: a>=b, "<=": lambda a,b: a<=b,
        ">": lambda a,b: a>b, "<": lambda a,b: a<b}

def is_punct(input_str: str) -> bool:
    return all(char in string.punctuation for char in input_str)

ENABLED_DEBUG_OUTPUT = True
def console_output_debug_msg(message : str, end = "\n"):
    if ENABLED_DEBUG_OUTPUT: print(f"[debug]: {message}", end = end)

class TokenError:
    TYPE_NONE = 0
    TYPE_UNKNOWN_CHAR = 1
    TYPE_UNKNOWN_IDENTIFIER = 2
    TYPE_DECIMAL_POINT_COUNT = 3
    def __init__(self):
        self.string = ""
        self.type = TokenError.TYPE_NONE
    def __str__(self):
        return f"TokenError(string: {self.string}, type: {self.type})"

class Token:
    TYPE_BAD = -1
    TYPE_NONE = 0
    TYPE_IDENTIFIER = 1
    TYPE_CONST = 2
    TYPE_NUMBER = 3
    TYPE_BINARY_FUNCTION = 4
    TYPE_OPEN_BRACKET = 9
    TYPE_CLOSE_BRACKET = 10
    TYPE_FUNCTION = 11
    TYPE_VAR = 12
    TYPE_ASSIGNMENT = 13
    def get_str_from_type_enum(enum_type: TYPE_NONE):
        if (enum_type == Token.TYPE_BAD):
            return "Bad"
        elif (enum_type == Token.TYPE_NONE):
            return "None"
        elif (enum_type == Token.TYPE_IDENTIFIER):
            return "Identifier"
        elif (enum_type == Token.TYPE_CONST):
            return "Const"
        elif (enum_type == Token.TYPE_NUMBER):
            return "Number"
        elif (enum_type == Token.TYPE_BINARY_FUNCTION):
            return "Binary Function"
        elif (enum_type == Token.TYPE_OPEN_BRACKET):
            return "Open bracket"
        elif (enum_type == Token.TYPE_CLOSE_BRACKET):
            return "Close bracket"
        elif (enum_type == Token.TYPE_FUNCTION):
            return "Function"
        elif (enum_type == Token.TYPE_VAR):
            return "Variable"
        elif (enum_type == Token.TYPE_ASSIGNMENT):
            return "Assignment"
        else:
            return "Unknown"

    # Object specific methods
    def __init__(self, lexeame: str = "", token_type: int = TYPE_NONE, char_index: int = 0, error_object: TokenError = None):
        self.lexeame = lexeame
        self.type = token_type
        self.char_index = char_index
        self.error_object = error_object
    def get_type_str(self):
        return Token.get_str_from_type_enum(self.type)
    def __str__(self):
        return f"Token(lexeame: {self.lexeame}, type: {self.get_type_str()}, char_index: {self.char_index}, error_object: {self.error_object})"

def lex(expression : str):
    # TODO: Refactor to handle lex, rpn-generation, minus-to-negation. Return a
    #   list of error strings, rather than needing an external function. Want to
    #   catch as many formatting errors here, leaving only run-time errors and
    #   variable resolution for the evaluation function
    skip_char_count = 0
    tokens = []
    def append_unknown_char_token(char: str, char_index: int) -> None:
        error_object = TokenError()
        error_object.type = TokenError.TYPE_UNKNOWN_CHAR
        print_char = f"\'{char}\'" if char.isprintable() else f"{ord(char)}"
        error_object.string = f"Unknown char {print_char}"
        cur_token = Token("", Token.TYPE_BAD, char_index, error_object)
        tokens.append(cur_token)
    for char_index, char in enumerate(expression):
        if (skip_char_count > 0):
            skip_char_count -= 1
            continue
        if (char.isspace()):
            continue
        if (char.isdigit() or char == '.'):
            decimal_count = 0
            cur_token = Token()
            cur_token.char_index = char_index
            cur_token.type = Token.TYPE_NUMBER
            cur_token.lexeame = ""
            skip_char_count = -1
            for char_index in range(char_index, len(expression)):
                char = expression[char_index]
                if (char == '.'):
                    decimal_count += 1
                    if (decimal_count > 1):
                        cur_token.type = Token.TYPE_BAD
                        cur_token.error_object = TokenError()
                        cur_token.error_object.type = TokenError.TYPE_DECIMAL_POINT_COUNT
                        cur_token.error_object.string = f"Number cannot have more than one decimal point"
                        break
                    cur_token.lexeame += char
                    skip_char_count += 1
                elif (char.isdigit()):
                    cur_token.lexeame += char
                    skip_char_count += 1
                else:
                    break
            tokens.append(cur_token)
        elif (char.isalpha() or char == '_'):
            cur_token = Token()
            cur_token.char_index = char_index
            cur_token.type = Token.TYPE_IDENTIFIER
            cur_token.lexeame = ""
            skip_char_count -= 1
            for char_index in range(char_index, len(expression)):
                char = expression[char_index]
                if (char.isalnum() or char == '_'):
                    cur_token.lexeame += char
                    skip_char_count += 1
                else:
                    break
            if (cur_token.lexeame in KNOWN_CONSTS.keys()):
                cur_token.type = Token.TYPE_CONST
            elif (cur_token.lexeame in KNOWN_FUNCTIONS.keys()):
                cur_token.type = Token.TYPE_FUNCTION
            elif (cur_token.lexeame == 'A'):
                cur_token.type = Token.TYPE_NUMBER
                cur_token.lexeame = str(previous_answer)
            else:
                cur_token.type = Token.TYPE_VAR
                #cur_token.error_object = TokenError()
                #cur_token.error_object.type = TokenError.TYPE_UNKNOWN_IDENTIFIER
                #cur_token.error_object.string = f"Unknown constant or function \'{cur_token.lexeame}\'"
            tokens.append(cur_token)
        elif (char == '('):
            tokens.append(Token('(', Token.TYPE_OPEN_BRACKET, char_index, None))
        elif (char == ')'):
            tokens.append(Token(')', Token.TYPE_CLOSE_BRACKET, char_index, None))
        elif is_punct(char):
            trial_function = f"{char}"
            for sub_char_index, sub_char in enumerate(expression[char_index+1:]):
                if not is_punct(sub_char):
                    break
                sub_char_index += char_index
                trial_function += sub_char
                found_name = None
                skip_char_count += 1
                if len(trial_function) == binary_functions_max_name_len:
                    break
            while len(trial_function) > 0:
                matched_binary_fn = False
                for binary_fn in binary_function_names:
                    if trial_function == binary_fn:
                        tokens.append(Token(trial_function, Token.TYPE_BINARY_FUNCTION, char_index, None))
                        matched_binary_fn = True
                        break
                if matched_binary_fn:
                    break
                if (trial_function == '='):
                    tokens.append(Token('=', Token.TYPE_ASSIGNMENT, char_index, None))
                    break
                skip_char_count -= 1
                trial_function = trial_function[:len(trial_function)-1]
            if len(trial_function) == 0:
                append_unknown_char_token(char, char_index)
        else:
            append_unknown_char_token(char, char_index)
    return tokens

def get_lex_error_count(tokens : typing.List[Token]):
    error_count = 0
    for token in tokens:
        if (token.type == Token.TYPE_BAD):
            error_count += 1
    return error_count

def get_lex_error_strs(tokens: typing.List[Token], heading: str="") -> list[str]:
    errors = []
    for token in tokens:
        if token.type == Token.TYPE_BAD:
            error = f"{heading}TOKEN ERROR: char {token.char_index+1}. {token.error_object.string}."
            errors.append(error)
    return errors
def print_lex_errors(tokens : typing.List[Token], heading:str="") -> int:
    errors = get_lex_error_strs(tokens, heading)
    for error in errors:
        print(error)
    return len(errors)

def eval_lex_tokens(tokens : typing.List[Token]) -> (decimal.Decimal or None, list[str]):
    '''
    Returns list(evaluated_value: decimal.Decimal, errors: list[str])
       evaluated_value : decimal.Decimal() or None on error.
       errors : list[str], empty list on success.
    '''
    tokens = tokens.copy()
    def get_op_precedence(token : Token):
        '''
        get_precedence of operators
        '''
        # larger number greater precedence
        if token.type == token.TYPE_BINARY_FUNCTION:
            return BINARY_FUNCTIONS[token.lexeame].precedence
        if (token.type == Token.TYPE_NONE or token.type == Token.TYPE_OPEN_BRACKET):
            return LOWEST_PRECEDENCE_VALUE
        if (token.type == Token.TYPE_ASSIGNMENT):
            return ASSIGNMENT_PRECEDENCE_VALUE
        if (token.type == Token.TYPE_FUNCTION):
            return UNARY_FUNCTION_PRECEDENCE_VALUE
        console_output_debug_msg(f"get_precedence fn param not recognised token_type:{token_type}")
        return -1
    def is_operator(token_type : Token):
        if (token_type == Token.TYPE_BINARY_FUNCTION):
            return True
        if (token_type == Token.TYPE_FUNCTION):
            return True
        if (token_type == Token.TYPE_ASSIGNMENT):
            return True
        return False

    for i, token in enumerate(tokens):
        if token.type == Token.TYPE_VAR:
            next_is_assignment = False
            if i+1 < len(tokens):
                next_token = tokens[i+1]
                if next_token.type == Token.TYPE_ASSIGNMENT:
                    next_is_assignment = True
            if (token.lexeame in variables.keys() and not next_is_assignment):
                tokens[i].type = Token.TYPE_NUMBER
                tokens[i].lexeame = str(variables[token.lexeame])

    errors = []
    evaluated_value = 0
    operators_stack = []
    numbers_stack: list[decimal.Decimal or str] = []
    post_fix_token_list = []

    open_bracket_token = Token()
    open_bracket_token.char_index = -1
    open_bracket_token.type = Token.TYPE_OPEN_BRACKET
    open_bracket_token.lexeame = "("
    close_bracket_token = Token()
    close_bracket_token.char_index = -1
    close_bracket_token.type = Token.TYPE_CLOSE_BRACKET
    close_bracket_token.lexeame = ")"
    zero_token = Token()
    zero_token.char_index = -1
    zero_token.type = Token.TYPE_NUMBER
    zero_token.lexeame = "0"

    # handle minus signs and convert constants
    cur_token_index = 0
    cur_token = None
    for cur_token_index in range(len(tokens)):
        cur_token = tokens[cur_token_index]
        if (cur_token.type == Token.TYPE_CONST):
            tokens[cur_token_index].lexeame = str(KNOWN_CONSTS[tokens[cur_token_index].lexeame])
            tokens[cur_token_index].type = Token.TYPE_NUMBER
    cur_token_index = 0
    cur_token = None
    while (cur_token_index < len(tokens)):
        cur_token = tokens[cur_token_index]
        if (cur_token.type == Token.TYPE_BINARY_FUNCTION and cur_token.lexeame == "-"): # Special case for the '-' sign (to attempt to keep compatibility with older program versions)
            if (cur_token_index == 0):
                if (len(tokens) > 1):
                    console_output_debug_msg(f"cur_token_index:{cur_token_index} next token type:\'{Token.get_str_from_type_enum(tokens[cur_token_index+1].type)}\'")
                    if (tokens[cur_token_index+1].type == Token.TYPE_NUMBER or tokens[cur_token_index+1].type == Token.TYPE_CONST or tokens[cur_token_index+1].type == Token.TYPE_IDENTIFIER):
                        console_output_debug_msg("     Added tokens: (0<token>))")
                        tokens.insert(0, open_bracket_token)
                        tokens.insert(1, zero_token)
                        tokens.insert(cur_token_index+4, close_bracket_token)
                        cur_token_index += 3
            else:
                if (cur_token_index+1 < len(tokens)):
                    console_output_debug_msg(f"cur_token_index:{cur_token_index} last token type:\'{Token.get_str_from_type_enum(tokens[cur_token_index-1].type)}\', next token type:\'{Token.get_str_from_type_enum(tokens[cur_token_index+1].type)}\'")
                    if ((tokens[cur_token_index-1].type != Token.TYPE_NUMBER and tokens[cur_token_index-1].type != Token.TYPE_CONST and tokens[cur_token_index-1].type != Token.TYPE_IDENTIFIER and tokens[cur_token_index-1].type != Token.TYPE_CLOSE_BRACKET) and (tokens[cur_token_index+1].type == Token.TYPE_NUMBER or tokens[cur_token_index+1].type == Token.TYPE_CONST or tokens[cur_token_index+1].type == Token.TYPE_IDENTIFIER)):
                        console_output_debug_msg(f"((tokens[cur_token_index-1].type != Token.TYPE_NUMBER:{tokens[cur_token_index-1].type != Token.TYPE_NUMBER}")
                        console_output_debug_msg(f"tokens[cur_token_index-1].type != Token.TYPE_CONST:{tokens[cur_token_index-1].type != Token.TYPE_CONST}")
                        console_output_debug_msg(f"tokens[cur_token_index-1] != Token.TYPE_IDENTIFIER:{tokens[cur_token_index-1].type != Token.TYPE_IDENTIFIER}")
                        console_output_debug_msg(f"tokens[cur_token_index-1] != Token.TYPE_CLOSE_BRACKET:{tokens[cur_token_index-1].type != Token.TYPE_CLOSE_BRACKET}")
                        console_output_debug_msg(f"tokens[cur_token_index+1].type == Token.TYPE_NUMBER:{tokens[cur_token_index+1].type == Token.TYPE_NUMBER}")
                        console_output_debug_msg(f"tokens[cur_token_index+1] == Token.TYPE_CONST:{tokens[cur_token_index+1].type == Token.TYPE_CONST}")
                        console_output_debug_msg(f"tokens[cur_token_index+1] == Token.TYPE_IDENTIFIER:{tokens[cur_token_index+1].type == Token.TYPE_IDENTIFIER}")
                        console_output_debug_msg("     Added tokens: (0<token>))")
                        tokens.insert(cur_token_index, zero_token)
                        tokens.insert(cur_token_index, open_bracket_token)
                        tokens.insert(cur_token_index+4, close_bracket_token)
                        cur_token_index += 3
        cur_token_index += 1

    console_output_debug_msg(f"Printing partial processed tokens:")
    debug_token_str = " ".join([token.lexeame for token in tokens])
    console_output_debug_msg(debug_token_str)

    #infix to postfix
    open_bracket_count = 0
    for token_index, token in enumerate(tokens):

        post_fix_str = ""
        for o in post_fix_token_list:
            post_fix_str += str(o.lexeame) + " "
        console_output_debug_msg(f"[{token_index}] post fix expression: \'{post_fix_str}\'")

        if (token.type == Token.TYPE_IDENTIFIER or token.type == Token.TYPE_CONST or token.type == Token.TYPE_VAR):
            post_fix_token_list.append(token)
        elif (token.type == Token.TYPE_NUMBER):
            post_fix_token_list.append(token)
        elif (token.type == Token.TYPE_OPEN_BRACKET):
            open_bracket_count += 1
            operators_stack.append(token)
        elif (token.type == Token.TYPE_CLOSE_BRACKET):
            open_bracket_count -= 1
            cur_token = operators_stack[-1]
            while (cur_token.type != Token.TYPE_OPEN_BRACKET):
                if (len(operators_stack) == 0):
                    errors.append("Unmatched brackets, no matching \'(\' found")
                    break
                post_fix_token_list.append(operators_stack.pop())
                cur_token = operators_stack[-1]
            if (len(operators_stack) > 0):
                operators_stack.pop() 
        elif (is_operator(token.type) and token.type == Token.TYPE_FUNCTION):
            cur_func_prec = get_op_precedence(token)
            if len(operators_stack) > 0:
                stack_top_op_precedence = get_op_precedence(operators_stack[-1])
                while stack_top_op_precedence >= cur_func_prec and operators_stack[-1].type != Token.TYPE_FUNCTION:
                    post_fix_token_list.append(operators_stack.pop())
                    if (len(operators_stack) > 0):
                        stack_top_op_precedence = get_op_precedence(operators_stack[-1])
                    else:
                        break
            operators_stack.append(token)

        elif (is_operator(token.type)):
            console_output_debug_msg(f"[{token_index}] Considered token as an operator, {token}")
            cur_op_precedence = get_op_precedence(token)
            if (len(operators_stack) > 0):
                stack_top_op_precedence = get_op_precedence(operators_stack[-1])
            else:
                stack_top_op_precedence = get_op_precedence(Token())
            console_output_debug_msg(f"[{token_index}] both precedences (cur, stack_top): ({cur_op_precedence}, {stack_top_op_precedence})")
            if (cur_op_precedence > stack_top_op_precedence):
                console_output_debug_msg(f"[{token_index}] Added {token.lexeame} to op stack")
            while (stack_top_op_precedence >= cur_op_precedence):
                console_output_debug_msg(f"[{token_index}] Adding operator to post-fix list ({operators_stack[-1].lexeame})")
                console_output_debug_msg(f"[{token_index}] Adding operator to post-fix list ({operators_stack[-1].lexeame}) then added another operator to operators_stack ({token.lexeame})")
                post_fix_token_list.append(operators_stack.pop())
                if (len(operators_stack) > 0):
                    stack_top_op_precedence = get_op_precedence(operators_stack[-1])
                else:
                    stack_top_op_precedence = get_op_precedence(Token())
            operators_stack.append(token)
        else:
            error_string = f"[char_index:{token.char_index}] Token list contains unknown or bad token type"
            errors.append(error_string)
    
    if (len(operators_stack) > 0):
        console_output_debug_msg(f"Adding remaining operators on stack to post-fix list, len:{len(operators_stack)}")
    for operator_index in range(len(operators_stack)):
        console_output_debug_msg(f" [{operator_index}] adding operator:{operators_stack[-1].lexeame} to post_fix_token_list")
        post_fix_token_list.append(operators_stack.pop())

    if (open_bracket_count > 0):
        errors.append(f"Bracket mismatch. Some brackets dont have \')\', {open_bracket_count} unclosed brackets remaining")

    # debug
    post_fix_str = ""
    for o in post_fix_token_list:
        post_fix_str += " " + str(o.lexeame)
    console_output_debug_msg(f"post fix expression: {post_fix_str}")
    # /debug

    if (len(errors) > 0):
        return (None, errors)

    def is_number(a) -> bool:
        return isinstance(a, decimal.Decimal)

    # process post fix list
    for token in post_fix_token_list:
        if (token.type == Token.TYPE_NUMBER):
            numbers_stack.append(decimal.Decimal(token.lexeame))
        if (token.type == Token.TYPE_VAR):
            console_output_debug_msg(f"Adding variable token {token} to the numbers stack")
            numbers_stack.append(token.lexeame)
        elif (is_operator(token.type)):
            if (len(numbers_stack) < 1):
                errors.append("Too many operators, for the number of operands")
                break
            operand_a = numbers_stack.pop()
            if (token.type == Token.TYPE_FUNCTION):
                console_output_debug_msg(f"running function {token.lexeame} with parameter {operand_a}")
                try:
                    if not is_number(operand_a):
                        errors.append(f"{[token.char_index+1]} Expecting a number, not a variable")
                        break
                    numbers_stack.append(decimal.Decimal(KNOWN_FUNCTIONS[token.lexeame.lower()](operand_a)))
                    continue
                except ZeroDivisionError:
                    errors.append(f"{[token.char_index+1]} Function failure, division by zero")
                    break
                except ValueError:
                    errors.append(f"{[token.char_index+1]} Function failure, math domain error")
                    break
                except:
                    errors.append(f"{[token.char_index+1]} Function failure, {sys.exc_info()[1]}")
                    break

            if (len(numbers_stack) < 1):
                errors.append("1 Too many operators, for the number of operands")
                break
            operand_b = numbers_stack.pop()
            if token.type == Token.TYPE_BINARY_FUNCTION:
                if not(is_number(operand_a) and is_number(operand_b)):
                    errors.append(f"{[token.char_index+1]} Expecting a number, not a variable")
                    break
                binary_object = BINARY_FUNCTIONS[token.lexeame]
                evaluated_num, eval_errors = binary_object.call_callback(operand_b, operand_a)
                errors.extend(eval_errors)
                if len(eval_errors) == 0:
                    numbers_stack.append(evaluated_num)
            if (token.type == Token.TYPE_ASSIGNMENT):
                if not is_number(operand_a):
                    errors.append(f"{[token.char_index+1]} Expecting a number, not a variable")
                    break
                if not isinstance(operand_b, str):
                    errors.append(f"{[token.char_index+1]} Assignment can only occur to a variable")
                    break
                variables[operand_b] = operand_a
                numbers_stack.append(operand_a) # Going to return the value that got assigned to the variable
        console_output_debug_msg(f"numbers_stack at eval: {numbers_stack}")

    if (len(numbers_stack) > 1):
        errors.append(f"Too few functions/operators, for the number of operands, {len(numbers_stack)} operands remaining")
        console_output_debug_msg(f"Error: numbers_stack:{numbers_stack}")

    if (len(errors) > 0):
        return (None, errors)
    if not is_number(numbers_stack[0]):
        return (None, ["Remaining value is not a number"])
    return (numbers_stack[0], errors)

def eval_expression(expression: str) -> (decimal.Decimal or None, list[str]):
    lex_tokens = lex(expression)
    errors = get_lex_error_strs(lex_tokens)
    if len(errors) > 0:
        return (None, errors)
    value, errors = eval_lex_tokens(lex_tokens)
    errors = [f"EVALUATE ERROR: {error}" for error in errors]
    if len(errors) > 0:
        return (None, errors)
    return (value, errors)

class IOType:
    IOT_IN = 0
    IOT_OUT = 1
    IOT_IN_OUT = 2
    def to_string(self_type):
        if self_type == IOType.IOT_IN:
            return "IN"
        elif self_type == IOType.IOT_OUT:
            return "OUT"
        elif self_type == IOType.IOT_IN_OUT:
            return "IN-OUT"
        else:
            raise Exception("Unhandled IOType str convertions")

class CommandDataType:
    CDT_LITERAL_NUMBER = 1
    CDT_VAR = 2
    CDT_ITERATOR = 3

def merge_tags(a: list[str], b: list[str]) -> list[str]:
    '''
    Modifies the 'a' list in place.
    Returns the the list 'a'
    '''
    for val in b:
        if val in a:
            continue
        a.append(val)

class CommandDataPackage:
    def __init__(self, data_type: CommandDataType, data: float or str):
        self.data_type = data_type
        self.data = data

class CommandProcessMatchReturnData:
    def __init__(self, values: list, errors: list[str], tags: list[str]):
        if not isinstance(values, list):
            raise TypeError("values should be of type list")
        if not isinstance(errors, list):
            raise TypeError("errors should be of type list[str]")
        for error in errors:
            if not isinstance(error, str):
                raise TypeError("errors elements must be of type str only")
        if not isinstance(tags, list):
            raise TypeError("tags should be of type list[str]")
        for tag in tags:
            if not isinstance(tag, str):
                raise TypeError("tags elements must be of type str only")
        self.values = values
        self.errors = errors
        self.tags = tags
        self.validate_internal_state()
    def __str__(self) -> str:
        return f"CommandProcessMatchReturnData({self.values=}, {self.errors=}, {self.tags=})"
    def __repr__(self) -> str:
        return self.__str__()
    def __add__(self, other):
        values = self.values.copy()
        errors = self.errors.copy()
        tags = self.tags.copy()
        values.extend(other.values)
        errors.extend(other.errors)
        merge_tags(tags, other.tags)
        return CommandProcessMatchReturnData(values, errors, tags)
    def validate_internal_state(self) -> None:
        if len(self.values) == 0 and len(self.errors) == 0:
            raise Exception("Assumption not met. len(values) and len(errors) cannot both be zero")
        if len(self.values) > 0 and len(self.errors) > 0:
            raise Exception("Assumption not met. len(values) and len(errors) cannot both be > 0")
    def successful_match(self) -> bool:
        self.validate_internal_state()
        return len(self.values) > 0
    def has_errors(self) -> bool:
        self.validate_internal_state()
        return len(self.errors) > 0

class CommandProcessNode: # Abstract
    def reset_iterator(self) -> None:
        pass
    def match(self, phrases: list[str]) -> CommandProcessMatchReturnData:
        '''
        Return: (values, errors, tags)
        '''
        pass
    def get_str(self) -> str:
        pass

class CommandProcessRequiredGroup(CommandProcessNode):
    def __init__(self, nodes: list[CommandProcessNode]):
        self.nodes = nodes
        self.reset_iterator()
    def match(self, phrases: list[str]) -> CommandProcessMatchReturnData:
        phrases_index = 0
        operation_final_values = []
        operation_tags = []
        for nodes_index in range(len(self.nodes)):
            if phrases_index >= len(phrases):
                # Missing required arguments
                console_output_debug_msg(" CommandProcessRequiredGroup: Missing required arguments")
                return CommandProcessMatchReturnData([], ["Missing required arguments"], [])
            data = self.nodes[nodes_index].match(phrases[phrases_index:])
            if data.has_errors():
                return CommandProcessMatchReturnData([], data.errors, [])
            operation_final_values.extend(data.values)
            merge_tags(operation_tags, data.tags)
            phrases_index += len(data.values)
        return CommandProcessMatchReturnData(operation_final_values, [], operation_tags)
    def get_str(self) -> str:
        nodes_str = ""
        for i, node in enumerate(self.nodes):
            if i != 0:
                nodes_str += " "
            nodes_str += node.get_str()
        return f"{nodes_str}"

class CommandProcessXOR(CommandProcessNode):
    def __init__(self, nodes: list[CommandProcessNode]):
        self.nodes = nodes
    def match(self, phrases: list[str]) -> CommandProcessMatchReturnData:
        phrases_index = 0
        all_errors: list = []
        for nodes_index in range(len(self.nodes)):
            if phrases_index >= len(phrases):
                console_output_debug_msg(" CommandProcessXOR: Missing required arguments")
                return CommandProcessMatchReturnData([], ["Missing required arguments"], [])
            data = self.nodes[nodes_index].match(phrases[phrases_index:])
            if data.has_errors():
                all_errors.extend(data.errors)
                continue
            phrases_index += len(data.values)
            return CommandProcessMatchReturnData(data.values, [], data.tags)
        all_errors.extend(["No phrase matches required arguments"])
        return CommandProcessMatchReturnData([], all_errors, data.tags)
    def get_str(self) -> str:
        nodes_str = ""
        for i, node in enumerate(self.nodes):
            if i != 0:
                nodes_str += "|"
            nodes_str += node.get_str()
        return f"<{nodes_str}>"

class CommandProcessOptional(CommandProcessNode):
    def __init__(self, optional_node: CommandProcessNode):
        self.optional_node = optional_node
    def match(self, phrases: list[str]) -> CommandProcessMatchReturnData:
        if len(phrases) == 0:
            return CommandProcessMatchReturnData([None], [], [])
        data = self.optional_node.match(phrases)
        return data
    def get_str(self) -> str:
        return f"[{self.optional_node.get_str()}]"

class CommandProcessAddition(CommandProcessNode):
    def __init__(self, main_node: CommandProcessNode, optional_node: CommandProcessNode):
        self.main_node = main_node
        self.optional_node = optional_node
    def match(self, phrases: list[str]) -> CommandProcessMatchReturnData:
        if len(phrases) == 0:
            console_output_debug_msg(" CommandProcessAddition: Missing required arguments")
            return CommandProcessMatchReturnData([], ["Missing required arguements"], [])
        phrases_index = 0
        data = self.main_node.match(phrases[phrases_index:])
        if data.has_errors():
            return CommandProcessMatchReturnData([], data.errors, [])
        phrases_index += len(data.values)
        no_more_phrases = phrases_index == len(phrases)
        if no_more_phrases:
            return data
        optional_data = self.optional_node.match(phrases[phrases_index:])
        if optional_data.has_errors():
            return CommandProcessMatchReturnData([], optional_data.errors, [])
        return data + optional_data
    def get_str(self) -> str:
        return f"{self.main_node.get_str()} [{self.optional_node.get_str()}]"

class CommandProcessRepeat(CommandProcessNode):
    '''
    Have the match continue untill it returns errors,
    Two types of behaviours when it errors,
      either stop processing the matches, and return as a success (yes, even means no match is a success, or could add a check to garantee a single match (even have it as an arguemnt)), 
      or fail if any matches fail, meaning repeat must always be placed at the end, no exceptions
    '''
    def __init__(self, node: CommandProcessNode):
        self.node = node
    def match(self, phrases: list[str]) -> CommandProcessMatchReturnData:
        final_tags = []
        final_values = []
        for phrasei in range(len(phrases)):
            data = self.node.match(phrases[phrasei:])
            if data.has_errors():
                if len(final_tags) == 0:
                    console_output_debug_msg(" CommandProcessRepeat: Requires at least one valid argument")
                    return CommandProcessMatchReturnData([], data.errors.extend("Repeat command requires at least one valid argument"), [])
                return CommandProcessMatchReturnData(final_values, data.errors, final_tags)
            final_values.extend(data.values)
            merge_tags(final_tags, data.tags)
        return CommandProcessMatchReturnData(final_values, data.errors, final_tags)
    def get_str(self) -> str:
        return f"{self.node.get_str()}..."

def convert_to_number_or_none(phrase: str) -> decimal.Decimal or None:
    try:
        return decimal.Decimal(float(phrase))
    except ValueError:
        return None
class CommandProcessLiteralNumber(CommandProcessNode):
    def __init__(self, tag: str):
        self.tag = tag
    def match(self, phrases: list[str]) -> CommandProcessMatchReturnData:
        try:
            return CommandProcessMatchReturnData([decimal.Decimal(float(phrases[0]))], [], [self.tag])
        except ValueError:
            console_output_debug_msg(" CommandProcessLiteralNumber: Failed to convert")
            return CommandProcessMatchReturnData([], [f"Cannot convert '{phrases[0]}' to a number"], [])
    def get_str(self) -> str:
        return "NUMBER"
class CommandProcessVariable(CommandProcessNode):
    def __init__(self, io_type: IOType, tag: str, convert_in_var_to_number: bool):
        self.io_type = io_type
        self.tag = tag
        self.convert_in_var_to_number = convert_in_var_to_number
    def match(self, phrases: list[str]) -> CommandProcessMatchReturnData:
        phrase = phrases[0]
        var_exists = variables.get(phrase) != None
        if self.io_type == IOType.IOT_IN or self.io_type == IOType.IOT_IN_OUT:
            if not var_exists:
                console_output_debug_msg(" CommandProcessVariable: use of undefined var")
                return CommandProcessMatchReturnData([], [f"Varible '{phrases}' is undefined"], [])
            if self.convert_in_var_to_number and self.io_type == IOType.IOT_IN:
                phrase = variables.get(phrase)
        return CommandProcessMatchReturnData([phrase], [], [self.tag])
    def get_str(self) -> str:
        io_str = IOType.to_string(self.io_type)
        return f"{io_str}-VAR"
class CommandProcessIterator(CommandProcessNode):
    def __init__(self, io_type: IOType, tag: str):
        self.io_type = io_type
        self.tag = tag
    def match(self, phrases: list[str]) -> CommandProcessMatchReturnData:
        phrase = phrases[0]
        iterator_exists = iterator_arrays.get(phrase) != None
        if self.io_type == IOType.IOT_IN or self.io_type == IOType.IOT_IN_OUT:
            if not iterator_exists:
                console_output_debug_msg(f" Available iterators: {iterator_arrays=}")
                console_output_debug_msg(" CommandProcessIterator: use of undefined iter")
                return CommandProcessMatchReturnData([], [f"Iterator '{phrase}' is undefined"], [])
        return CommandProcessMatchReturnData([phrase], [], [self.tag])
    def get_str(self) -> str:
        io_str = IOType.to_string(self.io_type)
        return f"{io_str}-ITER"
class CommandProcessCmpOperator(CommandProcessNode):
    def __init__(self, tag: str):
        self.tag = tag
    def match(self, phrases: list[str]) -> CommandProcessMatchReturnData:
        phrase = phrases[0]
        operator = comparison_operators.get(phrase)
        if operator == None:
            console_output_debug_msg(" CommandProcessCmpOperator: unrecognised operator")
            return CommandProcessMatchReturnData([], [f"Comparison operator '{operator}' is unrecognised"], [])
        return CommandProcessMatchReturnData([operator], [], [self.tag])
    def get_str(self) -> str:
        return "CMP-OP"
class CommandProcessExpression(CommandProcessNode):
    def __init__(self, tag: str):
        self.tag = tag
    def match(self, phrases: list[str]) -> CommandProcessMatchReturnData:
        phrase = phrases[0]
        lex_tokens = lex(phrase)
        errors = get_lex_error_strs(lex_tokens)
        if len(errors) > 0:
            console_output_debug_msg(" CommandProcessExpression: Expression had lexical errors")
            return CommandProcessMatchReturnData([], errors, [])
        return CommandProcessMatchReturnData([phrase], [], [self.tag])
    def get_str(self) -> str:
        return "EXPRESSION"

class CommandProcessText(CommandProcessNode):
    def __init__(self, tag: str, match_exact_str: str or None):
        self.tag = tag
        self.match_exact_str = match_exact_str
    def match(self, phrases: list[str]) -> CommandProcessMatchReturnData:
        if len(phrases) == 0:
            return CommandProcessMatchReturnData([], ["Missing required arguments"], [])
        if self.match_exact_str != None:
            if phrases[0] != self.match_exact_str:
                return CommandProcessMatchReturnData([], [f"Exact string '{self.match_exact_str}' not matched"], [])
        return CommandProcessMatchReturnData([phrases[0]], [], [self.tag])
    def get_str(self) -> str:
        text = "TEXT" if self.match_exact_str == None else self.match_exact_str
        return text

'''
values callback signature
CHAR: def _(specifier: char) -> list[any or None, list[str]]
'''
FORMAT_SPECIFIER_GETTERS = {
        "v": lambda a: [variables.get(a), [f"Variable '{a}' is undefined"]], 
        "e": lambda a: eval_expression(a),
        "i": lambda a: [iterator_arrays.get(a), [f"Iterator '{a}' is undefined"]], 
        "n": lambda a: [convert_to_number_or_none(a), [f"'{a}' is not a valid literal number"]]
        }
class CommandProcessFormatString(CommandProcessNode):
    def __init__(self, tag: str):
        self.tag = tag
    def match(self, phrases: list[str]) -> CommandProcessMatchReturnData:
        if len(phrases) == 0:
            return CommandProcessMatchReturnData([], ["Missing required arguments, format specifier"], [])
        cur_phrase_phrases_index = 0
        formatted_string = ""
        format_string = phrases[cur_phrase_phrases_index]
        char_skip_count = 0
        for chari, char in enumerate(format_string):
            if char_skip_count > 0:
                char_skip_count -= 1
                continue
            if char == "%":
                if chari >= len(format_string):
                    return CommandProcessMatchReturnData([], ["Format string cannot end with a %, use  %%  for a literal percentage sign.", []])
                next_char = format_string[chari+1]
                char_skip_count += 1
                if next_char == "%":
                    formatted_string += "%"
                elif next_char in FORMAT_SPECIFIER_GETTERS.keys():
                    if cur_phrase_phrases_index+1 >= len(phrases):
                        return CommandProcessMatchReturnData([], ["Missing some format specifier arguments"], [])
                    value, errors = FORMAT_SPECIFIER_GETTERS[next_char](phrases[cur_phrase_phrases_index+1])
                    cur_phrase_phrases_index += 1
                    if value == None:
                        return CommandProcessMatchReturnData([], ["Format string conversion error occurred"].extend(errors), [])
                    formatted_string += str(value)
                else:
                    return CommandProcessMatchReturnData([], [f"Unrecognised format specifier '{next_char}'"], [])
            else:
                formatted_string += char
        return CommandProcessMatchReturnData([formatted_string], [], [self.tag])
    def get_str(self) -> str:
        return f"FORMAT_STRING [FORMAT_ARGS].."

class CommandProcessTreeMatchState:
    def __init__(self, command_matched: bool, args_matched: bool, callback_errors: list[str], values: list, tags: list[str]):
        self.command_matched = command_matched
        self.args_matched = args_matched
        self.callback_errors = callback_errors
        self.values = values
        self.tags = tags
        self.assert_check_types()
    def assert_check_types(self) -> None:
        if not isinstance(self.command_matched, bool):
            raise TypeError("command_matched must be of type bool")
        if not isinstance(self.args_matched, bool):
            raise TypeError("args_matched must be of type bool")
        if not isinstance(self.callback_errors, list):
            raise TypeError("callback_errors must be of type list[str]")
        for error in self.callback_errors:
            if not isinstance(error, str):
                raise TypeError("callback_errors must only contain strings")
        if not isinstance(self.values, list):
            raise TypeError("values must be of type list")
        if not isinstance(self.tags, list):
            raise TypeError("tags must be of type list")
        for tag in self.tags:
            if not isinstance(tag, str):
                raise TypeError("tags must only contain strings")
    def __str__(self) -> str:
        return f"CommandProcessMatchState({self.command_matched=}, {self.args_matched=}, {self.callback_had_errors=}, {self.values=}, {self.tags=})"
    def callback_had_errors(self) -> bool:
        return len(self.callback_errors) > 0
class CommandProcessTree:
    def __init__(self, name: str, root_node: CommandProcessNode):
        self.name = name
        self.root_node = root_node
    def match_and_run(self, test_phrases: list[str], script_line_number: int, on_success_callback: typing.Callable) -> CommandProcessTreeMatchState:
        '''
        on_success_callback: def callback(values: list, tags: list[str]) -> None or list[str]
        '''
        match_args_len_exact = True
        if len(test_phrases) == 0:
            console_output_debug_msg(f"CommandProcessTree.match_and_run(): {self.get_str()}: test_phrases.len()==0")
            return CommandProcessTreeMatchState(False, False, [], [], [])
        match_name = f"!{self.name}"
        if test_phrases[0] != match_name:
            return CommandProcessTreeMatchState(False, False, [], [], [])
        console_output_debug_msg(f"given phrases: {test_phrases}")
        data = self.root_node.match(test_phrases[1:])
        console_output_debug_msg(f"match_and_run: root_node ({self.root_node}): return ({data=})")
        if data.has_errors():
            print(f"[{script_line_number}] Errors occurred for command {self.name}: Expected format '{self.get_str()}'")
            for error in data.errors:
                print(f"  {error}")
            return CommandProcessTreeMatchState(True, False, [], [], [])
        if len(data.values) < len(test_phrases)-1 and match_args_len_exact:
            console_output_debug_msg(f"Early return due to too many arguments")
            return CommandProcessTreeMatchState(True, False, [], [], [])
        callback_errors = []
        if on_success_callback != None:
            return_value = on_success_callback(data.values, data.tags)
            if return_value != None and isinstance(return_value, (list, tuple)):
                callback_errors = [f"[{script_line_number}] {self.name}: {error}" for error in return_value]
                for error in callback_errors:
                    print(error)
        return CommandProcessTreeMatchState(True, True, callback_errors, data.values, data.tags)

    def get_str(self) -> str:
        return f"!{self.name} {self.root_node.get_str()}"


class BinaryFunction:
    def __init__(self, lexeame: str, precedence: int, callback: typing.Callable, pre_condition_fn: typing.Callable or None):
        self._lexeame = None
        self.lexeame = lexeame
        if not isinstance(precedence, int):
            raise TypeError("precedence must be of type int")
        if not isinstance(callback, typing.Callable):
            raise TypeError("callback must be of type callable")
        if pre_condition_fn == None:
            pre_condition_fn = lambda a, b: []
        if not isinstance(pre_condition_fn, typing.Callable):
            raise TypeError("pre_condition_fn must be of type callable")
        self._precedence = precedence
        self._callback = callback
        self._pre_condition_fn = pre_condition_fn
    def __str__(self) -> str:
        return f"BinaryFunction({self.lexeame=}, {self.precedence=}, {self.callback=})"

    def handle_precondition(self, left_operand: decimal.Decimal, right_operand: decimal.Decimal) -> list[str]:
        '''
        Return a list of strings representing errors
        '''
        return self._pre_condition_fn(left_operand, right_operand)

    @property
    def lexeame(self) -> chr:
        return self._lexeame
    @lexeame.setter
    def lexeame(self, lexeame: chr) -> None:
        if not isinstance(lexeame, str):
            raise TypeError("lexeame must be of type chr")
        if len(lexeame) < 1:
            raise ValueError("lexeame must be at least of length 1")
        if not is_punct(lexeame):
            raise ValueError("lexeame must be made strictly from punctuation characters")
        self._lexeame = lexeame

    @property
    def precedence(self) -> int:
        return self._precedence
    
    @property
    def callback(self) -> typing.Callable:
        return self._callback

    def call_callback(self, left_operand: decimal.Decimal, right_operand: decimal.Decimal) -> (decimal.Decimal, list[str]):
        precondition_errors = self.handle_precondition(left_operand, right_operand)
        if len(precondition_errors) > 0:
            return (None, precondition_errors)
        try:
            return_val = self._callback(left_operand, right_operand)
        except (ValueError, ZeroDivisionError):
            return (None, [f"binary callback function failure, {sys.exc_info()[1]}"])
        if not isinstance(return_val, decimal.Decimal):
            raise TypeError("callback does not return the correct type, expected type decimal.Decimal")
        return (return_val, [])

KNOWN_CONSTS = {"pi": math.pi, "e": math.e, "deg2rad": (math.pi/180), "rad2deg": (180/math.pi)}
'''
NOTE: These functions take a single decimal.Decimal as input and returns a single Decimal.Decimal
'''
KNOWN_FUNCTIONS = {"negate": negate, "ceil": math.ceil, "floor": math.floor, "round": round, "sqrt": math.sqrt, "log10": log10, "log2": log2, "cos": math.cos, "sin": math.sin, "tan": math.tan, "cosec": cosec, "sec": sec, "cot": cot, "acos": math.acos, "asin": math.asin, "atan": math.atan}


BINARY_FUNCTIONS = {"+": BinaryFunction('+', 10, lambda a,b: a+b, None), 
        "-": BinaryFunction('-', 10, lambda a,b: a-b, None), 
        "*": BinaryFunction('*', 20, lambda a,b: a*b, None),
        "/": BinaryFunction('/', 20, lambda a,b: a/b, lambda left,right: ["Division by zero"] if right==0 else []),
        "%": BinaryFunction('%', 20, lambda a,b: a%b, lambda left,right: ["Division by zero"] if right==0 else []),
        "^": BinaryFunction('^', 30, lambda a,b: decimal.Decimal(math.pow(a,b)), None),
        ">": BinaryFunction('>', 5, lambda a,b: decimal.Decimal(a>b), None),
        "<": BinaryFunction('<', 5, lambda a,b: decimal.Decimal(a<b), None),
        ">=": BinaryFunction('>=', 5, lambda a,b: decimal.Decimal(a>=b), None),
        "<=": BinaryFunction('<=', 5, lambda a,b: decimal.Decimal(a<=b), None),
        "==": BinaryFunction('==', 5, lambda a,b: decimal.Decimal(a==b), None),
        "!=": BinaryFunction('!=', 5, lambda a,b: decimal.Decimal(a!=b), None),
        "&&": BinaryFunction('&&', 4, lambda a,b: decimal.Decimal(bool(a) and bool(b)), None),
        "||": BinaryFunction('||', 3, lambda a,b: decimal.Decimal(bool(a) or bool(b)), None), }

if not all(map(lambda a: a[0] == a[1].lexeame, zip(BINARY_FUNCTIONS.keys(), BINARY_FUNCTIONS.values()))):
        raise ValueError("Binary function lexeame and BINARY_FUNCTIONS key do not match")

binary_function_names = BINARY_FUNCTIONS.keys()
binary_functions_max_name_len = max(map(lambda a: len(a), BINARY_FUNCTIONS.keys()))

LOWEST_PRECEDENCE_VALUE = 0
ASSIGNMENT_PRECEDENCE_VALUE = 1
UNARY_FUNCTION_PRECEDENCE_VALUE = 50

def get_user_number_input(prompt, allow_program_exit=False) -> float:
    is_valid = False
    number = 0
    invalid_input_error_message = "Input Error: Expected an int"
    while not is_valid:
        is_valid = True
        try:
            number = float(input(prompt))
        except (ValueError):
            print(invalid_input_error_message)
            is_valid = False
        except (EOFError, KeyboardInterrupt):
            if allow_program_exit:
                sys.exit("Exited by user on input prompt")
            print(invalid_input_error_message)
            is_valid = False
    return number

command_tree_if = CommandProcessTree("if", 
    CommandProcessAddition(
        CommandProcessRequiredGroup([
            CommandProcessXOR([
                CommandProcessLiteralNumber(""),
                CommandProcessVariable(IOType.IOT_IN, "", True)
            ]),
            CommandProcessCmpOperator(""),
            CommandProcessXOR([
                CommandProcessLiteralNumber(""),
                CommandProcessVariable(IOType.IOT_IN, "", True)
            ])
        ]), 
        CommandProcessRequiredGroup([
            CommandProcessVariable(IOType.IOT_OUT, "ifset", True),
            CommandProcessXOR([
                CommandProcessLiteralNumber("ifset"),
                CommandProcessVariable(IOType.IOT_IN, "ifset", True)
            ])
        ])
    )
)

command_tree_while = CommandProcessTree("while", 
    CommandProcessRequiredGroup([
        CommandProcessXOR([
            CommandProcessLiteralNumber(""),
            CommandProcessVariable(IOType.IOT_IN, "", True)
        ]),
        CommandProcessCmpOperator(""),
        CommandProcessXOR([
            CommandProcessLiteralNumber(""),
            CommandProcessVariable(IOType.IOT_IN, "", True)
        ]),
    ])
)

command_tree_exit = CommandProcessTree("exit",
    CommandProcessOptional(
        CommandProcessXOR([
            CommandProcessLiteralNumber("code"),
            CommandProcessVariable(IOType.IOT_IN, "code", True)
        ])
    )
)

command_tree_input = CommandProcessTree("input",
    CommandProcessOptional(
        CommandProcessRepeat(
            CommandProcessText("prompt", None)
        )
    )
)

def command_process_callback_input(values: list, tags: list[str]) -> None:
    console_output_debug_msg(f"command_process_callback_input: {values=} {tags=}")
    if "prompt" in tags:
        prompt = " ".join(values)
    else:
        prompt = "INPUT >> "
    variables["input"] = decimal.Decimal(get_user_number_input(prompt))

command_tree_print = CommandProcessTree("print",
     CommandProcessOptional(
        CommandProcessRepeat(
            CommandProcessText("text", None)
        )
    )
)

def command_process_callback_print(values: list, tags: list[str]) -> None:
    output = ""
    if "text" in tags:
        output = " ".join(values)
    print(output)

command_tree_varout = CommandProcessTree("varout",
    CommandProcessOptional(
        CommandProcessAddition(
            CommandProcessVariable(IOType.IOT_IN, "var", False),
            CommandProcessText("name", "-name")
        )
    )
)

def command_process_callback_varout(values: list, tags: list[str]) -> None:
    output = f"{values[0]}=" if "name" in tags else ""
    output += str(variables[values[0]]) if "var" in tags else ""
    if "var" in tags: print(output)

command_tree_repeat = CommandProcessTree("repeat",
     CommandProcessRequiredGroup([
         CommandProcessXOR([
             CommandProcessLiteralNumber(""),
             CommandProcessVariable(IOType.IOT_IN, "", True)
         ]),
         CommandProcessExpression("")
     ])
 )

def command_process_callback_repeat(values: list, tags: list[str]) -> list[str]:
    for _ in range(int(values[0])):
        value, errors = eval_expression(values[1])
        if len(errors) > 0:
            return errors

command_tree_yield = CommandProcessTree("yield",
    CommandProcessRequiredGroup([
        CommandProcessIterator(IOType.IOT_OUT, ""),
        CommandProcessXOR([
            CommandProcessLiteralNumber(""),
            CommandProcessVariable(IOType.IOT_IN, "", True)
        ])
    ])
)

def command_process_callback_yield(values: list, tags: list[str]) -> None:
    global iterator_arrays
    console_output_debug_msg(f"yield callback: yield command callback called for iterator {values[0]}")
    if iterator_arrays.get(values[0]) == None:
        iterator_arrays[values[0]] = []
    iterator_arrays[values[0]].append(values[1])
    console_output_debug_msg(f"yield callback: {iterator_arrays=}")

command_tree_clear = CommandProcessTree("clear",
    CommandProcessIterator(IOType.IOT_IN, "")
)

def command_process_callback_clear(values: list, tags: list[str]) -> None:
    global iterator_arrays
    iterator_arrays[values[0]] = []

command_tree_dup = CommandProcessTree("dup",
    CommandProcessRequiredGroup([
        CommandProcessIterator(IOType.IOT_OUT, ""),
        CommandProcessIterator(IOType.IOT_IN, "")
    ])
)

def command_process_callback_dup(values: list, tags: list[str]) -> None:
    global iterator_arrays
    iterator_arrays[values[0]] = iterator_arrays[values[1]].copy()

command_tree_count = CommandProcessTree("count",
    CommandProcessRequiredGroup([
        CommandProcessIterator(IOType.IOT_IN, ""),
        CommandProcessVariable(IOType.IOT_OUT, "", False)
    ])
)

def command_process_callback_count(values: list, tags: list[str]) -> None:
    global variables
    variables[values[1]] = len(iterator_arrays[values[0]])
    console_output_debug_msg(f"count callback: Set variable {values[1]}={len(iterator_arrays[values[0]])} from iterator {values[0]}")

command_tree_map = CommandProcessTree("map",
    CommandProcessRequiredGroup([
        CommandProcessIterator(IOType.IOT_IN_OUT, ""),
        CommandProcessExpression("")
    ])
)

def command_process_callback_map(values: list, tags: list[str]) -> list[str]:
    global iterator_arrays, variables
    iterator_len = len(iterator_arrays[values[0]])
    for i in range(iterator_len):
        variables[values[0]] = iterator_arrays[values[0]][i]
        mapped_value, errors = eval_expression(values[1])
        if mapped_value == None:
            return errors
        iterator_arrays[values[0]][i] = mapped_value
    return []

command_tree_filter = CommandProcessTree("filter",
    CommandProcessRequiredGroup([
        CommandProcessIterator(IOType.IOT_IN_OUT, ""),
        CommandProcessXOR([
            CommandProcessLiteralNumber(""),
            CommandProcessVariable(IOType.IOT_IN, "left_var", False)
        ]),
        CommandProcessCmpOperator(""),
        CommandProcessXOR([
            CommandProcessLiteralNumber(""),
            CommandProcessVariable(IOType.IOT_IN, "right_var", False)
        ])
    ])
)

def command_process_callback_filter(values: list, tags: list[str]) -> None:
    global iterator_arrays, variables
    filtered_list = []
    for val in iterator_arrays[values[0]]:
        variables[values[0]] = val
        left = variables[values[1]] if "left_var" in tags else values[1]
        right = variables[values[3]] if "right_var" in tags else values[3]
        if values[2](left, right):
            filtered_list.append(val)
    iterator_arrays[values[0]] = filtered_list

command_tree_next = CommandProcessTree("next",
    CommandProcessIterator(IOType.IOT_IN_OUT, "")
)

def command_process_callback_next(values: list, tags: list[str]) -> None:
    global variables, iterator_arrays
    iterator_name = values[0]
    if len(iterator_arrays[iterator_name]) == 0:
        console_output_debug_msg(f"next callback: Iterator {iterator_name} is empty")
        return None
    variables[iterator_name] = iterator_arrays[iterator_name].pop()
    console_output_debug_msg("next callback: Assigned new value to variable {values[0]}={variables[values[0]]}")

command_tree_sum = CommandProcessTree("sum",
    CommandProcessRequiredGroup([
        CommandProcessIterator(IOType.IOT_IN, ""),
        CommandProcessVariable(IOType.IOT_OUT, "", False)
    ])
)

def command_process_callback_sum(values: list, tags: list[str]) -> None:
    global variables
    variables[values[1]] = sum(iterator_arrays[values[0]])

command_tree_product = CommandProcessTree("product",
    CommandProcessRequiredGroup([
        CommandProcessIterator(IOType.IOT_IN, ""),
        CommandProcessVariable(IOType.IOT_OUT, "", False)
    ])
)

def command_process_callback_product(values: list, tags: list[str]) -> None:
    global variables
    variables[values[1]] = product(iterator_arrays[values[0]])

command_tree_write = CommandProcessTree("write",
    CommandProcessRequiredGroup([
        CommandProcessText("", None),
        CommandProcessIterator(IOType.IOT_IN, ""),
        CommandProcessVariable(IOType.IOT_OUT, "", False)
    ])
)

def command_process_callback_write(values: list, tags: list[str]) -> None:
    global variables
    file_path = values[0]
    input_iterator = iterator_arrays[values[1]]
    output_status_variable_name = values[2]
    serialized_iterator_data = ",".join([f"{value}" for value in input_iterator])

    STATUS_SUCCESS = 0
    STATUS_PERMISSION_ERROR = 1
    STATUS_ENCODE_ERROR = 2
    STATUS_IS_A_DIRECTORY = 5

    variables[output_status_variable_name] = decimal.Decimal(STATUS_SUCCESS)
    try:
        file_handle = open(file_path, "w")
    except PermissionError:
        console_output_debug_msg(f"!write: Denied permission to write to file {file_path}")
        variables[output_status_variable_name] = decimal.Decimal(STATUS_PERMISSION_ERROR)
        return None
    except IsADirectoryError:
        console_output_debug_msg(f"!write: File path {file_path} is a directory")
        variables[output_status_variable_name] = decimal.Decimal(STATUS_IS_A_DIRECTORY)
    try:
        file_handle.write(serialized_iterator_data)
    except UnicodeEncodeError:
        console_output_debug_msg(f"!write: Serialized iterator failed encoding when write to file {file_path}")
        variables[output_status_variable_name] = decimal.Decimal(STATUS_ENCODE_ERROR)
        return None
    except PermissionError:
        console_output_debug_msg(f"!write: Denied permission to write to file {file_path}")
        variables[output_status_variable_name] = decimal.Decimal(STATUS_PERMISSION_ERROR)
        return None
    file_handle.close()

command_tree_read = CommandProcessTree("read",
    CommandProcessRequiredGroup([
        CommandProcessText("", None),
        CommandProcessIterator(IOType.IOT_OUT, ""),
        CommandProcessVariable(IOType.IOT_OUT, "", False)
    ])
)

def command_process_callback_read(values: list, tags: list[str]) -> None:
    global variables, iterator_arrays
    file_path = values[0]
    output_iterator_name = values[1]
    output_status_variable_name = values[2]

    STATUS_SUCCESS = 0
    STATUS_PERMISSION_ERROR = 1
    STATUS_DECODE_ERROR = 2
    STATUS_DESERIALIZATION_ERROR = 3
    STATUS_FILE_NOT_FOUND = 4
    STATUS_IS_A_DIRECTORY = 5

    variables[output_status_variable_name] = decimal.Decimal(STATUS_SUCCESS)
    try:
        file_handle = open(file_path)
    except FileNotFoundError:
        console_output_debug_msg(f"!read: File {file_path} not found")
        variables[output_status_variable_name] = STATUS_FILE_NOT_FOUND
        return None
    except PermissionError:
        console_output_debug_msg(f"!read: Denied permission to write to file {file_path}")
        variables[output_status_variable_name] = STATUS_PERMISSION_ERROR
        return None
    except IsADirectoryError:
        console_output_debug_msg(f"!write: File path {file_path} is a directory")
        variables[output_status_variable_name] = decimal.Decimal(STATUS_IS_A_DIRECTORY)
    try:
        contents = file_handle.read()
    except UnicodeDecodeError:
        console_output_debug_msg(f"!read: File {file_path} is not a valid text file")
        variables[output_status_variable_name] = STATUS_DECODE_ERROR
        return None
    except PermissionError:
        console_output_debug_msg(f"!read: Denied permission to write to file {file_path}")
        variables[output_status_variable_name] = STATUS_PERMISSION_ERROR
        return None
    file_handle.close()
    deserialized_iterator_data = contents.split(",")
    deserialzed_numbers = []
    for data in deserialized_iterator_data:
        try:
            value = decimal.Decimal(float(data))
        except ValueError:
            console_output_debug_msg(f"!read: De-serialized iterator data is invalid")
            variables[output_status_variable_name] = STATUS_DESERIALIZATION_ERROR
            return None
        deserialzed_numbers.append(value)
    iterator_arrays[output_iterator_name] = deserialzed_numbers

command_trees = {
        "if": (command_tree_if, None),
        "while": (command_tree_while, None),
        "exit": (command_tree_exit, lambda values, tags: sys.exit(int(values[0]) if "code" in tags else 0)),
        "input": (command_tree_input, command_process_callback_input),
        "print": (command_tree_print, command_process_callback_print),
        "varout": (command_tree_varout, command_process_callback_varout),
        "repeat": (command_tree_repeat, command_process_callback_repeat),
        "yield": (command_tree_yield, command_process_callback_yield),
        "clear": (command_tree_clear, command_process_callback_clear),
        "dup": (command_tree_dup, command_process_callback_dup),
        "count": (command_tree_count, command_process_callback_count),
        "map": (command_tree_map, command_process_callback_map),
        "filter": (command_tree_filter, command_process_callback_filter),
        "next": (command_tree_next, command_process_callback_next),
        "sum": (command_tree_sum, command_process_callback_sum),
        "product": (command_tree_product, command_process_callback_product),
        "write": (command_tree_write, command_process_callback_write),
        "read": (command_tree_read, command_process_callback_read)
        }

command_process_descriptions = {
        "if": "Compare the two variables or literal numbers and either assign to a variable (if provided) or start a if statement block, end block with !endif command",
        "while": "Compare two variables or literal numbers and run the while block while the condition is true, end block with !endwhile command",
        "exit": "Stop the program with an optional exit code",
        "input": "Hold execution of the program and request user input as a number. The variable 'input' is assigned the users input",
        "print": "Output literal text to the user",
        "varout": "Output the value in a variable",
        "repeat": "Repeats an expression for a given count (can be a literal number or a variable). Count cannot be accessed or modified",
        "yield": "Appends a literal number or value in a variable to an iterator",
        "clear": "Removes all values within an iterator",
        "dup": "Makes a exact hard copy of an iterator",
        "count": "Returns the number of remaining values within an iterator, into a chosen variable",
        "map": "Higher order function 'map' that operates on iterators, given an expression. The current iterated value is the variable with the same name as the iterator",
        "filter": "Higher order function 'map' that operates on iterators, given a condition. The current iterated value is the variable with the same name as the iterator",
        "next": "Assumes iterator is not empty. Pops the next value from the iterator and assigns it to a variable with the same name as the iterator",
        "sum": "Higher order function 'map' that operates on iterators. Returns the sum into a chosen output variable",
        "product": "Higher order function 'map' that operates on iterators. Returns the sum into a chosen output variable",
        "write": "Attempts to write the given iterator to a given file path. The success of the operation is returned into a chosen variable. 0 is success, any other value is a failure. 1 - permission error. 2 - decode error. 5 - is a directory",
        "read": "Attempts to write the given iterator to a given file path. The success of the operation is returned into a chosen variable. 0 is success, any other value is a failure. 1 - permission error. 2 - encode error. 3 - de-serialization error. 4 - file not found. 5 - is a directory"
}

binary_function_descriptions = {
    "+":  "Binary addition",
    "-":  "Binary subtraction",
    "*":  "Binary multiplication",
    "/":  "Binary division",
    "%":  "Modulus operator",
    "^":  "Exponentiation",
    ">":  "Greater than",
    "<":  "Less than",
    ">=": "Greater than or equal too",
    "<=": "Less than or equal too",
    "==": "Exactly equal too, equivalent",
    "!=": "Not equal too, inequivalent",
    "&&": "Boolean AND",
    "||": "Boolean OR"
}

unary_function_descriptions = {
    "negate": "Negation. Flip the sign of the number",
    "ceil": "Mathematical ceiling of a number. Rounds number up to nearest whole number",
    "floor": "Mathematical floor of a number. Rounds number down to the nearest whole number",
    "round": "Mathematical round to whole number",
    "sqrt": "Mathematical square root",
    "log10": "Logarithmic function with base 10",
    "log2": "Logarithmic function with base 2",
    "cos": "Trigonometric cosine function, angle in radians",
    "sin": "Trigonometric sine function, angle in radians",
    "tan": "Trigonometric tangent function, angle in radians",
    "cosec": "Trigonometric co-secant function, angle in radians",
    "sec": "Trigonometric secant function, angle in radians",
    "cot": "Trigonometric co-tangent function, angle in radians",
    "acos": "Trigonometric arc-cosine function, angle in radians",
    "asin": "Trigonometric arc-sine function, angle in radians",
    "atan": "Trigonometric arc-tangent function, angle in radians"
}


previous_answer = 0

def print_constants() -> None:
    print("Constants:")
    for constant in KNOWN_CONSTS.keys():
        print(f" {constant} - {KNOWN_CONSTS[constant]}")
def print_functions() -> None:
    print("Unary Functions")
    for function in KNOWN_FUNCTIONS.keys():
        print(f" {function}")
def print_commands() -> None:
    print("Interactive mode commands")
    print(" help, h                 - print help page")
    print(" quit, q                 - exit program")
    print(" exit [INT|VAR]          - exit program with exit code INT or with value in VAR")
    print(" debug [on|off|toggle]   - toggle debug output")
    print(" echo [on|off|toggle]    - toggle echo output")
    print(" input [PROMPT]          - output PROMPT to stdout and wait input\n    (input put into variable 'input')")
    print(" print [TEXT]            - output TEXT to stdout")
    print(" varout <VAR> [-name]    - output variable <VAR> with optional name")

def parse_input_for_args(uinput: str) -> list[str]:
    out_args = []
    in_quote = False
    cur_phrase = ""
    skip_char_count = 0
    for chari, char in enumerate(uinput):
        if skip_char_count > 0:
            skip_char_count -= 1
            continue
        if char == "\\":
            skip_char_count += 1
            if chari+1 < len(uinput):
                next_char = uinput[chari+1]
                if next_char == '"':
                    cur_phrase += '"'
                elif next_char == '\\':
                    cur_phrase += '\\'
            continue
        if char == '"':
            in_quote = not in_quote
            continue
        if in_quote:
            cur_phrase += char
            continue
        if char.isspace():
            if len(cur_phrase) > 0:
                out_args.append(cur_phrase)
            cur_phrase = ""
            continue
        cur_phrase += char
    if len(cur_phrase) > 0:
        out_args.append(cur_phrase)
    return out_args

is_interactive = False
if (len(sys.argv) == 1):
    is_interactive = True
if len(sys.argv) > 1:
    if (sys.argv[1] == "--help" or sys.argv[1] == "-h"):
        print(f"python3 {sys.argv[0]} [expression]")
        print( "python3 {-v|-h|__VERSION__}")
        print( "  -v, --version                 print program version and exit")
        print( "      __VERSION__               output version in specific format")
        print( "      --license                 print program license")
        print(f"      --output-script-standard  output the script standard to the file 'script-{APP_SCRIPT_VERSION}-standard'")
        print( "  -h, --help       print this help page and exit")
        sys.exit()
    if (sys.argv[1] == "--version" or sys.argv[1] == "-v"):
        print(f"VERSION: {APP_VERSION_MAJOR}.{APP_VERSION_MINOR}")
        print(f"SCRIPT_VERSION: {APP_SCRIPT_VERSION}")
        sys.exit()
    if (sys.argv[1] == "__VERSION__"):
        print(f"{APP_VERSION_MAJOR}.{APP_VERSION_MINOR}")
        sys.exit()
    if sys.argv[1] == "--license":
        print_program_license()
        sys.exit()
    if sys.argv[1] == "--output-script-standard":
        standards_output_path = f"script-{APP_SCRIPT_VERSION}-standard"
        if CUSTOM_SCRIPT_VERSION:
            standards_output_path += "-custom"
        file_handle = open(standards_output_path, "w")
        file_handle.write("Comments:\n   Commented lines start with a  #  character.\n")
        file_handle.write("\nCommands description:\n   Command lines start with a  !  character.\n")
        file_handle.write("   Each command has a unique interface (set of parameters) and have unique functionality.\n")
        file_handle.write("   Commands allows for text to be surrounded in double quotes (\") to be passed into a single parameter literally.\n")
        file_handle.write("   Some characters can be escaped by placing a \\ directly in front of them.\n")
        file_handle.write("\nIdentifiers:\n")
        file_handle.write("   Used for variable names and iterator names.\n")
        file_handle.write("   Valid characters: Alphabetic or  _  followed by any number of alphanumeric or  _  .\n")
        file_handle.write("\nExpression:\n")
        file_handle.write("   Consists of Identifiers, constants, Unary-operators, Binary-Operators and variable assignments.\n")
        file_handle.write("   If a line does not begin with a  !  or  #  it is assumed to be a expression.\n")
        file_handle.write("\nVariables description:\n")
        file_handle.write("   All assigned variables are global variables, there are no local variables.\n")
        file_handle.write("   Variables can only store decimal (or floating point) numbers.\n")
        file_handle.write("\nVariable assignment:\n")
        file_handle.write("   <Identifier> = <Expression>\n")
        serialized_predefined_variables = " ".join(variables.keys())
        file_handle.write("\nPre-defined variables:\n")
        file_handle.write(f"   {serialized_predefined_variables}\n")
        serialized_consts = " ".join(KNOWN_CONSTS.keys())
        file_handle.write("\nConstants:\n")
        file_handle.write(f"   {serialized_consts}\n")
        serialized_comparison_operators = " ".join(comparison_operators.keys())
        file_handle.write("\nComparison operators (CMP-OP):\n")
        file_handle.write(f"   {serialized_comparison_operators}\n")
        longest_unary_fn_name = max([len(fn) for fn in KNOWN_FUNCTIONS.keys()])
        serialized_unary_functions = "\n".join([f"   {fn:<{longest_unary_fn_name}}  - {unary_function_descriptions.get(fn)}" for fn in KNOWN_FUNCTIONS.keys()])
        file_handle.write("\nUnary functions:\n")
        file_handle.write(f"{serialized_unary_functions}\n")
        longest_binary_fn_name = max([len(fn) for fn in BINARY_FUNCTIONS.keys()])
        serialized_binary_functions = "\n".join([f"   {fn:<{longest_binary_fn_name}}  - {binary_function_descriptions.get(fn)}" for fn in BINARY_FUNCTIONS.keys()])
        file_handle.write("\nBinary functions:\n")
        file_handle.write(f"{serialized_binary_functions}\n")
        function_precedences = list(map(lambda a: (a.precedence, a.lexeame), BINARY_FUNCTIONS.values()))
        function_precedences.append((UNARY_FUNCTION_PRECEDENCE_VALUE, "<UNARY-FUNCTIONS>"))
        function_precedences = sorted(function_precedences, key=lambda a: a[0])
        console_output_debug_msg(f"{function_precedences=}")
        grouped_function_precedences = [list(group) for key, group in itertools.groupby(function_precedences, lambda a: a[0])]
        console_output_debug_msg(f"{grouped_function_precedences=}")
        grouped_function_precedences = [tuple([item[1] for item in group]) for group in grouped_function_precedences]
        console_output_debug_msg(f"{grouped_function_precedences=}")
        file_handle.write("\nFunction precedences (from least to most):\n")
        for precedence_group in grouped_function_precedences:
            serialized_function_group = " ".join(precedence_group)
            file_handle.write(f"   {serialized_function_group}\n")

        longest_command_word_len = max([len(cmd[0].get_str()) for cmd in command_trees.values()])
        file_handle.write("\nAvailable commands: \n")
        file_handle.write(f"   !strict\n      Tells the interpreter to exit for any error that occurs\n")
        file_handle.write(f"   !debug [on|off|toggle]\n      Enable or disable debug output\n")
        file_handle.write(f"   !echo [on|off|toggle]\n      Enable or disable per line expression evaluation output\n")
        file_handle.write(f"   !endif\n      Marks end of a if block\n")
        file_handle.write(f"   !endwhile\n      Marks end of a while block\n")
        for command_tree, command_callback in command_trees.values():
            file_handle.write(f"   {command_tree.get_str()}\n      {command_process_descriptions.get(command_tree.name)}\n")
        file_handle.close()
        sys.exit()
    if (os.path.isfile(sys.argv[1])):
        # NOTE: This scope is the scripting system. Everything here is only for the scripting part
        echo_enabled = True
        exit_on_fail = False
        errors_count = 0
        def output_error(line_index: int, message: str) -> None:
            global errors_count
            errors_count += 1
            err_msg = f"[{line_index+1}] Error: {message}"
            if exit_on_fail:
                sys.exit(err_msg)
            else:
                print(err_msg)
        fh = open(sys.argv[1])
        contents = fh.read().split("\n")
        contents = list(zip(contents, range(0, len(contents))))
        for i in range(len(contents)):
            contents[i] = (contents[i][0].strip(), contents[i][1])
        fh.close()
        i = 0
        while i < len(contents):
            if len(contents[i][0]) == 0:
                contents.pop(i)
                continue
            i += 1
        i=0
        while i < len(contents):
            if contents[i][0][0] == '#':
                contents.pop(i)
                continue
            i += 1

        class WhileEmbed:
            def __init__(self, start_index: int):
                self.start_index = start_index
                self.end_index = None
            def is_end_set(self) -> bool:
                return self.end_index != None
        while_embed_objects: list[WhileEmbed] = []
        dont_inc_expression_this_iteration = False
        skip_till_next_while_end_count = 0
        skip_till_if_end_count = 0
        skip_expression_count = 0
        expressioni = -1
        while expressioni+1 < len(contents):
            if not dont_inc_expression_this_iteration:
                expressioni += 1
            else:
                dont_inc_expression_this_iteration = False
            (expression, line_index) = contents[expressioni]
        #for expressioni, (expression, line_index) in enumerate(contents):
            console_output_debug_msg(f"loop: expressioni:{expressioni} content:{contents[expressioni]}")
            if skip_expression_count > 0:
                skip_expression_count -= 1
                continue
            if skip_till_if_end_count > 0 or skip_till_next_while_end_count > 0:
                console_output_debug_msg(" skipping line, due to skip_till_if_end or skip_till_while_end")
                expression_split = parse_input_for_args(expression)
                if len(expression_split) == 0:
                    continue
                if skip_till_next_while_end_count > 0:
                    console_output_debug_msg(f"   skip_till_while_end {skip_till_next_while_end_count}")
                    if expression_split[0] == "!endwhile":
                        skip_till_next_while_end_count -= 1
                    if expression_split[0] == "!while":
                        skip_till_next_while_end_count += 1
                if expression_split[0] == "!endif":
                    console_output_debug_msg(f"   skip_till_if_end {skip_till_if_end_count}")
                    if skip_till_if_end_count == 0:
                        output_error(line_index, "endif: Unmatched endif")
                        continue
                    skip_till_if_end_count -= 1
                continue

            expression_split = parse_input_for_args(expression)
            if len(expression_split) == 0:
                console_output_debug_msg(" skipping line, expression line empty")
                continue
            if expression_split[0] == "!endwhile":
                if len(while_embed_objects) == 0:
                    output_error(line_index, f"endwhile: unmatched !endwhile")
                    continue
                while_object = while_embed_objects.pop()
                expressioni = while_object.start_index
                dont_inc_expression_this_iteration = True
                console_output_debug_msg(f"[{line_index+1}] Found !endwhile. Now jumping back to line {expressioni+1}  expressioni:{expressioni}")
                continue
            if expression_split[0][0] == "!":
                if expression_split[0] == "!endif":
                    console_output_debug_msg(f"[{line_index+1}] ignoring an endif command")
                    continue
                if expression_split[0] == "!strict":
                    exit_on_fail = True
                    continue
                elif expression_split[0] == "!debug":
                    if len(expression_split) <= 1:
                        ENABLED_DEBUG_OUTPUT = not ENABLED_DEBUG_OUTPUT
                        print("ENABLED DEBUG OUTPUT" if ENABLED_DEBUG_OUTPUT else "DISABLED DEBUG OUTPUT")
                    elif expression_split[1] == "on":
                        ENABLED_DEBUG_OUTPUT = True
                    elif expression_split[1] == "off":
                        ENABLED_DEBUG_OUTPUT = False
                    elif expression_split[1] == "toggle":
                        ENABLED_DEBUG_OUTPUT = not ENABLED_DEBUG_OUTPUT
                    else:
                        output_error(line_index, "debug: Invalid value for debug option")
                    continue
                elif expression_split[0] == "!echo":
                    if len(expression_split) <= 1:
                        echo_enabled = not echo_enabled
                        print("ENABLED ECHO OUTPUT" if echo_enabled else "DISABLED ECHO OUTPUT")
                    elif expression_split[1] == "on":
                        echo_enabled = True
                    elif expression_split[1] == "off":
                        echo_enabled = False
                    elif expression_split[1] == "toggle":
                        echo_enabled = not echo_enabled
                    else:
                        output_error(line_index, "echo: Invalid value for echo option")
                    continue
                if expression_split[0] in ["!if", "!while"]:
                    for command in ["if", "while"]:
                        command_match_object = command_trees[command][0].match_and_run(expression_split, line_index+1, None)
                        if not command_match_object.command_matched:
                            continue
                        if not command_match_object.args_matched:
                            sys.exit(f"Fatal error Missing or invalid arguments for {command} command statement")
                        if command == "if":
                            condition_true = command_match_object.values[1](command_match_object.values[0], command_match_object.values[2])
                            console_output_debug_msg(f"[{line_index+1}] if condition: {expression_split[1]} {expression_split[2]} {expression_split[3]} = {condition_true}")
                            contains_ifset_data = 'ifset' in command_match_object.tags
                            if contains_ifset_data:
                                if condition_true:
                                    variables[command_match_object.values[3]] = command_match_object.values[4]
                                break
                            if not condition_true:
                                skip_till_if_end_count += 1
                            break
                        elif command == "while":
                            condition_true = command_match_object.values[1](command_match_object.values[0], command_match_object.values[2])
                            if condition_true:
                                while_embed_objects.append(WhileEmbed(expressioni))
                            else:
                                console_output_debug_msg(f"[{line_index+1}] While condition unmet ({expression_split[1]};{command_match_object.values[0]} {expression_split[2]} {expression_split[3]};{command_match_object.values[2]} = {condition_true}). skipping to next endwhile")
                                skip_till_next_while_end_count = 1
                    continue

                command_matched = False
                for command, callback in command_trees.values():
                    data = command.match_and_run(expression_split, line_index+1, callback)
                    if data.command_matched and not data.args_matched:
                        sys.exit(f"Invalid command arguments to command {command.name}")
                    if data.command_matched and data.args_matched:
                        command_matched = True
                        if data.callback_had_errors():
                            sys.exit(f"Fatal error occurred during command {command.name}, exiting ...")
                        break
                if not command_matched:
                    output_error(line_index, f"Command: unrecognised command '{expression_split[0]}'")
                continue
            lex_tokens = lex(expression)
            lex_error_count = print_lex_errors(lex_tokens, f"{line_index+1}: ")
            if (lex_error_count > 0):
                errors_count += 1
                #print(f"{line_index+1}: {lex_error_count} error(s)")
                if exit_on_fail:
                    sys.exit(f"Lexer error on line {line_index+1}")
                continue
            evaluated_value, errors = eval_lex_tokens(lex_tokens)
            if (len(errors) > 0):
                errors_count += 1
                #print("{line_index+1}: Input had errors, no value returned", file = sys.stderr)
                for error in errors:
                    print(f"{line_index+1}: Error: {error}", file = sys.stderr)
                if exit_on_fail:
                    sys.exit(f"Evaluation error on line {line_index+1}")
                continue
            if echo_enabled:
                print(evaluated_value)

        if skip_till_if_end_count > 0:
            print("Warning: Not all if statements have been closed")
        sys.exit(errors_count != 0)

echo_enabled = True
while True:
    if is_interactive:
        try:
            expression = input(">> ").strip()
        except EOFError:
            print("\r")
            expression = "q"
        if len(expression) == 0:
            continue
        if expression == "q" or expression == "quit":
            sys.exit()
        if expression == "help" or expression == "h":
            print_constants()
            print_functions()
            print_commands()
            continue
        #expression_split = expression.strip().split()
        #while "" in expression_split:
        #    expression_split.remove("")
        expression_split = parse_input_for_args(expression)
        if len(expression_split) > 0:
            #expression_split[0] = expression_split[0].strip()
            if expression_split[0] == "exit":
                exit_code = 0
                if len(expression_split) > 1:
                    try:
                        exit_code = int(expression_split[1])
                    except ValueError:
                        var_val = variables.get(expression_split[1])
                        if var_val != None:
                            exit_code = int(var_val)
                sys.exit(exit_code)
            if expression_split[0] == "debug":
                if len(expression_split) <= 1:
                    ENABLED_DEBUG_OUTPUT = not ENABLED_DEBUG_OUTPUT
                    print("ENABLED DEBUG OUTPUT" if ENABLED_DEBUG_OUTPUT else "DISABLED DEBUG OUTPUT")
                elif expression_split[1] == "on":
                    ENABLED_DEBUG_OUTPUT = True
                elif expression_split[1] == "off":
                    ENABLED_DEBUG_OUTPUT = False
                elif expression_split[1] == "toggle":
                    ENABLED_DEBUG_OUTPUT = not ENABLED_DEBUG_OUTPUT
                else:
                    print("Error: Invalid value for debug option")
                continue
            if expression_split[0] == "echo":
                if len(expression_split) <= 1:
                    echo_enabled = not echo_enabled
                    print("ENABLED ECHO OUTPUT" if echo_enabled else "DISABLED ECHO OUTPUT")
                elif expression_split[1] == "on":
                    echo_enabled = True
                elif expression_split[1] == "off":
                    echo_enabled = False
                elif expression_split[1] == "toggle":
                    echo_enabled = not echo_enabled
                else:
                    print("Error: Invalid value for echo option")
                continue
            if expression_split[0] == "input":
                prompt = ""
                if len(expression_split) == 1:
                    prompt = "INPUT >> "
                else:
                    for i, text in enumerate(expression_split[1:]):
                        if i != 0:
                            prompt += " "
                        prompt += text
                variables["input"] = decimal.Decimal(get_user_number_input(prompt))
                continue
            if expression_split[0] == "print":
                output = ""
                if len(expression_split) >= 1:
                    for i, text in enumerate(expression_split[1:]):
                        if i != 0:
                            output += " "
                        output += text
                print(output)
                continue
            if expression_split[0] == "varout":
                if len(expression_split) > 1:
                    var_name = expression_split[1]
                    var_val = variables.get(var_name)
                    var_output = f"{var_val}"
                    include_name = False
                    if len(expression_split) > 2:
                        if expression_split[2] == "-name":
                            include_name = True
                    if include_name:
                        var_output = f"{var_name}={var_val}"
                    if var_val == None:
                        print(f"varout: variable '{var_name}' is not defined")
                    else:
                        print(var_output)
                continue

    else:
        expression = sys.argv[1]
    lex_tokens = lex(expression)
    lex_error_count = print_lex_errors(lex_tokens)
    if (lex_error_count > 0):
        if is_interactive:
            print(f"{lex_error_count} error(s)")
            continue
        else:
            print(f"{lex_error_count} error(s) occured in <expression>")
            sys.exit()

    console_output_debug_msg("All lex tokens:")
    for token_index, token in enumerate(lex_tokens):
        console_output_debug_msg(f" [{token_index}] {token.lexeame}")
    console_output_debug_msg("End of tokens")
    evaluated_value, errors = eval_lex_tokens(lex_tokens)
    if (len(errors) > 0):
        print("Input had errors, no value returned", file = sys.stderr)
        for error in errors:
            print(f"Error: {error}", file = sys.stderr)
        if is_interactive:
            continue
        else:
            sys.exit(1)
    if echo_enabled:
        print(evaluated_value)
    previous_answer = evaluated_value
    if (not is_interactive):
        sys.exit()
