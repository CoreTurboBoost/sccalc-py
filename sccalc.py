#!/bin/env python3

# Script Calc.py

import math
import decimal
import sys
import typing
import os

APP_VERSION_MAJOR = 0
APP_VERSION_MINOR = 7

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

def product(array: list) -> decimal.Decimal:
    if len(array) == 0:
        return 0
    val = 1
    for a in array:
        val *= a
    return val

KNOWN_CONSTS = {"pi": math.pi, "e": math.e, "deg2rad": (math.pi/180), "rad2deg": (180/math.pi)}
'''
NOTE: These functions take a single decimal.Decimal as input and returns a single Decimal.Decimal
'''
KNOWN_FUNCTIONS = {"sqrt": math.sqrt, "log10": log10, "log2": log2, "cos": math.cos, "sin": math.sin, "tan": math.tan, "cosec": cosec, "sec": sec, "cot": cot, "acos": math.acos, "asin": math.asin, "atan": math.atan}

variables = {"script_version": 1}
iterator_arrays = {}

previous_answer = 0

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
    TYPE_ADDITION = 4
    TYPE_SUBTRACTION = 5
    TYPE_MULTIPLICATION = 6
    TYPE_DIVISION = 7
    TYPE_EXPONENT = 8
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
        elif (enum_type == Token.TYPE_ADDITION):
            return "Addition"
        elif (enum_type == Token.TYPE_SUBTRACTION):
            return "Subtraction"
        elif (enum_type == Token.TYPE_MULTIPLICATION):
            return "Multiplication"
        elif (enum_type == Token.TYPE_DIVISION):
            return "Division"
        elif (enum_type == Token.TYPE_EXPONENT):
            return "Exponent"
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
    skip_char_count = 0
    tokens = []
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
        elif (char == '+'):
            tokens.append(Token('+', Token.TYPE_ADDITION, char_index, None))
        elif (char == '-'):
            tokens.append(Token('-', Token.TYPE_SUBTRACTION, char_index, None))
        elif (char == '*'):
            tokens.append(Token('*', Token.TYPE_MULTIPLICATION, char_index, None))
        elif (char == '/'):
            tokens.append(Token('/', Token.TYPE_DIVISION, char_index, None))
        elif (char == '^'):
            tokens.append(Token('^', Token.TYPE_EXPONENT, char_index, None))
        elif (char == '('):
            tokens.append(Token('(', Token.TYPE_OPEN_BRACKET, char_index, None))
        elif (char == ')'):
            tokens.append(Token(')', Token.TYPE_CLOSE_BRACKET, char_index, None))
        elif (char == '='):
            tokens.append(Token('=', Token.TYPE_ASSIGNMENT, char_index, None))
        else:
            error_object = TokenError()
            error_object.type = TokenError.TYPE_UNKNOWN_CHAR
            if (char.isprintable()):
                print_char = f"\'{char}\'"
            else:
                print_char = f"{ord(char)}"
            error_object.string = f"Unknown char {print_char}"
            cur_token = Token("", Token.TYPE_BAD, char_index, error_object)
            tokens.append(cur_token)
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
    return tokens

def get_lex_error_count(tokens : typing.List[Token]):
    error_count = 0
    for token in tokens:
        if (token.type == Token.TYPE_BAD):
            error_count += 1
    return error_count

def print_lex_errors(tokens : typing.List[Token], heading:str="") -> int:
    error_count = 0
    for token in tokens:
        if (token.type == Token.TYPE_BAD):
            print(f"{heading}TOKEN ERROR: char {token.char_index+1}. {token.error_object.string}.")
            error_count += 1
    return error_count

