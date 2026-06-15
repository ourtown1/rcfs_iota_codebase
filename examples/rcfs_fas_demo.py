from pathlib import Path

from rcfs_iota import audit_term, render_svg
from rcfs_iota.rcfs import rcfs_fas_kernel_iota

out = Path("out")
out.mkdir(exist_ok=True)
term = rcfs_fas_kernel_iota()
cert = audit_term(term, source="RCFS_FAS_kernel")
(out / "rcfs_fas.audit.json").write_text(cert.to_json(), encoding="utf-8")
(out / "rcfs_fas.svg").write_text(render_svg(term, title="RCFS F/A/S Barker iota mandala"), encoding="utf-8")
print(cert.to_json())
