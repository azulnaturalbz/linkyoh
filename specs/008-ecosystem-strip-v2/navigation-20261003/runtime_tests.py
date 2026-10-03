"""Reuse the isolated runtime harness without overwriting historical evidence."""

import importlib.util
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('strip_runtime', HERE.parent / 'runtime_tests.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.OUT = HERE / 'evidence'
module.IMAGE = 'linkyoh-web:strip-v2-60d5af7'
module.PREFIX = 'linkyoh-navigation-20261003-qa-'

if __name__ == '__main__':
    sys.exit(module.main())
