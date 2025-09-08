import unittest
import os
import shutil
import argparse
from io import StringIO
from features import duplicates as dup_feature


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


class TestDuplicates(unittest.TestCase):
    def setUp(self):
        self.base = "tests/data_duplicates"
        os.makedirs(self.base, exist_ok=True)

        # layout:
        # base/
        #   a.txt      ("SAME")
        #   b.txt      ("SAME")   -> duplicate with a.txt
        #   c.txt      ("DIFF")
        #   sub/
        #     d.txt    ("SAME")   -> duplicate with a.txt/b.txt
        self.a = os.path.join(self.base, "a.txt")
        self.b = os.path.join(self.base, "b.txt")
        self.c = os.path.join(self.base, "c.txt")
        sub = os.path.join(self.base, "sub")
        os.makedirs(sub, exist_ok=True)
        self.d = os.path.join(sub, "d.txt")

        for p, content in [(self.a, "SAME"), (self.b, "SAME"), (self.c, "DIFF"), (self.d, "SAME")]:
            with open(p, "w", encoding="utf-8") as f:
                f.write(content)

        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-p", "--path", required=True)

    def tearDown(self):
        if os.path.exists(self.base):
            shutil.rmtree(self.base, ignore_errors=True)

    def test_duplicates_found(self):
        args = self.parser.parse_args(["-p", self.base])
        groups, out = capture_stdout(dup_feature.run, args)

        self.assertIsInstance(groups, list)
        # Expect a group that contains a,b,d (3 files), not c
        flat = []
        for g in groups:
            flat.extend(g["files"])
        # Normalize to forward slashes in checks not needed; just verify presence
        self.assertIn(self.a, flat)
        self.assertIn(self.b, flat)
        self.assertIn(self.d, flat)
        self.assertNotIn(self.c, flat)

        # stdout should have "Duplicate group"
        self.assertIn("Duplicate group #", out)

    def test_no_duplicates(self):
        # Make all files unique
        shutil.rmtree(self.base, ignore_errors=True)
        os.makedirs(self.base, exist_ok=True)
        paths = [os.path.join(self.base, f"u{i}.txt") for i in range(3)]
        for i, p in enumerate(paths):
            with open(p, "w", encoding="utf-8") as f:
                f.write(f"unique-{i}")

        args = self.parser.parse_args(["-p", self.base])
        groups, out = capture_stdout(dup_feature.run, args)
        self.assertEqual(groups, [])
        self.assertIn("No duplicates found", out)

    def test_path_not_directory(self):
        file_path = os.path.join(self.base, "file.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("x")

        args = self.parser.parse_args(["-p", file_path])
        groups, err = capture_stderr(dup_feature.run, args)

        self.assertIsNone(groups)
        self.assertIn("error", err.lower())
        self.assertIn("not a directory", err.lower())

    def test_path_not_found(self):
        missing = os.path.join(self.base, "no_such_dir")
        args = self.parser.parse_args(["-p", missing])
        groups, err = capture_stderr(dup_feature.run, args)

        self.assertIsNone(groups)
        self.assertIn("error", err.lower())
        self.assertIn("path not found", err.lower())


if __name__ == "__main__":
    unittest.main()
