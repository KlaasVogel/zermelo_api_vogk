import sys
from pathlib import Path

# The package lives in app/ (setup.py's package_dir) and isn't installed in the dev venv.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))
