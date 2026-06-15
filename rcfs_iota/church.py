from __future__ import annotations

from .lambda_calc import LTerm, church_lambda, lambda_to_ski
from .terms import Term
from .iota import expand_ski_to_iota


def church_numeral(n: int) -> LTerm:
    return church_lambda(n)


def church_ski(n: int) -> Term:
    return lambda_to_ski(church_lambda(n))


def church_iota(n: int) -> Term:
    return expand_ski_to_iota(church_ski(n))
