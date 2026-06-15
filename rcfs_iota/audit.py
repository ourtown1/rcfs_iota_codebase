from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from typing import Any

from .terms import App, Atom, Term, pretty, serialize
from .iota import iota_count, expand_iota_to_ski, is_pure_iota
from .ski import reduce_ski, redex_count_ski


@dataclass(frozen=True)
class AuditCertificate:
    source: str
    term_hash: str
    node_count: int
    depth: int
    iota_symbols: int
    pure_iota: bool
    ski_redexes_before: int
    iota_steps: int
    ski_steps: int
    normalized: bool
    normal_form_hash: str
    normal_form_preview: str
    residue: str
    delta_rcfs: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False, sort_keys=True)


def _hash(term: Term | str) -> str:
    payload = serialize(term) if not isinstance(term, str) else term
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def mixed_reduce(term: Term, max_iota_steps: int = 20_000, max_ski_steps: int = 20_000) -> tuple[Term, list[str], list[str]]:
    """Replay pure iota into mixed SKI, then SKI-normalize.

    This is a certificate route, not a cost-optimal evaluator.
    """
    mixed, iota_trace = expand_iota_to_ski(term, max_steps=max_iota_steps)
    normal, ski_trace = reduce_ski(mixed, max_steps=max_ski_steps)
    return normal, iota_trace, ski_trace


def delta_rcfs(
    term: Term,
    normal_form: Term,
    iota_trace: list[str],
    ski_trace: list[str],
    max_iota_steps: int,
    max_ski_steps: int,
) -> dict[str, Any]:
    """Closure residue ledger.

    ΔRCFS is not assumed to be zero. It records what failed or survived after transport.
    """
    iota_halt = bool(iota_trace and iota_trace[-1].startswith("HALT"))
    ski_halt = bool(ski_trace and ski_trace[-1].startswith("HALT"))
    symbolic_atoms = sorted(
        {t.name for t in normal_form.walk() if isinstance(t, Atom) and t.name not in {"S", "K", "I", "Y", "ι"}}
    )
    return {
        "basis_obstruction": 0 if not symbolic_atoms else "symbolic_atoms_remaining",
        "symbolic_atoms_remaining": symbolic_atoms,
        "iota_halt": iota_halt,
        "ski_halt": ski_halt,
        "iota_steps": len(iota_trace),
        "ski_steps": len(ski_trace),
        "operational_obstructions": [
            item
            for item, active in [
                ("iota_step_limit", iota_halt),
                ("ski_step_limit_or_divergence", ski_halt),
                ("symbolic_unexpanded_atoms", bool(symbolic_atoms)),
                ("size_blowup_risk", term.node_count() > 5_000),
                ("deep_tree_risk", term.depth() > 512),
            ]
            if active
        ],
    }


def audit_term(
    term: Term,
    source: str = "term",
    max_iota_steps: int = 20_000,
    max_ski_steps: int = 20_000,
) -> AuditCertificate:
    normal, iota_trace, ski_trace = mixed_reduce(term, max_iota_steps=max_iota_steps, max_ski_steps=max_ski_steps)
    residue = "closed" if not delta_rcfs(term, normal, iota_trace, ski_trace, max_iota_steps, max_ski_steps)["operational_obstructions"] else "residue-present"
    delta = delta_rcfs(term, normal, iota_trace, ski_trace, max_iota_steps, max_ski_steps)
    return AuditCertificate(
        source=source,
        term_hash=_hash(term),
        node_count=term.node_count(),
        depth=term.depth(),
        iota_symbols=iota_count(term),
        pure_iota=is_pure_iota(term),
        ski_redexes_before=redex_count_ski(term),
        iota_steps=len(iota_trace),
        ski_steps=len(ski_trace),
        normalized=not any(str(x).startswith("HALT") for x in [*(iota_trace[-1:] or []), *(ski_trace[-1:] or [])]),
        normal_form_hash=_hash(normal),
        normal_form_preview=pretty(normal, max_chars=320),
        residue=residue,
        delta_rcfs=delta,
    )