def eval_lex_tokens(tokens : typing.List[Token]):
    '''
    Returns list(evaluated_value: decimal.Decimal, errors: list[str])
       evaluated_value : decimal.Decimal() or None on error.
       errors : list[str], empty list on success.
    '''
    tokens = tokens.copy()
    def get_op_precedence(token_type : Token):
        # larger number greater precedence
        if (token_type == Token.TYPE_NONE or token_type == Token.TYPE_OPEN_BRACKET):
            return 0
        if (token_type == Token.TYPE_ASSIGNMENT):
            return 1
        if (token_type == Token.TYPE_ADDITION or token_type == Token.TYPE_SUBTRACTION):
            return 2
        if (token_type == Token.TYPE_MULTIPLICATION or token_type == Token.TYPE_DIVISION):
            return 3
        if (token_type == Token.TYPE_EXPONENT):
            return 4
        if (token_type == Token.TYPE_FUNCTION):
            return 5
        console_output_debug_msg(f"get_precedence fn param not recognised token_type:{token_type}")
        return -1
    def is_operator(token_type : Token):
        if (token_type == Token.TYPE_ADDITION or token_type == Token.TYPE_SUBTRACTION):
            return True
        if (token_type == Token.TYPE_MULTIPLICATION or token_type == Token.TYPE_DIVISION):
            return True
        if (token_type == Token.TYPE_EXPONENT):
            return True
        if (token_type == Token.TYPE_FUNCTION):
            return True
        if (token_type == Token.TYPE_ASSIGNMENT):
            return True
        return False

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
        if (cur_token.type == Token.TYPE_SUBTRACTION):
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
            cur_func_prec = get_op_precedence(token.type)
            if len(operators_stack) > 0:
                stack_top_op_precedence = get_op_precedence(operators_stack[-1].type)
                while stack_top_op_precedence >= cur_func_prec and operators_stack[-1].type != Token.TYPE_FUNCTION:
                    post_fix_token_list.append(operators_stack.pop())
                    if (len(operators_stack) > 0):
                        stack_top_op_precedence = get_op_precedence(operators_stack[-1].type)
                    else:
                        break
            operators_stack.append(token)

        elif (is_operator(token.type)):
            console_output_debug_msg(f"[{token_index}] Considered token as an operator, {token}")
            cur_op_precedence = get_op_precedence(token.type)
            if (len(operators_stack) > 0):
                stack_top_op_precedence = get_op_precedence(operators_stack[-1].type)
            else:
                stack_top_op_precedence = get_op_precedence(Token.TYPE_NONE)
            console_output_debug_msg(f"[{token_index}] both precedences (cur, stack_top): ({cur_op_precedence}, {stack_top_op_precedence})")
            if (cur_op_precedence > stack_top_op_precedence):
                console_output_debug_msg(f"[{token_index}] Added {token.lexeame} to op stack")
            while (stack_top_op_precedence >= cur_op_precedence):
                console_output_debug_msg(f"[{token_index}] Adding operator to post-fix list ({operators_stack[-1].lexeame})")
                console_output_debug_msg(f"[{token_index}] Adding operator to post-fix list ({operators_stack[-1].lexeame}) then added another operator to operators_stack ({token.lexeame})")
                post_fix_token_list.append(operators_stack.pop())
                if (len(operators_stack) > 0):
                    stack_top_op_precedence = get_op_precedence(operators_stack[-1].type)
                else:
                    stack_top_op_precedence = get_op_precedence(Token.TYPE_NONE)
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
        errors.append(f"Bracket mismatch. Some brackets dont have \')\', {open_bracket_count} specifically")

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
            if (token.type == Token.TYPE_ADDITION):
                if not (is_number(operand_a) and is_number(operand_b)):
                    errors.append(f"{[token.char_index+1]} Expecting a number, not a variable")
                    break
                numbers_stack.append(operand_a + operand_b)
            if (token.type == Token.TYPE_SUBTRACTION):
                if not (is_number(operand_a) and is_number(operand_b)):
                    errors.append(f"{[token.char_index+1]} Expecting a number, not a variable")
                    break
                numbers_stack.append(operand_b - operand_a)
            if (token.type == Token.TYPE_MULTIPLICATION):
                if not (is_number(operand_a) and is_number(operand_b)):
                    errors.append(f"{[token.char_index+1]} Expecting a number, not a variable")
                    break
                numbers_stack.append(operand_a * operand_b)
            if (token.type == Token.TYPE_DIVISION):
                if not (is_number(operand_a) and is_number(operand_b)):
                    errors.append(f"{[token.char_index+1]} Expecting a number, not a variable")
                    break
                if (operand_a == 0):
                    errors.append(f"[{token.char_index+1}] Division by zero")
                    break
                numbers_stack.append(operand_b / operand_a)
            if (token.type == Token.TYPE_EXPONENT):
                if not (is_number(operand_a) and is_number(operand_b)):
                    errors.append(f"{[token.char_index+1]} Expecting a number, not a variable")
                    break
                console_output_debug_msg(f"exponent operation: {operand_b}^{operand_a}")
                try:
                    numbers_stack.append(decimal.Decimal(math.pow(operand_b, operand_a)))
                except:
                    errors.append(f"[{token.char_index+1}] expression: \'{operand_b}^({operand_a})\' failed, {sys.exc_info()[1]}")
            if (token.type == Token.TYPE_ASSIGNMENT):
                if not is_number(operand_a):
                    errors.append(f"{[token.char_index+1]} Expecting a number, not a variable")
                    break
                if not isinstance(operand_b, str):
                    errors.append(f"{[token.char_index+1]} Assignment can only occur to a variable")
                    break
                variables[operand_b] = operand_a
                numbers_stack.append(operand_a) # Going to return the value that got assigned to the variable

    if (len(numbers_stack) > 1):
        errors.append(f"Too few operators, for the number of operands, {len(numbers_stack)} specifically")
        console_output_debug_msg(f"Error: numbers_stack:{numbers_stack}")

    if (len(errors) > 0):
        return (None, errors)
    return (numbers_stack[0], errors)

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

