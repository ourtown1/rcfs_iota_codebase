from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, Union


class Term:
    """Base class for first-order applicative terms."""

    def children(self) -> tuple[Term, ...]:
        return ()

    def walk(self) -> Iterator[Term]:
        yield self
        for child in self.children():
            yield from child.walk()

    def node_count(self) -> int:
        return sum(1 for _ in self.walk())

    def depth(self) -> int:
        kids = self.children()
        if not kids:
            return 1
        return 1 + max(k.depth() for k in kids)


@dataclass(frozen=True, slots=True)
class Atom(Term):
    name: str

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name


@dataclass(frozen=True, slots=True)
class App(Term):
    fn: Term
    arg: Term

    def children(self) -> tuple[Term, Term]:
        return (self.fn, self.arg)

    def __str__(self) -> str:
        return f"({self.fn} {self.arg})"

    def __repr__(self) -> str:
        return str(self)


def atom(name: str) -> Atom:
    return Atom(name)


def app(fn: Term, arg: Term) -> App:
    return App(fn, arg)


def apps(head: Term, *args: Term) -> Term:
    out = head
    for arg in args:
        out = App(out, arg)
    return out


def left_spine(term: Term) -> tuple[Term, list[Term]]:
    """Return head and left-associated args for (((h a) b) c)."""
    args: list[Term] = []
    cur = term
    while isinstance(cur, App):
        args.append(cur.arg)
        cur = cur.fn
    args.reverse()
    return cur, args


def pretty(term: Term, max_chars: int = 240) -> str:
    s = str(term)
    if len(s) <= max_chars:
        return s
    return s[: max_chars - 3] + "..."


def replace_atoms(term: Term, mapping: dict[str, Term]) -> Term:
    if isinstance(term, Atom):
        return mapping.get(term.name, term)
    if isinstance(term, App):
        return App(replace_atoms(term.fn, mapping), replace_atoms(term.arg, mapping))
    raise TypeError(type(term))


def count_atom(term: Term, name: str) -> int:
    return sum(1 for t in term.walk() if isinstance(t, Atom) and t.name == name)


def serialize(term: Term) -> str:
    """Stable prefix serialization for hashing/certificates."""
    if isinstance(term, Atom):
        return term.name
    if isinstance(term, App):
        return f"@({serialize(term.fn)},{serialize(term.arg)})"
    raise TypeError(type(term))
