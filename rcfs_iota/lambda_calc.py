from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .terms import App, Atom, Term, app, apps, atom
from .ski import S, K, I


class LTerm:
    pass


@dataclass(frozen=True, slots=True)
class Var(LTerm):
    name: str

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True, slots=True)
class Lam(LTerm):
    var: str
    body: LTerm

    def __str__(self) -> str:
        return f"(λ{self.var}.{self.body})"


@dataclass(frozen=True, slots=True)
class LApp(LTerm):
    fn: LTerm
    arg: LTerm

    def __str__(self) -> str:
        return f"({self.fn} {self.arg})"


def lapps(head: LTerm, *args: LTerm) -> LTerm:
    out = head
    for arg in args:
        out = LApp(out, arg)
    return out


def free_vars_lam(term: LTerm) -> set[str]:
    if isinstance(term, Var):
        return {term.name}
    if isinstance(term, Lam):
        return free_vars_lam(term.body) - {term.var}
    if isinstance(term, LApp):
        return free_vars_lam(term.fn) | free_vars_lam(term.arg)
    raise TypeError(type(term))


def free_vars_ski(term: Term) -> set[str]:
    if isinstance(term, Atom):
        if term.name in {"S", "K", "I", "Y", "ι"}:
            return set()
        return {term.name}
    if isinstance(term, App):
        return free_vars_ski(term.fn) | free_vars_ski(term.arg)
    raise TypeError(type(term))


def lambda_to_ski(term: LTerm) -> Term:
    """Translate lambda syntax into a mixed SKI term by bracket abstraction.

    This is intentionally close to the classical MicroHs-style path:
    parse λ-term → eliminate abstraction → closed SKI DAG/tree.
    """
    if isinstance(term, Var):
        return atom(term.name)
    if isinstance(term, LApp):
        return app(lambda_to_ski(term.fn), lambda_to_ski(term.arg))
    if isinstance(term, Lam):
        return abstract(term.var, lambda_to_ski(term.body))
    raise TypeError(type(term))


def abstract(var: str, body: Term) -> Term:
    """Classical bracket abstraction [var].body.

    Rules:
      [x] x     = I
      [x] M     = K M                 when x not free in M
      [x] M N   = S ([x] M) ([x] N)
    """
    if isinstance(body, Atom) and body.name == var:
        return I
    if var not in free_vars_ski(body):
        return app(K, body)
    if isinstance(body, App):
        return apps(S, abstract(var, body.fn), abstract(var, body.arg))
    # Remaining case is a free variable different from var; handled by K.
    return app(K, body)


def bracket_abstract(term: LTerm) -> Term:
    return lambda_to_ski(term)


def church_lambda(n: int) -> LTerm:
    if n < 0:
        raise ValueError("Church numerals require n >= 0")
    f = Var("f")
    x: LTerm = Var("x")
    body = x
    for _ in range(n):
        body = LApp(f, body)
    return Lam("f", Lam("x", body))
