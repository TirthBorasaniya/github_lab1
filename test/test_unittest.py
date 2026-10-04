"""
Unittest suite for the scientific calculator mirroring the core pytest checks.
Uses subTest for case tables and assertRaises for error paths.
"""

import io
import unittest
from contextlib import redirect_stdout

from src import base_conversion as base
from src import calculator as calc
from src import statistics_mode as stats
from src.expression import evaluate
from src.scientific_calculator import ScientificCalculator, main

EXPRESSION_CASE_LIST = [
    # (expression, angle_mode, expected)
    ('2+3', 'rad', 5.0),
    ('10-4', 'rad', 6.0),
    ('6*7', 'rad', 42.0),
    ('7/2', 'rad', 3.5),
    ('2^10', 'rad', 1024.0),
    ('2^3^2', 'rad', 512.0),
    ('-(3+4)*2', 'rad', -14.0),
    ('sqrt(144)', 'rad', 12.0),
    ('root(27,3)', 'rad', 3.0),
    ('root(-8,3)', 'rad', -2.0),
    ('log(1000)', 'rad', 3.0),
    ('log(8,2)', 'rad', 3.0),
    ('ln(e)', 'rad', 1.0),
    ('exp(0)', 'rad', 1.0),
    ('abs(-3.5)', 'rad', 3.5),
    ('sin(30)', 'deg', 0.5),
    ('cos(60)', 'deg', 0.5),
    ('tan(45)', 'deg', 1.0),
    ('sin(pi/2)', 'rad', 1.0),
    ('cos(pi)', 'rad', -1.0),
    ('asin(1)', 'deg', 90.0),
    ('atan(1)', 'deg', 45.0),
    ('fact(5)', 'rad', 120.0),
    ('nCr(5,2)', 'rad', 10.0),
    ('nPr(5,2)', 'rad', 20.0),
    ('2*sin(30)+sqrt(16)', 'deg', 5.0),
    ('fact(4)/nCr(4,2)', 'rad', 4.0),
]


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


class TestStatistics(unittest.TestCase):
    """Tests for statistics mode."""

    def test_values(self):
        spread_values = (2, 4, 4, 4, 5, 5, 7, 9)
        self.assertAlmostEqual(stats.mean(2, 4, 4, 5), 3.75)
        self.assertAlmostEqual(stats.median(4, 1, 3, 2), 2.5)
        self.assertEqual(stats.mode(1, 2, 2, 3), 2)
        self.assertAlmostEqual(stats.pstdev(*spread_values), 2)
        self.assertEqual(stats.value_range(1, 5, 3), 4)

    def test_errors(self):
        with self.assertRaises(ValueError):
            stats.mean()
        with self.assertRaises(ValueError):
            stats.variance(5)
        with self.assertRaises(TypeError):
            stats.mean(1, "2")


class TestBaseConversion(unittest.TestCase):
    """Tests for number base conversion."""

    def test_conversions(self):
        self.assertEqual(base.to_base(10, 2), "1010")
        self.assertEqual(base.from_base("0xFF", 16), 255)
        self.assertEqual(base.format_in_base(-10, "bin"), "-0b1010")

    def test_round_trip(self):
        for n in (0, 7, 255, -1000):
            for target_base in (2, 8, 16):
                with self.subTest(n=n, base=target_base):
                    self.assertEqual(base.from_base(base.to_base(n, target_base), target_base), n)

    def test_errors(self):
        with self.assertRaises(ValueError):
            base.from_base("102", 2)
        with self.assertRaises(ValueError):
            base.to_base(2.5, 2)


class TestExpression(unittest.TestCase):
    """Tests for the expression evaluator."""

    def test_cases(self):
        for expression, angle_mode, expected in EXPRESSION_CASE_LIST:
            with self.subTest(expression=expression):
                self.assertAlmostEqual(evaluate(expression, angle_mode=angle_mode), expected)

    def test_statistics_and_literals(self):
        self.assertAlmostEqual(evaluate("mean(2, 4, 4, 5)"), 3.75)
        self.assertEqual(evaluate("0b1010 + 0xff"), 265)

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

    def test_main_base_output(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = main(["--expr", "255", "--base", "hex"])
        self.assertEqual(exit_code, 0)
        self.assertEqual(buffer.getvalue().strip(), "0xff")


if __name__ == "__main__":
    unittest.main()
