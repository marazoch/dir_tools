import unittest
import os
import shutil
import argparse
from io import StringIO
from features import move as move_feature


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


class TestMoveCommand(unittest.TestCase):
    def setUp(self):
        self.base = "tests/data_move"
        os.makedirs(self.base, exist_ok=True)

        self.src_file = os.path.join(self.base, "file.txt")
        with open(self.src_file, "w", encoding="utf-8") as f:
            f.write("hello")

        self.dst_dir = os.path.join(self.base, "dst")
        os.makedirs(self.dst_dir, exist_ok=True)

        # emulate manager.py args
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-s", "--src", required=True)
        self.parser.add_argument("-d", "--dst", required=True)

    def tearDown(self):
        if os.path.exists(self.base):
            shutil.rmtree(self.base, ignore_errors=True)

    def test_move_file_success(self):
        args = self.parser.parse_args(["-s", self.src_file, "-d", self.dst_dir])
        new_path, out = capture_stdout(move_feature.run, args)

        expected = os.path.join(self.dst_dir, "file.txt")
        self.assertEqual(os.path.abspath(expected), new_path)
        self.assertFalse(os.path.exists(self.src_file))
        self.assertTrue(os.path.exists(expected))
        self.assertIn("Moved:", out)

    def test_move_nonexistent_source(self):
        missing = os.path.join(self.base, "nope.txt")
        args = self.parser.parse_args(["-s", missing, "-d", self.dst_dir])
        new_path, err = capture_stderr(move_feature.run, args)

        self.assertIsNone(new_path)
        self.assertIn("error", err.lower())
        self.assertIn("source not found", err.lower())

    def test_move_nonexistent_destination(self):
        missing_dst = os.path.join(self.base, "no_such_dir")
        args = self.parser.parse_args(["-s", self.src_file, "-d", missing_dst])
        new_path, err = capture_stderr(move_feature.run, args)

        self.assertIsNone(new_path)
        self.assertIn("error", err.lower())
        self.assertIn("destination not found", err.lower())

    def test_move_when_target_exists(self):
        # put a file in dst with same name
        conflict = os.path.join(self.dst_dir, "file.txt")
        with open(conflict, "w", encoding="utf-8") as f:
            f.write("existing")

        args = self.parser.parse_args(["-s", self.src_file, "-d", self.dst_dir])
        new_path, err = capture_stderr(move_feature.run, args)

        self.assertIsNone(new_path)
        self.assertIn("error", err.lower())
        self.assertIn("already exists", err.lower())


if __name__ == "__main__":
    unittest.main()
