"""test_no_external_urls.py — the dashboard can never phone home.

Scans every file in dashboard/ and fails the build if any absolute URL
(http:// or https://) appears. All data must come from same-origin
relative paths (/agents, /health, /logs).
"""

from pathlib import Path

DASHBOARD_DIR = Path(__file__).resolve().parent.parent / "dashboard"


def test_dashboard_contains_no_absolute_urls():
    offenders = []
    for f in sorted(DASHBOARD_DIR.iterdir()):
        if not f.is_file() or f.name == ".gitkeep":
            continue
        text = f.read_text(encoding="utf-8")
        for i, line in enumerate(text.splitlines(), 1):
            if "http://" in line or "https://" in line:
                offenders.append(f"{f.name}:{i}: {line.strip()}")
    assert not offenders, (
        "dashboard must not reference outside URLs:\n" + "\n".join(offenders)
    )


def test_dashboard_fetches_are_relative_only():
    """Every fetch() call must start with a same-origin path."""
    text = (DASHBOARD_DIR / "index.html").read_text(encoding="utf-8")
    for line in text.splitlines():
        if "fetch(" in line:
            assert "http" not in line, f"fetch must be relative, got: {line.strip()}"
