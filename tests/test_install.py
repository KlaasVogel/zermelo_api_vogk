"""Regression test for install.py's basicConfig() side effect.

install.py used to call logging.basicConfig(filename="example.log", ...) at
import time, and it's imported unconditionally by zermelo_api/__init__.py -
so every `import zermelo_api`, by any consumer, silently redirected all
logging output to a growing example.log file in the consumer's working
directory instead of letting the consumer configure its own logging.

Runs in a subprocess so the check reflects a genuinely fresh import, not one
already cached (and thus already side-effected) by an earlier test/import in
this same process.
"""

import os
import subprocess
import sys
from pathlib import Path

APP_DIR = str(Path(__file__).resolve().parent.parent / "app")


def _run_in_subprocess(tmp_path, code: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "PYTHONPATH": APP_DIR}
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )


def test_import_does_not_create_example_log(tmp_path):
    result = _run_in_subprocess(tmp_path, "import zermelo_api")
    assert result.returncode == 0, result.stderr
    assert not (tmp_path / "example.log").exists()


def test_import_does_not_configure_root_logger(tmp_path):
    result = _run_in_subprocess(
        tmp_path,
        "import logging\nimport zermelo_api\nprint(len(logging.getLogger().handlers))",
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "0"
