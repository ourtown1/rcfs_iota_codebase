from pathlib import Path

from rcfs_iota import audit_term, church_iota, render_svg

out = Path("out")
out.mkdir(exist_ok=True)
term = church_iota(6)
cert = audit_term(term, source="Church_6")
(out / "church6.audit.json").write_text(cert.to_json(), encoding="utf-8")
(out / "church6.svg").write_text(render_svg(term, title="Church 6 Barker iota mandala"), encoding="utf-8")
print(cert.to_json())
