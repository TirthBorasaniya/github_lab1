"""
Arithmetic and scientific calculator functions with strict input validation.
Retains the original lab functions fun1 to fun4 and adds roots, logarithms, trigonometry,
and combinatorics.
"""

import math

ANGLE_MODES = ("rad", "deg")
DEFAULT_ANGLE_MODE = "rad"
ZERO_TOLERANCE = 1e-12
MAX_FACTORIAL_INPUT = 170


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def validate_number(value, name: str) -> float:
    """Return value unchanged, raising TypeError or ValueError if it is not a real number."""
    # bool is a subclass of int and must be rejected explicitly
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number, got {type(value).__name__}")
    if math.isnan(value):
        raise ValueError(f"{name} must not be NaN")
    return value


def validate_integer(value, name: str) -> int:
    """Return value as int, accepting integral floats and rejecting fractional values."""
    validate_number(value, name)
    if isinstance(value, float):
        if not value.is_integer():
            raise ValueError(f"{name} must be an integer, got {value}")
        value = int(value)
    return value


def validate_angle_mode(angle_mode: str) -> None:
    """Raise ValueError if angle_mode is not one of ANGLE_MODES."""
    if angle_mode not in ANGLE_MODES:
        raise ValueError(f"angle_mode must be one of {ANGLE_MODES}, got {angle_mode!r}")


def _snap_to_zero(value: float) -> float:
    """Replace floating-point residue near zero with exact zero."""
    return 0.0 if abs(value) < ZERO_TOLERANCE else value


def _to_radians(x: float, angle_mode: str) -> float:
    """Convert an angle to radians according to angle_mode."""
    validate_number(x, "x")
    validate_angle_mode(angle_mode)
    return math.radians(x) if angle_mode == "deg" else x


def _from_radians(x: float, angle_mode: str) -> float:
    """Convert an angle in radians to the unit given by angle_mode."""
    validate_angle_mode(angle_mode)
    return math.degrees(x) if angle_mode == "deg" else x


# ---------------------------------------------------------------------------
# Original lab functions
# ---------------------------------------------------------------------------

def fun1(x: float, y: float) -> float:
    """Return the sum of x and y."""
    validate_number(x, "x")
    validate_number(y, "y")
    return x + y


def fun2(x: float, y: float) -> float:
    """Return x minus y."""
    validate_number(x, "x")
    validate_number(y, "y")
    return x - y


def fun3(x: float, y: float) -> float:
    """Return the product of x and y."""
    validate_number(x, "x")
    validate_number(y, "y")
    return x * y


def fun4(x: float, y: float) -> float:
    """Return the sum of fun1, fun2, and fun3 applied to x and y."""
    return fun1(x, y) + fun2(x, y) + fun3(x, y)


# ---------------------------------------------------------------------------
# Powers, roots, and logarithms
# ---------------------------------------------------------------------------

def divide(x: float, y: float) -> float:
    """Return x divided by y, raising ZeroDivisionError when y is zero."""
    validate_number(x, "x")
    validate_number(y, "y")
    if y == 0:
        raise ZeroDivisionError("division by zero")
    return x / y


def power(base: float, exponent: float) -> float:
    """
    Raise base to exponent using floating-point arithmetic.

    Parameters
    ----------
    base : float
        Base value.
    exponent : float
        Exponent value.

    Returns
    -------
    result : float
        base ** exponent. Raises OverflowError if the result exceeds float range.
    """
    validate_number(base, "base")
    validate_number(exponent, "exponent")
    if base == 0 and exponent < 0:
        raise ZeroDivisionError("zero cannot be raised to a negative power")
    if base < 0 and not float(exponent).is_integer():
        raise ValueError("negative base with non-integer exponent has no real result")
    # float conversion bounds runtime; integer pow on huge exponents would not terminate quickly
    return float(base) ** float(exponent)


def sqrt(x: float) -> float:
    """Return the square root of a non-negative number."""
    validate_number(x, "x")
    if x < 0:
        raise ValueError("square root of a negative number has no real result")
    return math.sqrt(x)


def nth_root(x: float, n: int) -> float:
    """
    Return the real n-th root of x.

    Parameters
    ----------
    x : float
        Radicand. May be negative when n is odd.
    n : int
        Root degree. Must be a non-zero integer.

    Returns
    -------
    root : float
        Real value r such that r ** n equals x.
    """
    validate_number(x, "x")
    n = validate_integer(n, "n")
    if n == 0:
        raise ValueError("root degree must be non-zero")
    if x >= 0:
        return x ** (1 / n)
    if n % 2 == 0:
        raise ValueError("even root of a negative number has no real result")
    return -(abs(x) ** (1 / n))


