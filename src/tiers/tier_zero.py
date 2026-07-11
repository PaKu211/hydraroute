"""
Tier 0 - Zero-cost local execution (v2 - improved).
Handles math problems using Python eval() and sympy.
No API calls = zero token cost.

Improvements:
- Better equation extraction regex (catches '2x + 10 = 30')
- More arithmetic patterns
- Percentage calculations
- Word problem fallback hints
"""

import logging
import re

logger = logging.getLogger("hydraroute")

# Allowed characters for safe eval: digits, operators, whitespace, parens, decimal
SAFE_EVAL_PATTERN = re.compile(r"^[\d\s\+\-\*/\.\(\)%]+$")


def execute(instruction: str) -> str | None:
    """Try to solve the task locally without an API call.

    Returns:
        Answer string if solved locally, None if fallback to API is needed.
    """
    text = instruction.strip()

    result = (
        _try_solve_equation(text)
        or _try_percentage(text)
        or _try_arithmetic(text)
    )

    if result is not None:
        logger.info("Tier 0 solved locally: %s", result[:50])
        return str(result)

    return None


def _try_arithmetic(text: str) -> str | None:
    """Try to extract and evaluate a simple arithmetic expression."""
    cleaned = text.lower()
    for prefix in [
        "what is", "what's", "calculate", "compute", "evaluate",
        "find the value of", "find", "how much is", "what does",
        "what do you get when you",
    ]:
        cleaned = cleaned.replace(prefix, "")

    cleaned = cleaned.strip().rstrip("?").strip()

    expr_match = re.search(r"([\d][\d\s\+\-\*/\.\(\)%]+[\d\)])", cleaned)
    if expr_match:
        expr = expr_match.group(1).strip()
        return _safe_eval(expr)

    if SAFE_EVAL_PATTERN.match(cleaned) and cleaned:
        return _safe_eval(cleaned)

    return None


def _try_percentage(text: str) -> str | None:
    """Handle percentage calculations like '15% of 200'."""
    match = re.search(
        r"(\d+(?:\.\d+)?)\s*%\s*(?:of)\s*(\d+(?:\.\d+)?)", text, re.IGNORECASE
    )
    if match:
        pct = float(match.group(1))
        base = float(match.group(2))
        result = (pct / 100.0) * base
        if result == int(result):
            return str(int(result))
        return str(result)
    return None


def _try_solve_equation(text: str) -> str | None:
    """Try to solve algebraic equations using sympy with AST parsing.

    Handles:
    - 'Solve for x: 2x + 10 = 30'
    - 'Solve 3x - 7 = 14'
    - 'If 2x + 5 = 15, what is x?'
    - 'A number times 3 equals 15'
    """
    try:
        import sympy
        from sympy.parsing.sympy_parser import (
            parse_expr,
            standard_transformations,
            implicit_multiplication_application,
        )
        TRANSFORMATIONS = standard_transformations + (implicit_multiplication_application,)
    except ImportError:
        logger.debug("sympy not available")
        return None

    lower = text.lower()

    # Must look like an equation problem
    has_solve_kw = any(kw in lower for kw in [
        "solve", "find x", "find y", "what is x", "what is y",
        "value of x", "value of y", "for x", "for y",
    ])
    has_equals = "=" in text and "==" not in text

    if not (has_solve_kw or has_equals):
        return None

    # Translate word problem keywords
    word_map = [
        (r"(?i)\ba number\b", "x"),
        (r"(?i)\btimes\b", "*"),
        (r"(?i)\bmultiplied by\b", "*"),
        (r"(?i)\bdivided by\b", "/"),
        (r"(?i)\bplus\b", "+"),
        (r"(?i)\bminus\b", "-"),
        (r"(?i)\bequals\b", "="),
        (r"(?i)\bis equal to\b", "="),
    ]
    translated = text
    for pattern, replacement in word_map:
        translated = re.sub(pattern, replacement, translated)

    equation_str = _extract_equation_v2(translated)
    if not equation_str:
        return None

    return _solve_with_sympy(equation_str, TRANSFORMATIONS)


