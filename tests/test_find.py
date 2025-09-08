import unittest
import os
import shutil
import argparse
from io import StringIO
from features import find as find_feature


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


class TestFindCommand(unittest.TestCase):
    def setUp(self):
        self.base = "tests/data_find"
        os.makedirs(self.base, exist_ok=True)

        # files: a.txt, b.md, sub/c.txt
        with open(os.path.join(self.base, "a.txt"), "w", encoding="utf-8") as f:
            f.write("a")
        with open(os.path.join(self.base, "b.md"), "w", encoding="utf-8") as f:
            f.write("b")

        sub = os.path.join(self.base, "sub")
        os.makedirs(sub, exist_ok=True)
        with open(os.path.join(sub, "c.txt"), "w", encoding="utf-8") as f:
            f.write("c")

        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-p", "--path", required=True)
        self.parser.add_argument("-r", "--regex", required=True)

    def tearDown(self):
        if os.path.exists(self.base):
            shutil.rmtree(self.base, ignore_errors=True)

    def test_find_txt_files(self):
        args = self.parser.parse_args(["-p", self.base, "-r", r".*\.txt"])
        matches, out = capture_stdout(find_feature.run, args)

        self.assertIsInstance(matches, list)
        self.assertEqual(len(matches), 2)  # a.txt + sub/c.txt
        self.assertIn("a.txt", "\n".join(matches))
        self.assertIn("c.txt", "\n".join(matches))
        self.assertIn(".txt", out)

    def test_find_no_matches(self):
        args = self.parser.parse_args(["-p", self.base, "-r", r".*\.pdf"])
        matches, out = capture_stdout(find_feature.run, args)

        self.assertEqual(matches, [])
        self.assertIn("No matches", out)

    def test_invalid_regex(self):
        args = self.parser.parse_args(["-p", self.base, "-r", r"*bad["])
        matches, err = capture_stderr(find_feature.run, args)

        self.assertIsNone(matches)
        self.assertIn("error", err.lower())
        self.assertIn("invalid regex", err.lower())

    def test_nonexistent_path(self):
        args = self.parser.parse_args(["-p", "no_such_dir", "-r", r".*"])
        matches, err = capture_stderr(find_feature.run, args)

        self.assertIsNone(matches)
        self.assertIn("error", err.lower())
        self.assertIn("path not found", err.lower())

    def test_not_a_directory(self):
        file_path = os.path.join(self.base, "a.txt")
        args = self.parser.parse_args(["-p", file_path, "-r", r".*"])
        matches, err = capture_stderr(find_feature.run, args)

        self.assertIsNone(matches)
        self.assertIn("error", err.lower())
        self.assertIn("not a directory", err.lower())


if __name__ == "__main__":
    unittest.main()
