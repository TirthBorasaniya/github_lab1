# GitHub Lab 1: Scientific Calculator with CI/CD
### Author: Tirth Borasaniya, IE-7374 MLOps

Based on `Labs/Github_Labs/Lab1` from the IE-7374 MLOps course repository. The original lab builds a four-function calculator, tests it with pytest and unittest, and runs those tests with GitHub Actions. This version keeps that purpose and structure and extends the calculator into a scientific calculator, with a larger test suite and an expanded CI/CD pipeline.

## Modifications

### 1. Scientific function library (`src/calculator.py`)
The original `fun1` to `fun4` are kept with the same behavior. New functions added:

| Category | Functions |
| --- | --- |
| Arithmetic | `divide`, `power`, `absolute` |
| Roots and logarithms | `sqrt`, `nth_root` (real odd roots of negatives), `log` (any base, default 10), `ln`, `exp` |
| Trigonometry | `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, each supporting degree or radian mode |
| Combinatorics | `factorial`, `n_choose_r` (nCr), `n_permute_r` (nPr) |

Every function validates its input: non-numbers raise `TypeError` (including `bool`, which Python treats as an int), and mathematically undefined inputs raise `ValueError` or `ZeroDivisionError`, such as `sqrt(-1)`, `log(0)`, `tan(90)` in degrees, or `1/0`. Floating-point residue is snapped to zero so `sin(180)` in degrees returns exactly `0`.

### 2. Safe expression evaluator (`src/expression.py`)
Like a physical scientific calculator, the program evaluates full expressions such as `2*sin(30) + sqrt(16)`. Supported syntax: `+ - * / ^` with standard precedence (`^` is right-associative), parentheses, unary minus, the constants `pi` and `e`, and all functions above.

The parser walks Python's abstract syntax tree and allows only whitelisted node types. It never calls `eval`, so input such as `__import__('os').system(...)` is rejected rather than executed.

### 3. Calculator state and command-line interface (`src/scientific_calculator.py`)
A `ScientificCalculator` class adds features found on scientific calculators: degree/radian mode, `ans` (previous result), a memory register (`M+`, `M-`, `MR`, `MC`, referenced in expressions as `mem`), and a capped history. Failed evaluations leave state unchanged.

```bash
python -m src.scientific_calculator --expr "2*sin(30) + sqrt(16)"    # prints 5
python -m src.scientific_calculator --mode rad                       # interactive session
```

Interactive session example:
```
> mode rad
angle mode: rad
> sin(pi/2)
1
> m+
M = 1
> ans*3 + mem
4
> history
1: sin(pi/2) = 1
2: ans*3 + mem = 4
```

### 4. Data-driven tests (`data/test_cases.csv`)
The original `data/` folder is empty. It now holds 27 expressions with their angle mode and expected result. Both test suites load this file, so new cases can be added without writing code.

### 5. Expanded tests
| | Original lab | This repository |
| --- | --- | --- |
| Pytest | 4 tests | 147 cases: parametrized values, error checks with `pytest.raises`, CSV-driven cases, rejection of unsafe expressions, state and CLI tests |
| Unittest | 4 tests | 12 tests using `subTest`, `assertRaises`, and CSV-driven cases |
| Line coverage | Not measured | About 99 percent |

### 6. CI/CD pipeline
| | Original lab | This repository |
| --- | --- | --- |
| Workflow location | `workflows/` (not detected by GitHub) | `.github/workflows/` |
| Actions versions | `@v2` (deprecated) | `checkout@v4`, `setup-python@v5`, `upload-artifact@v4` |
| Python versions | 3.8 only | Matrix of 3.10, 3.11, 3.12 |
| Operating systems | Ubuntu | Unittests on Ubuntu, Windows, and macOS |
| Triggers | Push to main | Push, pull request to main, manual run |
| Quality gates | Tests only | flake8 lint, 90 percent coverage minimum, CLI smoke test |
| Reporting | JUnit XML artifact | JUnit XML artifact per Python version, job summary |

## Project structure

```
.
├── .github/workflows/
│   ├── pytest_action.yml      # lint, pytest, coverage gate, CLI smoke test
│   └── unittest_action.yml    # unittest on three operating systems
├── data/
│   ├── __init__.py
│   └── test_cases.csv
├── src/
│   ├── __init__.py
│   ├── calculator.py
│   ├── expression.py
│   └── scientific_calculator.py
├── test/
│   ├── __init__.py
│   ├── test_pytest.py
│   └── test_unittest.py
├── pytest.ini
├── requirements.txt
└── .gitignore
```

## Setup and running

Run all commands from the repository root.

```bash
python -m venv github_lab1_env
source github_lab1_env/bin/activate      # Windows: github_lab1_env\Scripts\activate
pip install -r requirements.txt

pytest                                                        # pytest suite
pytest --cov=src --cov-report=term-missing                    # with coverage
python -m unittest discover -s test -t . -p "test_unittest.py" -v
flake8 src test --max-line-length 100                         # lint
```
