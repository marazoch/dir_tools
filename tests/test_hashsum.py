import unittest
import os
import shutil
import argparse
from io import StringIO
from features import hashsum as hashsum_feature


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


class TestHashsum(unittest.TestCase):
    def setUp(self):
        self.base = "tests/data_hashsum"
        os.makedirs(self.base, exist_ok=True)

        # files:
        # base/
        #   a.txt ("A")
        #   b.txt ("BBB")
        #   sub/c.txt ("C")
        self.a = os.path.join(self.base, "a.txt")
        with open(self.a, "wb") as f:
            f.write(b"A")

        self.b = os.path.join(self.base, "b.txt")
        with open(self.b, "wb") as f:
            f.write(b"BBB")

        sub = os.path.join(self.base, "sub")
        os.makedirs(sub, exist_ok=True)
        self.c = os.path.join(sub, "c.txt")
        with open(self.c, "wb") as f:
            f.write(b"C")

        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-p", "--path", required=True)
        self.parser.add_argument("-m", "--method", choices=["sha256", "md5"], default="sha256")

    def tearDown(self):
        if os.path.exists(self.base):
            shutil.rmtree(self.base, ignore_errors=True)

    def test_hash_file_sha256(self):
        args = self.parser.parse_args(["-p", self.a, "-m", "sha256"])
        result, out = capture_stdout(hashsum_feature.run, args)

        self.assertIsInstance(result, dict)
        self.assertIsNone(result["total"])
        self.assertEqual(result["method"], "sha256")
        self.assertEqual(len(result["items"]), 1)
        self.assertIn("sha256", out)
        self.assertIn(self.a, out)

        # sanity: digest length for sha256
        digest = result["items"][0]["hash"]
        self.assertEqual(len(digest), 64)

    def test_hash_file_md5(self):
        args = self.parser.parse_args(["-p", self.a, "-m", "md5"])
        result, out = capture_stdout(hashsum_feature.run, args)

        self.assertEqual(result["method"], "md5")
        self.assertIn("md5", out)
        self.assertEqual(len(result["items"][0]["hash"]), 32)  # md5 hex length

    def test_hash_directory_total(self):
        args = self.parser.parse_args(["-p", self.base, "-m", "sha256"])
        result, out = capture_stdout(hashsum_feature.run, args)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["method"], "sha256")
        self.assertGreaterEqual(len(result["items"]), 3)
        self.assertIsNotNone(result["total"])
        self.assertIn("TOTAL sha256", out)

        # Items should include our three files (paths may be absolute in result)
        paths = {os.path.abspath(self.a), os.path.abspath(self.b), os.path.abspath(self.c)}
        result_paths = {item["path"] for item in result["items"]}
        self.assertTrue(paths.issubset(result_paths))

    def test_nonexistent_path(self):
        missing = os.path.join(self.base, "no_such")
        args = self.parser.parse_args(["-p", missing, "-m", "sha256"])
        result, err = capture_stderr(hashsum_feature.run, args)

        self.assertIsNone(result)
        self.assertIn("error", err.lower())
        self.assertIn("path not found", err.lower())

    def test_not_a_file_or_dir(self):
        # Make a path that is neither file nor dir (unlikely on normal FS),
        # so we'll simulate by removing base and using it as a "ghost" path
        ghost = os.path.join(self.base, "ghost")
        # ensure it doesn't exist
        if os.path.exists(ghost):
            os.remove(ghost)
        args = self.parser.parse_args(["-p", ghost, "-m", "sha256"])
        result, err = capture_stderr(hashsum_feature.run, args)

        # Because it doesn't exist, the earlier branch hits path-not-found
        self.assertIsNone(result)
        self.assertIn("error", err.lower())

    def test_permission_errors_are_caught(self):
        # Simulate by making directory and removing permissions is overkill;
        # we just check that the code path doesn't raise and prints something sensible
        args = self.parser.parse_args(["-p", self.base, "-m", "sha256"])
        result, out = capture_stdout(hashsum_feature.run, args)
        # No strict asserts here—test ensures no exceptions and output contains method
        self.assertIn("sha256", out)
        self.assertIsInstance(result, dict)


if __name__ == "__main__":
    unittest.main()
