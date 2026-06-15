from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .audit import audit_term
from .church import church_iota, church_ski, church_numeral
from .iota import expand_ski_to_iota, iota_count
from .lambda_calc import lambda_to_ski
from .rcfs import rcfs_fas_kernel_iota, rcfs_fas_kernel_ski, fas_role_map
from .render import render_svg
from .terms import pretty


def _write_text(path: str | None, text: str) -> None:
    if not path:
        return
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def cmd_church(args: argparse.Namespace) -> int:
    lam = church_numeral(args.n)
    ski = church_ski(args.n)
    iota = church_iota(args.n)
    cert = audit_term(iota, source=f"Church_{args.n}", max_iota_steps=args.max_iota_steps, max_ski_steps=args.max_ski_steps)

    if args.emit in {"lambda", "all"}:
        print("λ:", lam)
    if args.emit in {"ski", "all"}:
        print("SKI:", pretty(ski, args.max_chars))
    if args.emit in {"iota", "all"}:
        print("ι:", pretty(iota, args.max_chars))
    if args.emit in {"audit", "all"}:
        print(cert.to_json())

    if args.svg:
        _write_text(args.svg, render_svg(iota, title=f"Church {args.n} Barker iota mandala"))
        print(f"wrote {args.svg}", file=sys.stderr)
    if args.json:
        _write_text(args.json, cert.to_json())
        print(f"wrote {args.json}", file=sys.stderr)
    return 0


def cmd_rcfs_demo(args: argparse.Namespace) -> int:
    ski = rcfs_fas_kernel_ski()
    iota = rcfs_fas_kernel_iota()
    cert = audit_term(iota, source="RCFS_FAS_kernel", max_iota_steps=args.max_iota_steps, max_ski_steps=args.max_ski_steps)
    roles = fas_role_map()

    print("RCFS/FAS role map:")
    print("  F fabrication:", roles.fabrication)
    print("  A repair:", roles.repair)
    print("  S replication:", roles.self_replication)
    print("  note:", roles.description)
    print("SKI:", pretty(ski, args.max_chars))
    print("ι:", pretty(iota, args.max_chars))
    print(cert.to_json())

    if args.svg:
        _write_text(args.svg, render_svg(iota, title="RCFS F/A/S Barker iota mandala"))
        print(f"wrote {args.svg}", file=sys.stderr)
    if args.json:
        _write_text(args.json, cert.to_json())
        print(f"wrote {args.json}", file=sys.stderr)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="rcfs-iota",
        description="Compile λ/MicroHs-style terms to SKI, Barker iota trees, PHYS mandalas, and ΔRCFS audits.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("church", help="compile/audit/render a Church numeral")
    c.add_argument("n", type=int)
    c.add_argument("--emit", choices=["lambda", "ski", "iota", "audit", "all"], default="audit")
    c.add_argument("--svg", help="write mandala SVG")
    c.add_argument("--json", help="write audit JSON")
    c.add_argument("--max-chars", type=int, default=800)
    c.add_argument("--max-iota-steps", type=int, default=20_000)
    c.add_argument("--max-ski-steps", type=int, default=20_000)
    c.set_defaults(func=cmd_church)

    r = sub.add_parser("rcfs-demo", help="compile/audit/render the compact RCFS F/A/S motif")
    r.add_argument("--svg", help="write mandala SVG")
    r.add_argument("--json", help="write audit JSON")
    r.add_argument("--max-chars", type=int, default=800)
    r.add_argument("--max-iota-steps", type=int, default=20_000)
    r.add_argument("--max-ski-steps", type=int, default=20_000)
    r.set_defaults(func=cmd_rcfs_demo)
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
