# GitHub Lab 1: Scientific Calculator

Author: Tirth Borasaniya, IE-7374 MLOps

Based on `Labs/Github_Labs/Lab1` from the IE-7374 MLOps course repository. The original lab builds a four-function calculator (`fun1` to `fun4`), tests it with pytest and unittest, and runs those tests with GitHub Actions. This version keeps that purpose and structure and extends the calculator into a scientific calculator.

## Modifications

### 1. Scientific functions (`src/calculator.py`)
The original `fun1` to `fun4` are kept with the same behavior. Added:

| Category | Functions |
| --- | --- |
| Arithmetic | `divide`, `power`, `absolute` |
| Roots and logarithms | `sqrt`, `nth_root` (real odd roots of negatives), `log` (any base, default 10), `ln`, `exp` |
| Trigonometry | `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, each in degree or radian mode |
| Combinatorics | `factorial`, `n_choose_r` (nCr), `n_permute_r` (nPr) |

All functions validate input: non-numbers raise `TypeError`, and undefined operations such as `sqrt(-1)`, `log(0)`, `tan(90)` in degrees, or `1/0` raise `ValueError` or `ZeroDivisionError`. Floating-point residue is snapped to zero, so `sin(180)` in degrees returns exactly `0`.

### 2. Expression evaluator (`src/expression.py`)
Full expressions can be entered, as on a physical scientific calculator:

```
2*sin(30) + sqrt(16)        -> 5
-(3 + 4) * 2                -> -14
2^3^2                       -> 512
```

Supported: `+ - * / ^` with standard precedence, parentheses, unary minus, the constants `pi` and `e`, and every function in this README. The evaluator walks Python's abstract syntax tree and allows only whitelisted operations. It never calls `eval`, so input such as `__import__('os').system(...)` is rejected rather than executed.

### 3. Calculator features and command-line interface (`src/scientific_calculator.py`)
A `ScientificCalculator` class adds standard calculator features:
- Degree and radian mode
- `ans`, the previous result, usable in the next expression
- Memory register: `M+`, `M-`, `MR`, `MC`, referenced in expressions as `mem`
- History of recent calculations

A failed calculation leaves the calculator's state unchanged.

### 4. Statistics mode (`src/statistics_mode.py`)
Statistics over any number of values:

| Function | Result |
| --- | --- |
| `mean`, `median`, `mode` | Central tendency; `mode` returns the smallest value when several are tied |
| `var`, `std` | Sample variance and standard deviation (n - 1) |
| `pvar`, `pstd` | Population variance and standard deviation (n) |
| `min`, `max`, `range` | Extremes and spread |

```
mean(2, 4, 4, 5)                -> 3.75
pstd(2, 4, 4, 4, 5, 5, 7, 9)    -> 2
range(1, 5, 3) * 2              -> 8
```

### 5. Number base conversion (`src/base_conversion.py`)
Integer conversion between decimal and bases 2 to 36, with standard prefixes for binary, octal, and hexadecimal:
- **Output:** `hex 255` gives `0xff`; `bin` alone converts the previous result
- **Input:** binary, octal, and hex values can be typed directly into expressions, such as `0b1010 + 0xff` giving `265`
- **Functions:** `to_base(n, base)`, `from_base(text, base)`, and `format_in_base(value, name)`

## Usage

Run from the repository root.

```bash
python -m src.scientific_calculator --expr "2*sin(30) + sqrt(16)"    # prints 5
python -m src.scientific_calculator --expr "255" --base hex          # prints 0xff
python -m src.scientific_calculator --mode rad                       # interactive session
```

Interactive session example:
```
> sin(90)
1
> m+
M = 1
> mean(2, 4, 4, 5) + mem
4.75
> hex 255
0xff
> history
1: sin(90) = 1
2: mean(2, 4, 4, 5) + mem = 4.75
3: 255 = 255
```

Type `help` in a session for the full list of commands.

## Lab requirements, extended

### Tests
| | Original lab | This repository |
| --- | --- | --- |
| Pytest | 4 tests | Over 230 cases: parametrized values, error checks with `pytest.raises`, base conversion round trips, rejection of unsafe expressions, state and CLI tests |
| Unittest | 4 tests | 19 tests using `subTest` and `assertRaises` |
| Line coverage | Not measured | About 99 percent |

Running `pytest` also collects the unittest tests, so it reports the combined total.

### Continuous integration
| | Original lab | This repository |
| --- | --- | --- |
| Workflow location | `workflows/` (not detected by GitHub) | `.github/workflows/` |
| Actions versions | `@v2` (deprecated) | `checkout@v4`, `setup-python@v5`, `upload-artifact@v4` |
| Python versions | 3.8 only | 3.10, 3.11, and 3.12 |
| Operating systems | Ubuntu | Unittests on Ubuntu, Windows, and macOS |
| Triggers | Push to main | Push, pull request to main, manual run |
| Quality checks | Tests only | flake8 lint, 90 percent coverage minimum, CLI smoke test |
| Reporting | JUnit XML artifact | JUnit XML artifact per Python version, job summary |
| Notifications | Success and failure messages | Kept in both workflows |

## Project structure

```
.
├── .github/workflows/
│   ├── pytest_action.yml      # lint, pytest, coverage check, CLI smoke test
│   └── unittest_action.yml    # unittest on three operating systems
├── data/
│   └── __init__.py
├── src/
│   ├── __init__.py
│   ├── calculator.py
│   ├── expression.py
│   ├── scientific_calculator.py
│   ├── statistics_mode.py
│   └── base_conversion.py
├── test/
│   ├── __init__.py
│   ├── test_pytest.py
│   └── test_unittest.py
├── pytest.ini
├── requirements.txt
└── .gitignore
```

## Setup

```bash
python -m venv github_lab1_env
source github_lab1_env/bin/activate      # Windows: github_lab1_env\Scripts\activate
pip install -r requirements.txt

pytest
python -m unittest discover -s test -t . -p "test_unittest.py" -v
flake8 src test --max-line-length 100
```