def get_user_number_input(prompt) -> float:
    is_valid = False
    number = 0
    while not is_valid:
        is_valid = True
        try:
            number = float(input(prompt))
        except:
            print("Input Error: Expected an int")
            is_valid = False
    return number

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
        print( "  -v, --version    print program version and exit")
        print( "      __VERSION__  output version in specific format")
        print( "  -h, --help       print this help page and exit")
        sys.exit()
    if (sys.argv[1] == "--version" or sys.argv[1] == "-v"):
        print(f"VERSION: {APP_VERSION_MAJOR}.{APP_VERSION_MINOR}")
        sys.exit()
    if (sys.argv[1] == "__VERSION__"):
        print(f"{APP_VERSION_MAJOR}.{APP_VERSION_MINOR}")
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
        def get_literal_or_var(literal_or_var: str) -> float or None:
            try:
                return float(literal_or_var)
            except ValueError:
                console_output_debug_msg(f"get_literal_or_var: Failed to convert {literal_or_var} to float")
                var_val = variables.get(literal_or_var)
                return var_val
        def apply_condition_operator(left: float, right: float, operator: str) -> bool or None:
            condition_true = False
            if operator == "==":
                return left == right
            elif operator == "!=":
                return left != right
            elif operator == ">=":
                return left >= right
            elif operator == "<=":
                return left <= right
            elif operator == ">":
                return left > right
            elif operator == "<":
                return left < right
            return None
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
                expression_split = parse_input_for_args(expression)
                if skip_till_next_while_end_count > 0:
                    if len(expression_split[0]) > 0 and expression_split[0] == "!endwhile":
                        skip_till_next_while_end_count -= 1
                    if len(expression_split[0]) > 0 and expression_split[0] == "!while":
                        skip_till_next_while_end_count += 1
                if len(expression_split[0]) > 0 and expression_split[0] == "!endif":
                    if skip_till_if_end_count == 0:
                        output_error(line_index, "endif: Unmatched endif")
                        continue
                    skip_till_if_end_count -= 1
                continue
            expression_split = parse_input_for_args(expression)
            if len(expression_split[0]) > 0 and expression_split[0] == "!endwhile":
                if len(while_embed_objects) == 0:
                    output_error(line_index, f"endwhile: unmatched !endwhile")
                    continue
                while_object = while_embed_objects.pop()
                start_index = while_object.start_index
                expressioni = start_index
                dont_inc_expression_this_iteration = True
                console_output_debug_msg(f"[{line_index+1}] Found !endwhile. Now jumping back to line {start_index+1}  expressioni:{expressioni}")
                continue
            if len(expression_split[0]) > 0 and expression_split[0][0] == "!":
                if expression_split[0] == "!strict":
                    exit_on_fail = True
                if expression_split[0] == "!debug":
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
                if expression_split[0] == "!echo":
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
                if expression_split[0] == "!input":
                    prompt = ""
                    if len(expression_split) == 1:
                        prompt = "INPUT >> "
                    else:
                        for i, text in enumerate(expression_split[1:]):
                            if i != 0:
                                prompt += " "
                            prompt += text
                    variables["input"] = decimal.Decimal(get_user_number_input(prompt))
                if expression_split[0] == "!print":
                    output = ""
                    if len(expression_split) >= 1:
                        for i, text in enumerate(expression_split[1:]):
                            if i != 0:
                                output += " "
                            output += text
                    print(output)
                if expression_split[0] == "!varout":
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
                            output_error(line_index, f"varout: variable '{var_name}' is not defined")
                        else:
                            print(var_output)
                if expression_split[0] == "!exit":
                    exit_code = 0
                    if len(expression_split) > 1:
                        try:
                            exit_code = int(expression_split[1])
                        except ValueError:
                            var_val = variables.get(expression_split[1])
                            if var_val != None:
                                exit_code = int(var_val)
                    sys.exit(exit_code)
                if expression_split[0] == "!if":
                    if len(expression_split) < 4:
                        sys.exit(f"[{line_index+1}] Error: Incorrect if statement format, expected '!if <NUMBER|VAR> <OP> <NUMBER|VAR> [<VAR> <NUMBER|VAR>]'")
                    if_left_val = 0
                    if_right_val = 0
                    if_operator = None
                    if_left_val = get_literal_or_var(expression_split[1])
                    if if_left_val == None:
                        output_error(line_index, f"if: Unrecognised variable name {expression_split[1]}")
                        continue
                    console_output_debug_msg(f"if: found left val {if_left_val}")
                    if_right_val = get_literal_or_var(expression_split[3])
                    if if_right_val == None:
                        output_error(line_index, f"if: Unrecognised variable name {expression_split[3]}")
                        continue
                    console_output_debug_msg(f"if: found right val {if_right_val}")
                    if_operator = expression_split[2]


                    if_condition_true = apply_condition_operator(if_left_val, if_right_val, if_operator)
                    if if_condition_true == None:
                        output_error(line_index, f"if: unrecognised condition operator {if_operator}")
                        if_condition_true = False
                    console_output_debug_msg(f"if: condition is {if_left_val} {if_operator} {if_right_val} = {if_condition_true}")
                    if len(expression_split) >= 6:
                        console_output_debug_msg(f"ifset: got set_var: {expression_split[4]}:{type(expression_split[4])}, set_val: {expression_split[5]}:{type(expression_split[5])}")
                        set_var_name = expression_split[4]
                        set_val = get_literal_or_var(expression_split[5])
                        console_output_debug_msg(f"ifset: have been given set_var: {set_var_name}, set_val: {set_val}")
                        if set_val == None:
                            output_error(line_index, f"if: Unrecognised variable name {expression_split[5]}")
                        if if_condition_true:
                            variables[set_var_name] = set_val
                    else:
                        if not if_condition_true:
                            skip_till_if_end_count += 1
                if expression_split[0] == "!repeat":
                    if len(expression_split) < 3:
                        sys.exit(f"[{line_index+1}] Error: Incorrect repeat statement format, expected '!repeat <NUMBER|VAR> <EXPRESSION>'")
                    iteration_count = int(get_literal_or_var(expression_split[1]))
                    if iteration_count == None:
                        output_error(line_index, f"repeat: Unrecognised variable name {expression_split[1]}")
                        iteration_count = 0
                    repeat_expression = expression_split[2]
                    for _ in range(iteration_count):
                        lex_tokens = lex(repeat_expression) # Only need to do this to update the variabels (as they get subsituted here, if that is moved, then only need to call once before the whole loop)
                        lex_tokens_error_count = print_lex_errors(lex_tokens, f"{line_index+1} in repeat: ")
                        if lex_tokens_error_count > 0:
                            sys.exit(f"{line_index+1} Lexer error(s) in repeat statement")
                        evaluated_value, eval_errors = eval_lex_tokens(lex_tokens)
                        if len(eval_errors) > 0:
                            for error in eval_errors:
                                print(f"{line_index+1} Error: repeat: {error}")
                            sys.exit(f"{line_index+1} Eval error(s) in repeat statement")
                if expression_split[0] == "!while":
                    if len(expression_split) < 4:
                        sys.exit(f"{line_index+1} Error: while: Incorrect while statement format, expected '!while <NUMBER|VAR> <OP> <NUMBER|VAR>'")
                    left_operand = get_literal_or_var(expression_split[1])
                    cmp_operator = expression_split[2]
                    right_operand = get_literal_or_var(expression_split[3])
                    if left_operand == None:
                        output_error(line_index, f"while: Unrecognised variable name {expression_split[1]}")
                        continue
                    if right_operand == None:
                        output_error(line_index, f"while: Unrecognised variable name {expression_split[3]}")
                        continue
                    condition_true = apply_condition_operator(left_operand, right_operand, cmp_operator)
                    if condition_true == None:
                        output_error(line_index, f"while: Unrecognised comparison operator {cmp_operator}")
                        continue
                    if not condition_true:
                        console_output_debug_msg(f"[{line_index+1}] While condition unmet. skipping to next endwhile")
                        skip_till_next_while_end_count = 1
                    else:
                        while_embed_objects.append(WhileEmbed(expressioni))
                if expression_split[0] == "!yield":
                    if len(expression_split) < 3:
                        sys.exit(f"[{line_index+1}] Error: yield: Incorrect yield format statement, expected '!yield <ITER> <NUMBER|VAR>'")
                    iterator_name = expression_split[1]
                    new_append_value = get_literal_or_var(expression_split[2])
                    if new_append_value == None:
                        output_error(line_index, f"yield: variable '{expression_split[2]}' is not defined")
                        continue
                    if iterator_arrays.get(iterator_name) == None:
                        iterator_arrays[iterator_name] = []
                    iterator_arrays[iterator_name].append(new_append_value)
                    console_output_debug_msg(f"Yielded {new_append_value} into iterator {iterator_name}, new_iterator {iterator_arrays[iterator_name]}")
                if expression_split[0] == "!clear":
                    if len(expression_split) < 2:
                        sys.exit(f"[{line_index+1}] Error: clear: Incorrect clear format statement, expected '!clear <ITER>'")
                    iterator_name = expression_split[1]
                    iterator_arrays[iterator_name] = []
                    console_output_debug_msg(f"Cleared iterator {iterator_name}")
                if expression_split[0] == "!dup":
                    if len(expression_split) < 3:
                        sys.exit(f"[{line_index+1}] Error: dup: Incorrect dup format statement, expected '!dup <OUT-ITER> <IN-ITER>'")
                    out_iterator_name = expression_split[1]
                    in_iterator_name = expression_split[2]
                    in_iterator = iterator_arrays.get(in_iterator_name)
                    if in_iterator == None:
                        output_error(line_index, f"dup: Iterator '{in_iterator_name}' is not defined")
                        continue
                    iterator_arrays[out_iterator_name] = in_iterator.copy()
                    console_output_debug_msg(f"Duplicated iterator {in_iterator_name}:{in_iterator} to {out_iterator_name}:{iterator_arrays[out_iterator_name]}")
                if expression_split[0] == "!count":
                    if len(expression_split) < 3:
                        sys.exit(f"[{line_index+1}] Error: count: Incorrect count format statement, expected '!count <ITER> <VAR>'")
                    iterator_name = expression_split[1]
                    iterator = iterator_arrays.get(iterator_name)
                    output_variable_name = expression_split[2]
                    if iterator == None:
                        output_error(line_index, f"count: Iterator '{iterator_name}' is not defined")
                        continue
                    variables[output_variable_name] = len(iterator_arrays[iterator_name])
                if expression_split[0] == "!map":
                    if len(expression_split) < 3:
                        sys.exit(f"[{line_index+1}] Error: map: Incorrect map format statement, expected '!map <ITER> <EXPRESSION>")
                    iterator_name = expression_split[1]
                    map_expression = expression_split[2]
                    iterator = iterator_arrays.get(iterator_name)
                    if iterator == None:
                        output_error(line_index, f"map: Iterator '{iterator_name}' is not defined")
                        continue
                    iter_len = len(iterator)
                    for i in range(iter_len):
                        cur_elm = iterator_arrays[iterator_name][i]
                        variables[iterator_name] = decimal.Decimal(cur_elm)
                        lex_tokens = lex(map_expression)
                        lex_error_count = print_lex_errors(lex_tokens, f"[{line_index+1}] map: ")
                        if lex_error_count > 0:
                            sys.exit(f"[{line_index+1}] map: {lex_error_count} lexer errors")
                        evaluated_value, eval_errors = eval_lex_tokens(lex_tokens)
                        if len(eval_errors) > 0:
                            for error in eval_errors:
                                print(f"[{line_index+1}] map: eval error {error}")
                            output_error(line_index, f"map: {len(eval_errors)} eval errors occured")
                            continue
                        iterator_arrays[iterator_name][i] = evaluated_value
                if expression_split[0] == "!filter":
                    #if len(expression_split) < 3:
                        #sys.exit(f"[{line_index+1}] filter: Incorrect filter statement, expected '!filter <ITER> <COMPARISON-EXPRESSION>")
                    if len(expression_split) < 5:
                        sys.exit(f"[{line_index+1}] filter: Incorrect filter statement, expected '!filter <ITER> <NUMBER|VAR> <CMP_OP> <NUMBER|VAR>")
                    iterator_name = expression_split[1]
                    iterator = iterator_arrays.get(iterator_name)
                    left_val = get_literal_or_var(expression_split[2])
                    right_val = get_literal_or_var(expression_split[4])
                    if left_val == None:
                        output_error(line_index, f"filter: Variable '{expression_split[2]}' is not defined")
                        continue
                    if right_val == None:
                        output_error(line_index, f"filter: Variable '{expression_split[4]}' is not defined")
                        continue
                    operator = expression_split[3]
                    condition_true = apply_condition_operator(left_val, right_val, operator)
                    if condition_true == None:
                        output_error(line_index, f"filter: Operator '{expression_split[3]}' is not recognised")
                        continue
                    if iterator == None:
                        output_error(line_index, f"filter: Iterator '{iterator_name}' is not defined")
                        continue
                    iter_len = len(iterator)
                    filtered_array = []
                    for i in range(iter_len):
                        cur_elm = iterator_arrays[iterator_name][i]
                        variables[iterator_name] = decimal.Decimal(cur_elm)
                        left_val = get_literal_or_var(expression_split[2])
                        right_val = get_literal_or_var(expression_split[4])
                        condition_true = apply_condition_operator(left_val, right_val, operator)
                        if condition_true:
                            filtered_array.append(cur_elm)
                    iterator_arrays[iterator_name] = filtered_array

                    #filtered_array = []
                    #for i in range(iter_len):
                    #    cur_elm = iterator_arrays[iterator_name][i]
                    #    variables[iterator_name] = decimal.Decimal(cur_elm)
                    #    lex_tokens = lex(map_expression)
                    #    lex_error_count = print_lex_errors(lex_tokens, f"[{line_index+1}] map: ")
                    #    if lex_error_count > 0:
                    #        sys.exit(f"[{line_index+1}] map: {lex_error_count} lexer errors")
                    #    evaluated_value, eval_errors = eval_lex_tokens(lex_tokens)
                    #    if len(eval_errors) > 0:
                    #        for error in eval_errors:
                    #            print(f"[{line_index+1}] map: eval error {error}")
                    #        output_error(line_index, f"map: {len(eval_errors)} eval errors occured")
                    #        continue
                    #    if evaluated_value:
                    #        filtered_array.append(cur_elm)
                    #iterator_arrays[iterator_name] = filtered_array
                if expression_split[0] == "!next":
                    if len(expression_split) < 2:
                        sys.exit(f"[{line_index+1}] Error: next: Incorrect next command format, expected '!next <ITER>'")
                    iterator_name = expression_split[1]
                    iterator = iterator_arrays.get(iterator_name)
                    if iterator == None:
                        output_error(line_index, f"next: Iterator '{iterator_name}' is not defined")
                        continue
                    if len(iterator) == 0:
                        continue # If the iterator is empty, dont update any variables
                    cur_val = iterator_arrays[iterator_name].pop(0)
                    variables[iterator_name] = decimal.Decimal(cur_val)
                if expression_split[0] == "!sum":
                    if len(expression_split) < 3:
                        sys.exit(f"[{line_index+1}] Error: sum: Incorrect sum command format, expected '!sum <ITER> <VAR>'")
                    iterator_name = expression_split[1]
                    variable_name = expression_split[2]
                    iterator = iterator_arrays.get(iterator_name)
                    if iterator == None:
                        output_error(line_index, f"sum: Iterator '{iterator_name}' is not defined")
                        continue
                    variables[variable_name] = sum(iterator)
                if expression_split[0] == "!product":
                    if len(expression_split) < 3:
                        sys.exit(f"[{line_index+1}] Error: product: Incorrect product command format, expected '!product <ITER> <VAR>'")
                    iterator_name = expression_split[1]
                    variable_name = expression_split[2]
                    iterator = iterator_arrays.get(iterator_name)
                    if iterator == None:
                        output_error(line_index, f"product: Iterator '{iterator_name}' is not defined")
                        continue
                    variables[variable_name] = product(iterator)
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
