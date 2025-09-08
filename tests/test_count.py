import unittest
import os
import shutil
import argparse
from io import StringIO
from features import count as count_feature


def capture_stdout(func, *args, **kwargs):
    old = os.sys.stdout
    buf = StringIO()
    try:
        os.sys.stdout = buf
        ret = func(*args, **kwargs)
        return ret, buf.getvalue()
    finally:
        os.sys.stdout = old


def capture_stderr(func, *args, **kwargs):
    old = os.sys.stderr
    buf = StringIO()
    try:
        os.sys.stderr = buf
        ret = func(*args, **kwargs)
        return ret, buf.getvalue()
    finally:
        os.sys.stderr = old


class TestCountCommand(unittest.TestCase):
    def setUp(self):
        self.base = "tests/data_count"
        # structure:
        # data_count/
        #   a.txt
        #   b.txt
        #   sub/
        #       c.txt
        #       deeper/
        #           d.txt
        os.makedirs(self.base, exist_ok=True)
        with open(os.path.join(self.base, "a.txt"), "w", encoding="utf-8") as f:
            f.write("a")
        with open(os.path.join(self.base, "b.txt"), "w", encoding="utf-8") as f:
            f.write("b")

        sub = os.path.join(self.base, "sub")
        os.makedirs(sub, exist_ok=True)
        with open(os.path.join(sub, "c.txt"), "w", encoding="utf-8") as f:
            f.write("c")

        deeper = os.path.join(sub, "deeper")
        os.makedirs(deeper, exist_ok=True)
        with open(os.path.join(deeper, "d.txt"), "w", encoding="utf-8") as f:
            f.write("d")

        # emulate manager.py args
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-p", "--path", required=True)

    def tearDown(self):
        if os.path.exists(self.base):
            shutil.rmtree(self.base, ignore_errors=True)

    def test_count_recursive(self):
        """Counts all files recursively (4 in total)."""
        args = self.parser.parse_args(["-p", self.base])
        total, out = capture_stdout(count_feature.run, args)

        self.assertEqual(total, 4)
        self.assertIn("Total files in", out)
        self.assertIn(": 4", out)

    def test_count_on_subdir(self):
        """Counts subdir only (2 files: c.txt and deeper/d.txt)."""
        sub = os.path.join(self.base, "sub")
        args = self.parser.parse_args(["-p", sub])
        total, out = capture_stdout(count_feature.run, args)

        self.assertEqual(total, 2)
        self.assertIn("Total files in", out)
        self.assertIn(": 2", out)

    def test_nonexistent_path(self):
        """Nonexistent path -> None and stderr message."""
        missing = os.path.join(self.base, "no_such_dir")
        self.assertFalse(os.path.exists(missing))

        args = self.parser.parse_args(["-p", missing])
        total, err = capture_stderr(count_feature.run, args)

        self.assertIsNone(total)
        self.assertIn("error", err.lower())
        self.assertIn("path not found", err.lower())

    def test_not_a_directory(self):
        """Existing file passed as path -> None and stderr message."""
        file_path = os.path.join(self.base, "a.txt")
        args = self.parser.parse_args(["-p", file_path])
        total, err = capture_stderr(count_feature.run, args)

        self.assertIsNone(total)
        self.assertIn("error", err.lower())
        self.assertIn("not a directory", err.lower())


if __name__ == "__main__":
    unittest.main()
