"""
Pytest suite for the scientific calculator covering functions, expression parsing, state, and CLI.
Includes data-driven cases loaded from data/test_cases.csv.
"""

import csv
import math
from pathlib import Path

import pytest

from src import calculator as calc
from src.expression import MAX_EXPRESSION_LENGTH, evaluate
from src.scientific_calculator import (
    HELP_TEXT,
    MAX_HISTORY,
    ScientificCalculator,
    format_result,
    handle_command,
    main,
    run_repl,
)

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "test_cases.csv"


def load_test_cases(csv_path):
    """Load (expression, angle_mode, expected) tuples from the test case CSV."""
    with open(csv_path, newline="") as f:
        return [
            (row["expression"], row["angle_mode"], float(row["expected"]))
            for row in csv.DictReader(f)
        ]


TEST_CASE_LIST = load_test_cases(DATA_PATH)


# ---------------------------------------------------------------------------
# Original lab functions
# ---------------------------------------------------------------------------

def test_fun1():
    assert calc.fun1(2, 3) == 5
    assert calc.fun1(5, 0) == 5
    assert calc.fun1(-1, 1) == 0
    assert calc.fun1(-1, -1) == -2


def test_fun2():
    assert calc.fun2(2, 3) == -1
    assert calc.fun2(5, 0) == 5
    assert calc.fun2(-1, 1) == -2
    assert calc.fun2(-1, -1) == 0


def test_fun3():
    assert calc.fun3(2, 3) == 6
    assert calc.fun3(5, 0) == 0
    assert calc.fun3(-1, 1) == -1
    assert calc.fun3(-1, -1) == 1


def test_fun4():
    assert calc.fun4(2, 3) == 10
    assert calc.fun4(5, 0) == 10
    assert calc.fun4(-1, -1) == -1


@pytest.mark.parametrize("func", [calc.fun1, calc.fun2, calc.fun3, calc.fun4])
@pytest.mark.parametrize("bad_value", ["2", None, True, [1]])
def test_original_functions_reject_non_numbers(func, bad_value):
    with pytest.raises(TypeError):
        func(bad_value, 1)


# ---------------------------------------------------------------------------
# Scientific functions
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "func, args, expected",
    [
        (calc.divide, (7, 2), 3.5),
        (calc.power, (2, 10), 1024),
        (calc.power, (2, -1), 0.5),
        (calc.power, (-2, 3), -8),
        (calc.sqrt, (2,), math.sqrt(2)),
        (calc.nth_root, (27, 3), 3),
        (calc.nth_root, (-32, 5), -2),
        (calc.nth_root, (4, -2), 0.5),
        (calc.log, (1000,), 3),
        (calc.log, (8, 2), 3),
        (calc.log, (81, 3), 4),
        (calc.ln, (math.e,), 1),
        (calc.exp, (1,), math.e),
        (calc.absolute, (-4,), 4),
        (calc.factorial, (0,), 1),
        (calc.factorial, (5.0,), 120),
        (calc.n_choose_r, (10, 3), 120),
        (calc.n_permute_r, (10, 3), 720),
    ],
)
def test_scientific_functions(func, args, expected):
    assert func(*args) == pytest.approx(expected)


@pytest.mark.parametrize(
    "func, x, angle_mode, expected",
    [
        (calc.sin, 30, "deg", 0.5),
        (calc.sin, math.pi / 2, "rad", 1),
        (calc.cos, 60, "deg", 0.5),
        (calc.cos, math.pi, "rad", -1),
        (calc.tan, 45, "deg", 1),
        (calc.tan, 0, "rad", 0),
        (calc.asin, 0.5, "deg", 30),
        (calc.acos, 0, "deg", 90),
        (calc.atan, 1, "rad", math.pi / 4),
    ],
)
def test_trigonometry(func, x, angle_mode, expected):
    assert func(x, angle_mode) == pytest.approx(expected)


@pytest.mark.parametrize(
    "func, x", [(calc.sin, 180), (calc.cos, 90), (calc.tan, 180)]
)
def test_trigonometry_snaps_residue_to_zero(func, x):
    assert func(x, "deg") == 0.0


@pytest.mark.parametrize(
    "func, args, exc",
    [
        (calc.divide, (1, 0), ZeroDivisionError),
        (calc.power, (0, -1), ZeroDivisionError),
        (calc.power, (-8, 1 / 3), ValueError),
        (calc.power, (10.0, 1000), OverflowError),
        (calc.sqrt, (-1,), ValueError),
        (calc.nth_root, (-16, 4), ValueError),
        (calc.nth_root, (8, 0), ValueError),
        (calc.nth_root, (8, 1.5), ValueError),
        (calc.log, (0,), ValueError),
        (calc.log, (8, 1), ValueError),
        (calc.log, (8, -2), ValueError),
        (calc.ln, (-1,), ValueError),
        (calc.exp, (1000,), OverflowError),
        (calc.tan, (90, "deg"), ValueError),
        (calc.asin, (2,), ValueError),
        (calc.acos, (-1.5,), ValueError),
        (calc.sin, (30, "grad"), ValueError),
        (calc.sin, (float("nan"),), ValueError),
        (calc.factorial, (-1,), ValueError),
        (calc.factorial, (2.5,), ValueError),
        (calc.factorial, (calc.MAX_FACTORIAL_INPUT + 1,), ValueError),
        (calc.factorial, ("5",), TypeError),
        (calc.n_choose_r, (3, 5), ValueError),
        (calc.n_permute_r, (-1, 0), ValueError),
    ],
)
def test_scientific_function_errors(func, args, exc):
    with pytest.raises(exc):
        func(*args)


