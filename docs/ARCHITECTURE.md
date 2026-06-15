# Architecture

## Kernel

```text
(FAS) → SKI → ι(Barker) → PHYS-mandala → ΔRCFS → Ω
```

## Theater separation

This repository implements formal-computational closure only.

| Layer | Meaning | Implemented as |
|---|---|---|
| FAS | Rosen role triad | `S`, `K`, `I/Y` role map |
| SKI | closed combinator graph | immutable applicative AST + reducer |
| Barker ι | single-primitive transport | `S/K/I → ι` structural substitution |
| PHYS mandala | visible residue witness | radial SVG of binary applicative tree |
| ΔRCFS | closure residue ledger | audit JSON containing invariants and obstructions |
| Ω | self-hosting refinement target | scaffolded as replay/audit/repair loop |

## Audit discipline

`ΔRCFS` is not assumed to be zero. It records:

- symbolic atoms that survived transport;
- step-limit or divergence markers;
- iota/SKI replay counts;
- size/depth risk;
- normal-form hash and preview.

## Non-claims

The code does **not** prove biological Rosen closure. It proves an exact formal transport and replay path for lambda/SKI/iota terms, then renders that path as a certificate-bearing graph object.
