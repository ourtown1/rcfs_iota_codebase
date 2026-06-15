from __future__ import annotations

from dataclasses import dataclass

from .terms import Term, atom, app, apps
from .ski import S, K, I, Y
from .iota import expand_ski_to_iota


@dataclass(frozen=True)
class RCFSRoleMap:
    fabrication: Term
    repair: Term
    self_replication: Term
    description: str


def fas_role_map() -> RCFSRoleMap:
    """Formal F/A/S role map inside the SKI theater.

    F fabrication    -> S: duplicates/distributes argument structure.
    A repair/assembly -> K: projects/preserves selected structure.
    S replication    -> I/Y: identity and fixed-point recurrence.
    """
    return RCFSRoleMap(
        fabrication=S,
        repair=K,
        self_replication=Y,
        description=(
            "Formal analogue only: S/K/I/Y implement fabrication, repair/projection, "
            "and self-replication/fixed-point roles in combinatory logic."
        ),
    )


def symbolic_repair_function() -> Term:
    return atom("repair")


def rcfs_closure_example() -> Term:
    """Symbolic SKI-level closure witness.

    Represents the schematic term:
      Y (λself. λinput. S (K self) (repair input))

    The lambda portion is kept symbolic here to avoid pretending this is a completed
    biological Rosen model. It is a formal fixed-point closure skeleton.
    """
    SELF_REPAIR_BODY = atom("SELF_REPAIR_BODY")
    return app(Y, SELF_REPAIR_BODY)


def rcfs_fas_kernel_ski() -> Term:
    """A compact executable F/A/S motif: S K I.

    It is not a full Rosen organism; it is a formal marker showing the three role
    residues in one closed SKI phrase.
    """
    return apps(S, K, I)


def rcfs_fas_kernel_iota() -> Term:
    return expand_ski_to_iota(rcfs_fas_kernel_ski())