def _extract_equation_v2(text: str) -> str | None:
    """Extract the equation string using multiple patterns.

    Returns the raw equation string like '2x + 10 = 30'.
    """
    # Pattern 1: "Solve for x: EQUATION" or "Solve EQUATION"
    m = re.search(
        r"(?:solve\s+(?:for\s+\w+\s*:?\s*)?|find\s+\w+\s*:?\s*)"  # prefix
        r"([^\?\.]+=[^\?\.]+)",  # equation
        text, re.IGNORECASE,
    )
    if m:
        return m.group(1).strip().rstrip("?., ")

    # Pattern 2: "If EQUATION, ..."
    m = re.search(r"if\s+([^\?,]+=[^\?,]+),", text, re.IGNORECASE)
    if m:
        return m.group(1).strip()

    # Pattern 3: bare equation anywhere "2x + 10 = 30"
    # Match: algebraic expression = algebraic expression
    m = re.search(
        r"((?:[\d]+\s*[\*]?\s*)?[a-zA-Z][\w\s\+\-\*/\.\(\)]*\s*=\s*[\d\w\s\+\-\*/\.\(\)]+)",
        text
    )
    if m:
        eq = m.group(1).strip().rstrip("?., ")
        # Must have a variable
        if re.search(r"[a-zA-Z]", eq):
            return eq

    return None


def _solve_with_sympy(equation_str: str, transformations=None) -> str | None:
    """Parse and solve an equation string using sympy AST parser."""
    try:
        import sympy
        from sympy.parsing.sympy_parser import (
            parse_expr, standard_transformations,
            implicit_multiplication_application,
        )
        if transformations is None:
            transformations = standard_transformations + (implicit_multiplication_application,)

        if "=" not in equation_str:
            return None

        parts = equation_str.split("=", 1)
        lhs_str = parts[0].strip()
        rhs_str = parts[1].strip()

        if not lhs_str or not rhs_str:
            return None

        # Safety: only allow algebraic-safe chars
        safe_pattern = re.compile(r"^[\d\s\+\-\*/\.\(\)a-zA-Z\^]+$")
        if not safe_pattern.match(lhs_str) or not safe_pattern.match(rhs_str):
            return None

        lhs = parse_expr(lhs_str, transformations=transformations)
        rhs = parse_expr(rhs_str, transformations=transformations)

        equation = sympy.Eq(lhs, rhs)
        free_vars = list(equation.free_symbols)

        if not free_vars:
            return None

        # Solve for first symbol found (usually x)
        # Prefer x over other variables
        var = next((v for v in free_vars if str(v) == "x"), free_vars[0])
        solutions = sympy.solve(equation, var)

        if not solutions:
            return None

        if isinstance(solutions, list):
            if len(solutions) == 1:
                sol = solutions[0]
                try:
                    val = int(sol)
                    return str(val)
                except (TypeError, ValueError):
                    return str(sol)
            return ", ".join(
                str(int(s)) if s.is_integer else str(s) for s in solutions
            )

        return str(solutions)

    except Exception as e:
        logger.debug("Sympy solve failed for '%s': %s", equation_str, e)
        return None


def _is_safe_algebra(expr: str) -> bool:
    """Check that expression only contains safe algebraic chars."""
    return bool(re.match(r"^[\d\s\+\-\*/\.\(\)a-zA-Z]+$", expr))


def _add_implicit_mult(expr: str) -> str:
    """Add implicit multiplication: '2x' -> '2*x', '3(y)' -> '3*(y)'."""
    expr = re.sub(r"(\d)([a-zA-Z])", r"\1*\2", expr)
    expr = re.sub(r"([a-zA-Z])(\d)", r"\1*\2", expr)
    expr = re.sub(r"\)(\()", r")*(", expr)
    expr = re.sub(r"\)([a-zA-Z])", r")*\1", expr)
    expr = re.sub(r"(\d)\(", r"\1*(", expr)
    return expr


def _safe_eval(expr: str) -> str | None:
    """Safely evaluate a pure arithmetic expression."""
    if not SAFE_EVAL_PATTERN.match(expr):
        return None
    if not expr or len(expr) > 200:
        return None
    try:
        code = compile(expr, "<math>", "eval")
        for name in code.co_names:
            return None  # No name lookups allowed
        result = eval(code, {"__builtins__": {}}, {})
        if isinstance(result, float):
            if result == int(result):
                return str(int(result))
            return f"{result:.10g}"
        return str(result)
    except Exception:
        return None
