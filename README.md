# RCFS implemented as MicroHs IotaTrees Barker SKI

This codebase is a compact executable scaffold for the chain:

```text
(FAS) → SKI → ι(Barker) → PHYS-mandala → ΔRCFS → Ω
```

It implements:

- MicroHs-style lambda abstraction elimination into SKI.
- Barker iota encoding with a single primitive `ι`, where `ι x = x S K`.
- Church numeral generation as lambda terms, SKI terms, and Barker-iota trees.
- Exact tree metrics: iota count, node count, depth, hash, redex counts.
- SKI reduction traces and normal-form/residue summaries.
- A dependency-free SVG radial mandala renderer for PHYS-lift witnesses.
- A CLI for compilation, rendering, and audit export.

The project deliberately separates **formal combinatory closure** from stronger biological/material Rosen closure. The code certifies formal transport and replay inside the λ/SKI/ι graph-reduction theater; it does not assert material autopoiesis.

## Install

```bash
cd rcfs_iota_codebase
python -m pip install -e .
```

## Quickstart

Compile Church numeral 3 to SKI and Barker iota:

```bash
rcfs-iota church 3 --emit all
```

Render a mandala SVG:

```bash
rcfs-iota church 4 --svg out/church4.svg --json out/church4.audit.json
```

Run the RCFS/FAS demo:

```bash
rcfs-iota rcfs-demo --svg out/rcfs_fas.svg --json out/rcfs_fas.audit.json
```

## Python API

```python
from rcfs_iota import church_numeral, bracket_abstract, expand_ski_to_iota, audit_term, render_svg

lam = church_numeral(3)
ski = bracket_abstract(lam)
iota = expand_ski_to_iota(ski)
cert = audit_term(iota, source="Church_3")
svg = render_svg(iota, title="Church 3 Barker iota mandala")
```

## Important precision

- `transport obstruction = 0` only for **basis equivalence** from SKI to Barker iota.
- Operational obstructions remain: size blowup, sharing loss, normalization cost, and nontermination for fixed-point terms.
- `ΔRCFS` is an audit ledger: the difference between expected closure invariants and realized replay invariants after transport/reduction/rendering.

## Repository layout

```text
rcfs_iota/
  terms.py        # immutable term AST
  lambda_calc.py  # lambda terms and MicroHs-style bracket abstraction
  ski.py          # SKI primitives, reduction, normal forms
  iota.py         # Barker iota encodings and expansion
  church.py       # Church numerals and iteration terms
  rcfs.py         # F/A/S role mapping and demo graph terms
  audit.py        # exact metrics, hashes, ΔRCFS certificate
  render.py       # dependency-free SVG radial renderer
  cli.py          # command line interface
examples/
  church6.py
  rcfs_fas_demo.py
tests/
  test_core.py
```

## License

MIT.
