"""Offline guards: another app's window or a missing owner claim blocks writes."""

import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('release_ops', Path(__file__).with_name('ops.py'))
ops = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ops)


class WindowTests(unittest.TestCase):
    def check(self, ledger, approved=True):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / 'ledger.md'
            file.write_text(ledger)
            with patch.object(ops, 'LEDGER', file), patch.dict(os.environ, {'LY_RELEASE_WINDOW_CONFIRMED': ops.COMMIT if approved else ''}):
                ops.window()

    def test_exact_owned_window_accepted(self):
        self.check('| `APP-LINKYOH` | `IN_PROGRESS` | 60d5af7 |\n| `APP-CHILLBOUT` | `COMPLETE` |')

    def test_missing_explicit_window_rejected(self):
        with self.assertRaises(AssertionError):
            self.check('| `APP-LINKYOH` | `IN_PROGRESS` | 60d5af7 |', approved=False)

    def test_wrong_or_unclaimed_candidate_rejected(self):
        for own in ('| `APP-LINKYOH` | `COMPLETE` | 60d5af7 |', '| `APP-LINKYOH` | `IN_PROGRESS` | old |'):
            with self.subTest(row=own), self.assertRaises(AssertionError):
                self.check(own)

    def test_foreign_window_rejected(self):
        for owner in ('APP-CHILLBOUT', 'HOST-BASE', 'APP-MARKETDAY'):
            with self.subTest(owner=owner), self.assertRaises(AssertionError):
                self.check('| `APP-LINKYOH` | `IN_PROGRESS` | 60d5af7 |\n| `' + owner + '` | `IN_PROGRESS` |')


if __name__ == '__main__':
    unittest.main()
