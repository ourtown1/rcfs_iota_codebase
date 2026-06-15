from __future__ import annotations

from .terms import App, Atom, Term, app, apps, atom, count_atom, replace_atoms, left_spine
from .ski import S, K, I, Y

IOTA = atom("ι")


def iota_I() -> Term:
    # I = ι ι
    return app(IOTA, IOTA)


def iota_K() -> Term:
    # K = ι(ι(ι ι))
    return app(IOTA, app(IOTA, app(IOTA, IOTA)))


def iota_S() -> Term:
    # S = ι(ι(ι(ι ι)))
    return app(IOTA, app(IOTA, app(IOTA, app(IOTA, IOTA))))


def iota_Y_symbolic() -> Term:
    """Y has no primitive finite Barker encoding unless given as an SKI term first.

    This placeholder is intentionally blocked from pure expansion; callers should provide
    an SKI definition for Y or keep Y symbolic and audit the fixed-point obstruction.
    """
    return atom("Y_UNEXPANDED")


def expand_ski_to_iota(term: Term, expand_y: bool = False) -> Term:
    """Replace S/K/I leaves by Barker iota encodings.

    This produces a pure iota tree for terms containing only S/K/I and application.
    If Y is present, either keep it as a symbolic obstruction or provide/inline a concrete SKI Y.
    """
    if isinstance(term, Atom):
        if term.name == "S":
            return iota_S()
        if term.name == "K":
            return iota_K()
        if term.name == "I":
            return iota_I()
        if term.name == "ι":
            return IOTA
        if term.name == "Y":
            if expand_y:
                raise NotImplementedError("Inline a concrete SKI Y term before Barker expansion.")
            return atom("Y")
        return term
    if isinstance(term, App):
        return app(expand_ski_to_iota(term.fn, expand_y=expand_y), expand_ski_to_iota(term.arg, expand_y=expand_y))
    raise TypeError(type(term))


def iota_count(term: Term) -> int:
    return count_atom(term, "ι")


def is_pure_iota(term: Term) -> bool:
    return all(isinstance(t, App) or (isinstance(t, Atom) and t.name == "ι") for t in term.walk())


def iota_to_mixed_ski_step(term: Term) -> tuple[Term, str | None]:
    """One normal-order Barker step: ι x -> x S K.

    This intentionally introduces S/K so a pure iota tree can be replayed by mixed iota/SKI
    reduction. Full reduction is handled in audit.py by alternating iota and SKI contractions.
    """
    if isinstance(term, App) and isinstance(term.fn, Atom) and term.fn.name == "ι":
        return apps(term.arg, S, K), "ι x -> x S K"
    if isinstance(term, App):
        nf, rule = iota_to_mixed_ski_step(term.fn)
        if rule:
            return app(nf, term.arg), rule
        na, rule = iota_to_mixed_ski_step(term.arg)
        if rule:
            return app(term.fn, na), rule
    return term, None


def expand_iota_to_ski(term: Term, max_steps: int = 10_000) -> tuple[Term, list[str]]:
    cur = term
    trace: list[str] = []
    for _ in range(max_steps):
        nxt, rule = iota_to_mixed_ski_step(cur)
        if rule is None:
            return cur, trace
        trace.append(rule)
        cur = nxt
    trace.append(f"HALT: iota max_steps={max_steps} reached")
    return cur, trace
