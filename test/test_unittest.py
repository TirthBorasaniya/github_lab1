"""
Unittest suite for the scientific calculator mirroring the core pytest checks.
Uses subTest for case tables and assertRaises for error paths.
"""

import csv
import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from src import calculator as calc
from src.expression import evaluate
from src.scientific_calculator import ScientificCalculator, main

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "test_cases.csv"


class TestOriginalFunctions(unittest.TestCase):
    """Tests for the original lab functions fun1 to fun4."""

    def test_fun1(self):
        self.assertEqual(calc.fun1(2, 3), 5)
        self.assertEqual(calc.fun1(-1, -1), -2)

    def test_fun2(self):
        self.assertEqual(calc.fun2(2, 3), -1)
        self.assertEqual(calc.fun2(-1, -1), 0)

    def test_fun3(self):
        self.assertEqual(calc.fun3(2, 3), 6)
        self.assertEqual(calc.fun3(-1, -1), 1)

    def test_fun4(self):
        self.assertEqual(calc.fun4(2, 3), 10)
        self.assertEqual(calc.fun4(-1, -1), -1)

    def test_type_errors(self):
        for func in (calc.fun1, calc.fun2, calc.fun3, calc.fun4):
            with self.subTest(func=func.__name__):
                with self.assertRaises(TypeError):
                    func("2", 3)


class TestScientificFunctions(unittest.TestCase):
    """Tests for scientific functions and their error handling."""

    def test_values(self):
        case_list = [
            (calc.power, (2, 10), 1024),
            (calc.sqrt, (144,), 12),
            (calc.nth_root, (-8, 3), -2),
            (calc.log, (1000,), 3),
            (calc.factorial, (5,), 120),
            (calc.n_choose_r, (5, 2), 10),
        ]
        for func, args, expected in case_list:
            with self.subTest(func=func.__name__, args=args):
                self.assertAlmostEqual(func(*args), expected)

    def test_trigonometry_degrees(self):
        self.assertAlmostEqual(calc.sin(30, "deg"), 0.5)
        self.assertEqual(calc.cos(90, "deg"), 0.0)
        self.assertAlmostEqual(calc.asin(1, "deg"), 90)

    def test_errors(self):
        case_list = [
            (calc.divide, (1, 0), ZeroDivisionError),
            (calc.sqrt, (-1,), ValueError),
            (calc.log, (0,), ValueError),
            (calc.tan, (90, "deg"), ValueError),
            (calc.factorial, (2.5,), ValueError),
        ]
        for func, args, exc in case_list:
            with self.subTest(func=func.__name__, args=args):
                with self.assertRaises(exc):
                    func(*args)


class TestExpression(unittest.TestCase):
    """Tests for the expression evaluator, including CSV-driven cases."""

    def test_csv_cases(self):
        with open(DATA_PATH, newline="") as f:
            row_list = list(csv.DictReader(f))
        self.assertGreater(len(row_list), 0)
        for row in row_list:
            with self.subTest(expression=row["expression"]):
                self.assertAlmostEqual(
                    evaluate(row["expression"], angle_mode=row["angle_mode"]),
                    float(row["expected"]),
                )

    def test_rejects_unsafe_input(self):
        for expression in ("__import__('os')", "open('x')", "x+1", "[1, 2]"):
            with self.subTest(expression=expression):
                with self.assertRaises(ValueError):
                    evaluate(expression)


class TestScientificCalculator(unittest.TestCase):
    """Tests for calculator state and the command-line entry point."""

    def test_ans_memory_history(self):
        calculator = ScientificCalculator()
        calculator.evaluate("2+3")
        calculator.memory_add()
        self.assertEqual(calculator.evaluate("ans*mem"), 25)
        self.assertEqual(len(calculator.history_list), 2)

    def test_main_one_shot(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = main(["--expr", "2*sin(30)+sqrt(16)"])
        self.assertEqual(exit_code, 0)
        self.assertEqual(buffer.getvalue().strip(), "5")


if __name__ == "__main__":
    unittest.main()