# ---------------------------------------------------------------------------
# Expression evaluator
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "expression, angle_mode, expected",
    TEST_CASE_LIST,
    ids=[case[0] for case in TEST_CASE_LIST],
)
def test_expression_cases_from_csv(expression, angle_mode, expected):
    assert evaluate(expression, angle_mode=angle_mode) == pytest.approx(expected)


@pytest.mark.parametrize(
    "expression, expected",
    [("2+3*4", 14), ("(2+3)*4", 20), ("-2^2", -4), ("2^-1", 0.5), ("2**3", 8), ("+5", 5)],
)
def test_operator_precedence(expression, expected):
    assert evaluate(expression) == pytest.approx(expected)


def test_named_values():
    assert evaluate("ans*2", ans=21) == 42
    assert evaluate("mem+1", memory=4) == 5
    assert evaluate("2*pi") == pytest.approx(2 * math.pi)


@pytest.mark.parametrize(
    "expression",
    [
        "__import__('os').system('ls')",
        "open('x')",
        "x+1",
        "[1, 2]",
        "'a'",
        "True + 1",
        "2 if 1 else 3",
        "math.pi",
        "sqrt(x=4)",
        "lambda: 1",
        "2 // 3",
        "2 % 3",
        "",
        "   ",
        "2+",
        "1e400",
        "1" * (MAX_EXPRESSION_LENGTH + 1),
    ],
)
def test_evaluate_rejects_unsafe_or_invalid_input(expression):
    with pytest.raises(ValueError):
        evaluate(expression)


def test_evaluate_rejects_non_string():
    with pytest.raises(TypeError):
        evaluate(42)


def test_evaluate_propagates_math_errors():
    with pytest.raises(ZeroDivisionError):
        evaluate("1/0")
    with pytest.raises(ValueError):
        evaluate("sin(30)", angle_mode="grad")


# ---------------------------------------------------------------------------
# Stateful calculator
# ---------------------------------------------------------------------------

def test_ans_and_history():
    calculator = ScientificCalculator()
    calculator.evaluate("2+3")
    assert calculator.evaluate("ans*10") == 50
    assert calculator.history_list == [("2+3", 5.0), ("ans*10", 50.0)]
    calculator.clear_history()
    assert calculator.history_list == []


def test_memory_register():
    calculator = ScientificCalculator()
    calculator.evaluate("6*7")
    calculator.memory_add()
    calculator.memory_add(8)
    assert calculator.memory_recall() == 50
    calculator.memory_subtract(10)
    calculator.memory_subtract()
    assert calculator.memory_recall() == -2
    assert calculator.evaluate("mem*2") == -4
    calculator.memory_clear()
    assert calculator.memory_recall() == 0


def test_memory_rejects_invalid_value():
    with pytest.raises(TypeError):
        ScientificCalculator().memory_add("5")


def test_history_is_capped():
    calculator = ScientificCalculator()
    for i in range(MAX_HISTORY + 5):
        calculator.evaluate(str(i))
    assert len(calculator.history_list) == MAX_HISTORY
    assert calculator.history_list[0] == ("5", 5.0)


def test_failed_evaluation_preserves_state():
    calculator = ScientificCalculator()
    calculator.evaluate("4")
    with pytest.raises(ZeroDivisionError):
        calculator.evaluate("1/0")
    assert calculator.ans == 4
    assert len(calculator.history_list) == 1


def test_angle_mode_switch():
    calculator = ScientificCalculator()
    assert calculator.evaluate("sin(90)") == pytest.approx(1)
    calculator.set_angle_mode("rad")
    assert calculator.evaluate("sin(pi/2)") == pytest.approx(1)
    with pytest.raises(ValueError):
        calculator.set_angle_mode("grad")
    with pytest.raises(ValueError):
        ScientificCalculator(angle_mode="grad")


# ---------------------------------------------------------------------------
# Command-line interface
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "value, expected",
    [(0.49999999999999994, "0.5"), (-0.0, "0"), (120.0, "120"), (1e20, "1e+20")],
)
def test_format_result(value, expected):
    assert format_result(value) == expected


@pytest.mark.parametrize(
    "line, expected",
    [("help", HELP_TEXT), ("history", "(empty)"), ("", ""), ("QUIT", None), ("exit", None)],
)
def test_handle_command_simple(line, expected):
    assert handle_command(ScientificCalculator(), line) == expected


def test_run_repl_session():
    line_iter = iter(
        ["mode rad", "sin(pi/2)", "m+", "m-", "m+", "mr", "1/0", "history", "mc", "quit"]
    )
    output_list = []
    run_repl(
        ScientificCalculator(),
        input_func=lambda _: next(line_iter),
        output_func=output_list.append,
    )
    assert "angle mode: rad" in output_list
    assert "1" in output_list
    assert "M = 0" in output_list
    assert "M = 1" in output_list
    assert "error: division by zero" in output_list
    assert "1: sin(pi/2) = 1" in output_list


def test_run_repl_ends_on_eof():
    def raise_eof(_):
        raise EOFError

    output_list = []
    run_repl(ScientificCalculator(), input_func=raise_eof, output_func=output_list.append)
    assert len(output_list) == 1


def test_main_one_shot(capsys):
    assert main(["--expr", "2*sin(30)+sqrt(16)"]) == 0
    assert capsys.readouterr().out.strip() == "5"


def test_main_radian_mode(capsys):
    assert main(["--expr", "cos(pi)", "--mode", "rad"]) == 0
    assert capsys.readouterr().out.strip() == "-1"


def test_main_error_exit_code(capsys):
    assert main(["--expr", "sqrt(-1)"]) == 1
    assert "error" in capsys.readouterr().err
