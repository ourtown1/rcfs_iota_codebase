from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .terms import App, Atom, Term, app, apps, atom, left_spine

S = atom("S")
K = atom("K")
I = atom("I")
Y = atom("Y")


def ski_size(term: Term) -> int:
    return term.node_count()


def is_comb(term: Term, name: str) -> bool:
    return isinstance(term, Atom) and term.name == name


def reduce_ski_once(term: Term) -> tuple[Term, str | None]:
    """One normal-order SKI/Y contraction.

    Returns (new_term, rule_name) or (term, None).
    Y is treated as a primitive fixed-point combinator: Y f -> f (Y f).
    """
    head, args = left_spine(term)

    if is_comb(head, "I") and len(args) >= 1:
        out = args[0]
        for a in args[1:]:
            out = app(out, a)
        return out, "I x -> x"

    if is_comb(head, "K") and len(args) >= 2:
        out = args[0]
        for a in args[2:]:
            out = app(out, a)
        return out, "K x y -> x"

    if is_comb(head, "S") and len(args) >= 3:
        x, y, z = args[0], args[1], args[2]
        out = apps(x, z, app(y, z))
        for a in args[3:]:
            out = app(out, a)
        return out, "S x y z -> x z (y z)"

    if is_comb(head, "Y") and len(args) >= 1:
        f = args[0]
        out = app(f, app(Y, f))
        for a in args[1:]:
            out = app(out, a)
        return out, "Y f -> f (Y f)"

    if isinstance(term, App):
        new_fn, rule = reduce_ski_once(term.fn)
        if rule:
            return app(new_fn, term.arg), rule
        new_arg, rule = reduce_ski_once(term.arg)
        if rule:
            return app(term.fn, new_arg), rule

    return term, None


def reduce_ski(term: Term, max_steps: int = 10_000) -> tuple[Term, list[str]]:
    cur = term
    trace: list[str] = []
    for _ in range(max_steps):
        nxt, rule = reduce_ski_once(cur)
        if rule is None:
            return cur, trace
        trace.append(rule)
        cur = nxt
    trace.append(f"HALT: max_steps={max_steps} reached")
    return cur, trace


def normalize_ski(term: Term, max_steps: int = 10_000) -> Term:
    return reduce_ski(term, max_steps=max_steps)[0]


def redex_count_ski(term: Term) -> int:
    count = 0
    for t in term.walk():
        _, rule = reduce_ski_once(t)
        if rule:
            count += 1
    return count
