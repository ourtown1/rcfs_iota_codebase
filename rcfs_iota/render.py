from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable

from .terms import App, Atom, Term
from .iota import iota_count


@dataclass(frozen=True)
class PositionedNode:
    idx: int
    label: str
    x: float
    y: float
    depth: int
    parent: int | None


def _collect_positions(term: Term, radius_step: float = 42.0, center: tuple[float, float] = (500.0, 500.0)) -> list[PositionedNode]:
    leaves: list[int] = []
    nodes: list[tuple[str, int, int | None]] = []

    def visit(t: Term, depth: int, parent: int | None) -> int:
        idx = len(nodes)
        label = "@" if isinstance(t, App) else t.name
        nodes.append((label, depth, parent))
        if isinstance(t, App):
            visit(t.fn, depth + 1, idx)
            visit(t.arg, depth + 1, idx)
        else:
            leaves.append(idx)
        return idx

    visit(term, 0, None)
    n = max(1, len(nodes))
    max_depth = max(depth for _, depth, _ in nodes) if nodes else 1

    # Assign angular slots by DFS order, then interpolate internal nodes as average child angle.
    angle: dict[int, float] = {}
    leaf_order = 0

    def assign(t: Term, idx_iter: list[int]) -> float:
        idx = idx_iter[0]
        idx_iter[0] += 1
        if isinstance(t, App):
            left_angle = assign(t.fn, idx_iter)
            right_angle = assign(t.arg, idx_iter)
            angle[idx] = (left_angle + right_angle) / 2.0
        else:
            nonlocal leaf_order
            angle[idx] = 2.0 * math.pi * leaf_order / max(1, len(leaves))
            leaf_order += 1
        return angle[idx]

    assign(term, [0])

    cx, cy = center
    positioned: list[PositionedNode] = []
    for idx, (label, depth, parent) in enumerate(nodes):
        r = 18.0 + radius_step * depth
        a = angle[idx]
        x = cx + r * math.cos(a)
        y = cy + r * math.sin(a)
        positioned.append(PositionedNode(idx, label, x, y, depth, parent))
    return positioned


def render_svg(
    term: Term,
    title: str = "Barker iota PHYS mandala",
    width: int = 1000,
    height: int = 1000,
    max_nodes: int = 2500,
) -> str:
    """Dependency-free radial SVG renderer.

    For very large terms, only the first max_nodes in traversal are rendered, while
    the certificate should still be computed on the full term.
    """
    nodes = _collect_positions(term, center=(width / 2, height / 2))
    truncated = len(nodes) > max_nodes
    draw_nodes = nodes[:max_nodes]
    keep = {n.idx for n in draw_nodes}

    def color(label: str, depth: int) -> str:
        if label == "ι":
            return "#13294b"
        if label == "@":
            palette = ["#2f6db3", "#2e8b57", "#7b3294", "#e66101", "#b2182b", "#008c8c"]
            return palette[depth % len(palette)]
        if label == "S":
            return "#2e8b57"
        if label == "K":
            return "#7b3294"
        if label == "I":
            return "#e66101"
        if label == "Y":
            return "#b2182b"
        return "#555555"

    lines: list[str] = []
    circles: list[str] = []
    labels: list[str] = []
    idx_to_node = {n.idx: n for n in nodes}
    for n in draw_nodes:
        if n.parent is not None and n.parent in keep:
            p = idx_to_node[n.parent]
            lines.append(
                f'<line x1="{p.x:.2f}" y1="{p.y:.2f}" x2="{n.x:.2f}" y2="{n.y:.2f}" '
                f'stroke="#9aa6b2" stroke-width="0.65" opacity="0.65" />'
            )
        c = color(n.label, n.depth)
        rad = 4.2 if n.label == "ι" else 3.0
        if n.label == "@":
            rad = 2.0
        circles.append(f'<circle cx="{n.x:.2f}" cy="{n.y:.2f}" r="{rad:.2f}" fill="{c}" opacity="0.92" />')
        if n.depth < 3 or n.label != "@" and len(draw_nodes) < 400:
            labels.append(
                f'<text x="{n.x + 5:.2f}" y="{n.y - 5:.2f}" font-size="10" fill="{c}" '
                f'font-family="Menlo,Consolas,monospace">{_escape(n.label)}</text>'
            )

    subtitle = f"nodes={term.node_count()} depth={term.depth()} #ι={iota_count(term)}"
    if truncated:
        subtitle += f" rendered={max_nodes}"
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="#fbfbfa"/>
  <text x="{width/2:.0f}" y="42" text-anchor="middle" font-size="28" font-weight="700" fill="#111827" font-family="Inter,Arial,sans-serif">{_escape(title)}</text>
  <text x="{width/2:.0f}" y="70" text-anchor="middle" font-size="14" fill="#4b5563" font-family="Inter,Arial,sans-serif">{_escape(subtitle)}</text>
  <g>{''.join(lines)}</g>
  <g>{''.join(circles)}</g>
  <g>{''.join(labels)}</g>
  <circle cx="{width/2:.0f}" cy="{height/2:.0f}" r="8" fill="#111827"/>
  <text x="24" y="{height-24}" font-size="12" fill="#6b7280" font-family="Inter,Arial,sans-serif">PHYS-lift witness: radial applicative tree / mandala render. Certificate must be audited separately.</text>
</svg>'''
    return svg


def _escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
