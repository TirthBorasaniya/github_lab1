"""
Stateful scientific calculator with angle mode, answer recall, a memory register, and history.
Provides a command-line interface for one-shot evaluation and interactive sessions.
"""

import argparse
import sys

from src import calculator as calc
from src.expression import evaluate

DEFAULT_ANGLE_MODE = "deg"
MAX_HISTORY = 50
RESULT_PRECISION = 12
EXIT_COMMANDS = ("quit", "exit")
CALCULATOR_ERRORS = (ValueError, TypeError, ZeroDivisionError, OverflowError)
HELP_TEXT = (
    "commands: mode deg | mode rad | m+ | m- | mr | mc | history | help | quit\n"
    "operators: + - * / ^ ( )   constants: pi e ans mem\n"
    "functions: sin cos tan asin acos atan sqrt root log ln exp abs fact nCr nPr"
)


def format_result(value: float) -> str:
    """Format a result to RESULT_PRECISION significant digits, removing floating-point residue."""
    # adding 0.0 converts negative zero to positive zero
    return f"{value + 0.0:.{RESULT_PRECISION}g}"


class ScientificCalculator:
    """Scientific calculator holding angle mode, last answer, memory register, and history."""

    def __init__(self, angle_mode=DEFAULT_ANGLE_MODE):
        calc.validate_angle_mode(angle_mode)
        self.angle_mode = angle_mode
        self.ans = 0.0
        self.memory = 0.0
        self.history_list = []

    def set_angle_mode(self, angle_mode):
        """Switch between "deg" and "rad"."""
        calc.validate_angle_mode(angle_mode)
        self.angle_mode = angle_mode

    def evaluate(self, expression):
        """
        Evaluate an expression and record it in history.

        State is updated only on success, so a failed evaluation leaves ans and history unchanged.

        Parameters
        ----------
        expression : str
            Calculator expression; may reference ans and mem.

        Returns
        -------
        result : float
            Evaluated result, also stored as ans.
        """
        result = evaluate(
            expression, angle_mode=self.angle_mode, ans=self.ans, memory=self.memory
        )
        self.ans = result
        self.history_list.append((expression, result))
        del self.history_list[:-MAX_HISTORY]
        return result

    def memory_add(self, value=None):
        """Add value, or ans when value is None, to the memory register (M+)."""
        self.memory += self.ans if value is None else calc.validate_number(value, "value")

    def memory_subtract(self, value=None):
        """Subtract value, or ans when value is None, from the memory register (M-)."""
        self.memory -= self.ans if value is None else calc.validate_number(value, "value")

    def memory_recall(self):
        """Return the memory register (MR)."""
        return self.memory

    def memory_clear(self):
        """Reset the memory register to zero (MC)."""
        self.memory = 0.0

    def clear_history(self):
        """Remove all history entries."""
        self.history_list = []


# ---------------------------------------------------------------------------
# Command-line interface
# ---------------------------------------------------------------------------

def _format_history(calculator):
    """Return history entries as numbered lines."""
    if not calculator.history_list:
        return "(empty)"
    return "\n".join(
        f"{i}: {expression} = {format_result(result)}"
        for i, (expression, result) in enumerate(calculator.history_list, start=1)
    )


def handle_command(calculator, line):
    """
    Execute one line of interactive input.

    Parameters
    ----------
    calculator : ScientificCalculator
        Calculator instance to operate on.
    line : str
        Raw input line: a command or an expression.

    Returns
    -------
    output : str or None
        Text to display, an empty string for no output, or None to end the session.
    """
    command = line.strip()
    lowered = command.lower()

    if lowered in EXIT_COMMANDS:
        return None
    if not command:
        return ""
    if lowered == "help":
        return HELP_TEXT
    if lowered.startswith("mode "):
        calculator.set_angle_mode(lowered.split(maxsplit=1)[1])
        return f"angle mode: {calculator.angle_mode}"
    if lowered == "m+":
        calculator.memory_add()
        return f"M = {format_result(calculator.memory)}"
    if lowered == "m-":
        calculator.memory_subtract()
        return f"M = {format_result(calculator.memory)}"
    if lowered == "mr":
        return f"M = {format_result(calculator.memory_recall())}"
    if lowered == "mc":
        calculator.memory_clear()
        return "M = 0"
    if lowered == "history":
        return _format_history(calculator)
    return format_result(calculator.evaluate(command))


def run_repl(calculator, input_func=input, output_func=print):
    """
    Run an interactive session until a quit command or end of input.

    Parameters
    ----------
    calculator : ScientificCalculator
        Calculator instance to operate on.
    input_func : callable
        Function that takes a prompt and returns one input line.
    output_func : callable
        Function that displays one output string.
    """
    output_func(f"Scientific calculator ({calculator.angle_mode} mode). Type 'help' for commands.")
    while True:
        try:
            line = input_func("> ")
        except EOFError:
            break
        try:
            output = handle_command(calculator, line)
        except CALCULATOR_ERRORS as err:
            output = f"error: {err}"
        if output is None:
            break
        if output:
            output_func(output)


def main(argv=None):
    """
    Entry point for the command-line interface.

    Usage:
        python -m src.scientific_calculator --expr "2*sin(30) + sqrt(16)"
        python -m src.scientific_calculator --mode rad

    Parameters
    ----------
    argv : list of str or None
        Command-line arguments; defaults to sys.argv[1:].

    Returns
    -------
    exit_code : int
        0 on success, 1 if the expression could not be evaluated.
    """
    parser = argparse.ArgumentParser(description="Scientific calculator")
    parser.add_argument("--expr", help="evaluate one expression and exit")
    parser.add_argument("--mode", choices=calc.ANGLE_MODES, default=DEFAULT_ANGLE_MODE)
    args = parser.parse_args(argv)

    calculator = ScientificCalculator(angle_mode=args.mode)
    if args.expr is None:
        run_repl(calculator)
        return 0

    try:
        print(format_result(calculator.evaluate(args.expr)))
    except CALCULATOR_ERRORS as err:
        print(f"error: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
