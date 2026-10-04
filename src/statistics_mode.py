"""
Statistics mode for the scientific calculator.
Computes central tendency, dispersion, and range over a list of numeric values.
"""

import statistics
from collections import Counter

from src.calculator import validate_number

MIN_SAMPLE_SIZE = 2


def _validate_values(values, min_count: int = 1) -> list:
    """Return values as a list, raising if there are too few or any value is not a number."""
    if len(values) < min_count:
        raise ValueError(f"at least {min_count} value(s) required, got {len(values)}")
    for i, value in enumerate(values):
        validate_number(value, f"values[{i}]")
    return list(values)


def mean(*values: float) -> float:
    """Return the arithmetic mean."""
    return statistics.fmean(_validate_values(values))


def median(*values: float) -> float:
    """Return the median; the mean of the two middle values when the count is even."""
    return float(statistics.median(_validate_values(values)))


def mode(*values: float) -> float:
    """Return the most frequent value, choosing the smallest when several are tied."""
    count_dict = Counter(_validate_values(values))
    max_count = max(count_dict.values())
    return min(value for value, count in count_dict.items() if count == max_count)


def variance(*values: float) -> float:
    """Return the sample variance (n - 1 denominator); requires at least two values."""
    return statistics.variance(_validate_values(values, MIN_SAMPLE_SIZE))


def pvariance(*values: float) -> float:
    """Return the population variance (n denominator)."""
    return statistics.pvariance(_validate_values(values))


def stdev(*values: float) -> float:
    """Return the sample standard deviation; requires at least two values."""
    return statistics.stdev(_validate_values(values, MIN_SAMPLE_SIZE))


def pstdev(*values: float) -> float:
    """Return the population standard deviation."""
    return statistics.pstdev(_validate_values(values))


def minimum(*values: float) -> float:
    """Return the smallest value."""
    return min(_validate_values(values))


def maximum(*values: float) -> float:
    """Return the largest value."""
    return max(_validate_values(values))


def value_range(*values: float) -> float:
    """Return the difference between the largest and smallest values."""
    value_list = _validate_values(values)
    return max(value_list) - min(value_list)
