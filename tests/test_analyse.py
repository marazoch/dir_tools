import unittest
import os
import shutil
import argparse
from io import StringIO
from features import analyse as analyse_feature


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


class TestAnalyseCommand(unittest.TestCase):
    def setUp(self):
        self.base = "tests/data_analyse"
        os.makedirs(self.base, exist_ok=True)

        # structure:
        # base/
        #   a.txt (1B)
        #   b.bin (3B)
        #   sub/
        #       c.txt (2B)
        self.a = os.path.join(self.base, "a.txt")
        with open(self.a, "wb") as f:
            f.write(b"A")  # 1 byte

        self.b = os.path.join(self.base, "b.bin")
        with open(self.b, "wb") as f:
            f.write(b"BBB")  # 3 bytes

        self.sub = os.path.join(self.base, "sub")
        os.makedirs(self.sub, exist_ok=True)
        self.c = os.path.join(self.sub, "c.txt")
        with open(self.c, "wb") as f:
            f.write(b"CC")  # 2 bytes

        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-p", "--path", required=True)

    def tearDown(self):
        if os.path.exists(self.base):
            shutil.rmtree(self.base, ignore_errors=True)

    def test_analyse_ok(self):
        args = self.parser.parse_args(["-p", self.base])
        result, out = capture_stdout(analyse_feature.run, args)

        # total: a(1) + b(3) + c(2) = 6 bytes
        self.assertIsInstance(result, dict)
        self.assertEqual(result["path"], os.path.abspath(self.base))
        self.assertEqual(result["total_bytes"], 6)
        # entries contain top-level items only: a.txt, b.bin, sub
        names = {name for name, _ in result["entries"]}
        self.assertEqual(names, {"a.txt", "b.bin", "sub"})

        self.assertIn("full size:", out)
        self.assertIn(" - a.txt", out)
        self.assertIn(" - b.bin", out)
        self.assertIn(" - sub", out)

    def test_nonexistent_path(self):
        missing = os.path.join(self.base, "no_such_dir")
        args = self.parser.parse_args(["-p", missing])
        result, err = capture_stderr(analyse_feature.run, args)

        self.assertIsNone(result)
        self.assertIn("error", err.lower())
        self.assertIn("path not found", err.lower())

    def test_not_a_directory(self):
        args = self.parser.parse_args(["-p", self.a])
        result, err = capture_stderr(analyse_feature.run, args)

        self.assertIsNone(result)
        self.assertIn("error", err.lower())
        self.assertIn("not a directory", err.lower())


if __name__ == "__main__":
    unittest.main()
