from rcfs_iota import App, I, K, S, app, apps, audit_term, church_iota, church_ski, expand_ski_to_iota, iota_count, normalize_ski
from rcfs_iota.iota import iota_I, iota_K, iota_S, expand_iota_to_ski
from rcfs_iota.ski import reduce_ski
from rcfs_iota.terms import atom


def test_i_reduces():
    x = atom("x")
    assert str(normalize_ski(app(I, x))) == "x"


def test_k_reduces():
    x = atom("x")
    y = atom("y")
    assert str(normalize_ski(apps(K, x, y))) == "x"


def test_s_reduces_shape():
    x, y, z = atom("x"), atom("y"), atom("z")
    out = normalize_ski(apps(S, x, y, z))
    assert str(out) == "((x z) (y z))"


def test_iota_encodings_have_iota_symbols():
    assert iota_count(iota_I()) == 2
    assert iota_count(iota_K()) == 4
    assert iota_count(iota_S()) == 5


def test_church_iota_audits():
    t = church_iota(2)
    cert = audit_term(t, source="Church_2")
    assert cert.iota_symbols > 0
    assert cert.node_count >= cert.iota_symbols
    assert cert.term_hash
