"""test_no_external_urls.py — the dashboard can never phone home.

Scans every author-authored file under dashboard/ recursively and fails the
build if any absolute URL (http:// or https://) appears. All data must come
from same-origin relative paths (/agents, /health, /logs).

Excluded: dashboard/fonts/ and dashboard/vendor/ — these are VENDORED local
assets (OFL fonts, MIT Three.js) downloaded once at build time and served
from this same origin. They are files on disk, not network fetches.
"""

from pathlib import Path

DASHBOARD_DIR = Path(__file__).resolve().parent.parent / "dashboard"

# vendored asset directories — local files, never fetched at runtime
SKIP_DIRS = {"fonts", "vendor"}


def _author_files():
    for f in sorted(DASHBOARD_DIR.rglob("*")):
        if not f.is_file() or f.name == ".gitkeep":
            continue
        rel = f.relative_to(DASHBOARD_DIR)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        yield f


def test_dashboard_contains_no_absolute_urls():
    offenders = []
    for f in _author_files():
        text = f.read_text(encoding="utf-8")
        for i, line in enumerate(text.splitlines(), 1):
            if "http://" in line or "https://" in line:
                offenders.append(f"{f.relative_to(DASHBOARD_DIR)}:{i}: {line.strip()}")
    assert not offenders, (
        "dashboard must not reference outside URLs:\n" + "\n".join(offenders)
    )


def test_dashboard_fetches_are_relative_only():
    """Every fetch() call must start with a same-origin path."""
    text = (DASHBOARD_DIR / "index.html").read_text(encoding="utf-8")
    for line in text.splitlines():
        if "fetch(" in line:
            assert "http" not in line, f"fetch must be relative, got: {line.strip()}"


def test_three_and_fonts_are_vendored_locally():
    """The 3D globe lib and fonts must load from local vendor paths only."""
    text = (DASHBOARD_DIR / "index.html").read_text(encoding="utf-8")
    assert "./vendor/three.module.js" in text, "three.js must be imported from ./vendor/"
    assert "./fonts/" in text, "fonts must be loaded from ./fonts/"
    assert "cdn." not in text and "unpkg" not in text and "jsdelivr" not in text, (
        "no CDN references allowed in index.html"
    )
    assert (DASHBOARD_DIR / "vendor" / "three.module.js").exists()
    assert any((DASHBOARD_DIR / "fonts").glob("*.woff2"))