def log(x: float, base: float = 10) -> float:
    """Return the logarithm of x in the given base, defaulting to base 10."""
    validate_number(x, "x")
    validate_number(base, "base")
    if x <= 0:
        raise ValueError("logarithm is defined only for positive numbers")
    if base <= 0 or base == 1:
        raise ValueError("logarithm base must be positive and not equal to 1")
    # dedicated functions avoid rounding error, e.g. math.log(1000, 10) returns 2.9999999999999996
    if base == 10:
        return math.log10(x)
    if base == 2:
        return math.log2(x)
    return math.log(x, base)


def ln(x: float) -> float:
    """Return the natural logarithm of x."""
    return log(x, math.e)


def exp(x: float) -> float:
    """Return e raised to x. Raises OverflowError if the result exceeds float range."""
    validate_number(x, "x")
    return math.exp(x)


def absolute(x: float) -> float:
    """Return the absolute value of x."""
    validate_number(x, "x")
    return abs(x)


# ---------------------------------------------------------------------------
# Trigonometry
# ---------------------------------------------------------------------------

def sin(x: float, angle_mode: str = DEFAULT_ANGLE_MODE) -> float:
    """Return the sine of x, interpreted in the given angle mode."""
    return _snap_to_zero(math.sin(_to_radians(x, angle_mode)))


def cos(x: float, angle_mode: str = DEFAULT_ANGLE_MODE) -> float:
    """Return the cosine of x, interpreted in the given angle mode."""
    return _snap_to_zero(math.cos(_to_radians(x, angle_mode)))


def tan(x: float, angle_mode: str = DEFAULT_ANGLE_MODE) -> float:
    """Return the tangent of x, raising ValueError where tangent is undefined."""
    radians = _to_radians(x, angle_mode)
    if abs(math.cos(radians)) < ZERO_TOLERANCE:
        raise ValueError(f"tangent is undefined at {x} {angle_mode}")
    return _snap_to_zero(math.tan(radians))


def asin(x: float, angle_mode: str = DEFAULT_ANGLE_MODE) -> float:
    """Return the arcsine of x in the given angle mode."""
    validate_number(x, "x")
    if not -1 <= x <= 1:
        raise ValueError("arcsine is defined only on [-1, 1]")
    return _from_radians(math.asin(x), angle_mode)


def acos(x: float, angle_mode: str = DEFAULT_ANGLE_MODE) -> float:
    """Return the arccosine of x in the given angle mode."""
    validate_number(x, "x")
    if not -1 <= x <= 1:
        raise ValueError("arccosine is defined only on [-1, 1]")
    return _from_radians(math.acos(x), angle_mode)


def atan(x: float, angle_mode: str = DEFAULT_ANGLE_MODE) -> float:
    """Return the arctangent of x in the given angle mode."""
    validate_number(x, "x")
    return _from_radians(math.atan(x), angle_mode)


# ---------------------------------------------------------------------------
# Combinatorics
# ---------------------------------------------------------------------------

def factorial(n: int) -> int:
    """Return n factorial for an integer n in [0, MAX_FACTORIAL_INPUT]."""
    n = validate_integer(n, "n")
    if n < 0:
        raise ValueError("factorial is defined only for non-negative integers")
    if n > MAX_FACTORIAL_INPUT:
        raise ValueError(f"factorial input must not exceed {MAX_FACTORIAL_INPUT}")
    return math.factorial(n)


def _validate_n_r(n: int, r: int) -> tuple[int, int]:
    """Validate and return n and r as integers satisfying 0 <= r <= n."""
    n = validate_integer(n, "n")
    r = validate_integer(r, "r")
    if n < 0 or r < 0:
        raise ValueError("n and r must be non-negative")
    if r > n:
        raise ValueError(f"r ({r}) must not exceed n ({n})")
    return n, r


def n_choose_r(n: int, r: int) -> int:
    """Return the number of combinations of r items chosen from n."""
    return math.comb(*_validate_n_r(n, r))


def n_permute_r(n: int, r: int) -> int:
    """Return the number of ordered arrangements of r items chosen from n."""
    return math.perm(*_validate_n_r(n, r))
