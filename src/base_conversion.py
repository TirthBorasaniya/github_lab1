"""
Number base conversion for the scientific calculator.
Converts integers between decimal and bases 2 to 36, with prefixed binary, octal, and hex output.
"""

from src.calculator import validate_integer

DIGITS = "0123456789abcdefghijklmnopqrstuvwxyz"
MIN_BASE = 2
MAX_BASE = 36
PREFIX_DICT = {2: "0b", 8: "0o", 16: "0x"}
BASE_NAME_DICT = {"bin": 2, "oct": 8, "dec": 10, "hex": 16}


def _validate_base(base) -> int:
    """Return base as int, raising if it is outside [MIN_BASE, MAX_BASE]."""
    base = validate_integer(base, "base")
    if not MIN_BASE <= base <= MAX_BASE:
        raise ValueError(f"base must be between {MIN_BASE} and {MAX_BASE}, got {base}")
    return base


def to_base(n: int, base: int) -> str:
    """
    Convert an integer to its digit string in the given base.

    Parameters
    ----------
    n : int
        Integer to convert. Integral floats such as 10.0 are accepted.
    base : int
        Target base in [2, 36]. Digits above 9 use lowercase letters.

    Returns
    -------
    digit_str : str
        Digits without prefix, with a leading "-" for negative values.
    """
    n = validate_integer(n, "n")
    base = _validate_base(base)
    if n == 0:
        return "0"

    digit_list = []
    remaining = abs(n)
    while remaining:
        remaining, digit = divmod(remaining, base)
        digit_list.append(DIGITS[digit])
    sign = "-" if n < 0 else ""
    return sign + "".join(reversed(digit_list))


def from_base(text: str, base: int) -> int:
    """
    Parse a digit string in the given base into an integer.

    Parameters
    ----------
    text : str
        Digits with an optional leading sign and an optional prefix matching the base
        (0b, 0o, or 0x). Letters are case-insensitive.
    base : int
        Source base in [2, 36].

    Returns
    -------
    n : int
        Parsed integer.
    """
    if not isinstance(text, str):
        raise TypeError(f"text must be a str, got {type(text).__name__}")
    base = _validate_base(base)

    digit_str = text.strip().lower()
    sign = -1 if digit_str.startswith("-") else 1
    digit_str = digit_str.lstrip("+-")
    prefix = PREFIX_DICT.get(base, "")
    if prefix and digit_str.startswith(prefix):
        digit_str = digit_str[len(prefix):]
    if not digit_str:
        raise ValueError(f"no digits in {text!r}")

    valid_digits = DIGITS[:base]
    n = 0
    for char in digit_str:
        if char not in valid_digits:
            raise ValueError(f"invalid digit {char!r} for base {base}")
        n = n * base + valid_digits.index(char)
    return sign * n


def format_in_base(value, base_name: str) -> str:
    """
    Format an integer value in a named base, using the standard prefix.

    Parameters
    ----------
    value : int or float
        Integral value to format, for example a calculator result.
    base_name : str
        One of "bin", "oct", "dec", or "hex".

    Returns
    -------
    formatted : str
        For example "0xff" for 255 in hex, or "-0b1010" for -10 in binary.
    """
    if base_name not in BASE_NAME_DICT:
        raise ValueError(f"base_name must be one of {tuple(BASE_NAME_DICT)}, got {base_name!r}")
    n = validate_integer(value, "value")
    base = BASE_NAME_DICT[base_name]
    sign = "-" if n < 0 else ""
    return f"{sign}{PREFIX_DICT.get(base, '')}{to_base(abs(n), base)}"
