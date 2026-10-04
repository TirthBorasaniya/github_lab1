"""
Safe expression evaluator for the scientific calculator built on the Python abstract syntax tree.
Only numeric literals, a fixed set of operators, named constants, and whitelisted functions
are allowed.
"""

import ast
import math
from functools import partial

from src import calculator as calc

MAX_EXPRESSION_LENGTH = 200
CONSTANT_DICT = {"pi": math.pi, "e": math.e}
BINARY_OPERATOR_DICT = {
    ast.Add: calc.fun1,
    ast.Sub: calc.fun2,
    ast.Mult: calc.fun3,
    ast.Div: calc.divide,
    ast.Pow: calc.power,
}
ANGLE_FUNCTION_DICT = {
    "sin": calc.sin,
    "cos": calc.cos,
    "tan": calc.tan,
    "asin": calc.asin,
    "acos": calc.acos,
    "atan": calc.atan,
}
PLAIN_FUNCTION_DICT = {
    "sqrt": calc.sqrt,
    "root": calc.nth_root,
    "log": calc.log,
    "ln": calc.ln,
    "exp": calc.exp,
    "abs": calc.absolute,
    "fact": calc.factorial,
    "nCr": calc.n_choose_r,
    "nPr": calc.n_permute_r,
}


def _build_function_dict(angle_mode: str) -> dict:
    """Return the whitelisted function table with trigonometric functions bound to angle_mode."""
    function_dict = dict(PLAIN_FUNCTION_DICT)
    function_dict.update(
        {name: partial(func, angle_mode=angle_mode) for name, func in ANGLE_FUNCTION_DICT.items()}
    )
    return function_dict


def _evaluate_constant(node: ast.Constant) -> float:
    """Return a numeric literal as float, rejecting non-numeric and non-finite literals."""
    if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
        raise ValueError(f"unsupported literal: {node.value!r}")
    value = float(node.value)
    if math.isinf(value):
        raise ValueError("numeric literal out of range")
    return value


def _evaluate_call(node: ast.Call, name_dict: dict, function_dict: dict) -> float:
    """Evaluate a call to a whitelisted function with positional arguments only."""
    if not isinstance(node.func, ast.Name) or node.func.id not in function_dict:
        raise ValueError(f"unsupported function call: {ast.unparse(node.func)}")
    if node.keywords:
        raise ValueError("keyword arguments are not supported")
    arg_list = [_evaluate_node(arg, name_dict, function_dict) for arg in node.args]
    return function_dict[node.func.id](*arg_list)


def _evaluate_node(node: ast.AST, name_dict: dict, function_dict: dict) -> float:
    """Recursively evaluate a whitelisted AST node."""
    if isinstance(node, ast.Expression):
        return _evaluate_node(node.body, name_dict, function_dict)

    if isinstance(node, ast.Constant):
        return _evaluate_constant(node)

    if isinstance(node, ast.Name):
        if node.id not in name_dict:
            raise ValueError(f"unknown name: {node.id}")
        return name_dict[node.id]

    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        operand = _evaluate_node(node.operand, name_dict, function_dict)
        return -operand if isinstance(node.op, ast.USub) else operand

    if isinstance(node, ast.BinOp) and type(node.op) in BINARY_OPERATOR_DICT:
        left = _evaluate_node(node.left, name_dict, function_dict)
        right = _evaluate_node(node.right, name_dict, function_dict)
        return BINARY_OPERATOR_DICT[type(node.op)](left, right)

    if isinstance(node, ast.Call):
        return _evaluate_call(node, name_dict, function_dict)

    raise ValueError(f"unsupported syntax: {type(node).__name__}")


def evaluate(expression, angle_mode=calc.DEFAULT_ANGLE_MODE, ans=0.0, memory=0.0):
    """
    Evaluate a calculator expression without using eval.

    Supports + - * / and ^ (or **) with standard precedence, unary minus, parentheses,
    the constants pi and e, the names ans and mem, and the functions in
    PLAIN_FUNCTION_DICT and ANGLE_FUNCTION_DICT. Example: "2*sin(30) + sqrt(16)".

    Parameters
    ----------
    expression : str
        Expression text, at most MAX_EXPRESSION_LENGTH characters.
    angle_mode : str
        "rad" or "deg"; applies to trigonometric functions.
    ans : float
        Value bound to the name ans (previous result).
    memory : float
        Value bound to the name mem (memory register).

    Returns
    -------
    result : float
        Evaluated result.
    """
    if not isinstance(expression, str):
        raise TypeError(f"expression must be a str, got {type(expression).__name__}")
    calc.validate_angle_mode(angle_mode)

    expression = expression.strip()
    if not expression:
        raise ValueError("expression must not be empty")
    if len(expression) > MAX_EXPRESSION_LENGTH:
        raise ValueError(f"expression exceeds {MAX_EXPRESSION_LENGTH} characters")

    try:
        tree = ast.parse(expression.replace("^", "**"), mode="eval")
    except SyntaxError as err:
        raise ValueError(f"invalid expression: {expression}") from err

    name_dict = {**CONSTANT_DICT, "ans": ans, "mem": memory}
    function_dict = _build_function_dict(angle_mode)
    return float(_evaluate_node(tree, name_dict, function_dict))
