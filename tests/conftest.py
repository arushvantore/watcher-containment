"""conftest.py — pytest setup that runs BEFORE any test imports.

We point DATABASE_PATH at a throwaway temp file so tests NEVER touch your
real db/agents.sqlite. This must happen before server.db is imported,
which is why it sits at module level here (pytest loads conftest first).
"""

import os
import tempfile

_fd, _path = tempfile.mkstemp(suffix=".sqlite")
os.close(_fd)
os.environ["DATABASE_PATH"] = _path
