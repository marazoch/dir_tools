import unittest
import os
import shutil
import argparse
from io import StringIO
from features import add_date as add_date_feature


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


class TestAddDate(unittest.TestCase):
    def setUp(self):
        self.base = "tests/data_add_date"
        os.makedirs(self.base, exist_ok=True)

        # base/a.txt
        self.a = os.path.join(self.base, "a.txt")
        with open(self.a, "w", encoding="utf-8") as f:
            f.write("A")

        # base/sub/b.txt
        self.sub = os.path.join(self.base, "sub")
        os.makedirs(self.sub, exist_ok=True)
        self.b = os.path.join(self.sub, "b.txt")
        with open(self.b, "w", encoding="utf-8") as f:
            f.write("B")

        # emulate manager.py
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-p", "--path", required=True)
        self.parser.add_argument("-r", "--recursive", action="store_true")

    def tearDown(self):
        if os.path.exists(self.base):
            shutil.rmtree(self.base, ignore_errors=True)

    @staticmethod
    def _expected_new_name_for_existing(path: str) -> str:
        """
        Build expected 'name_YYYY-MM-DD.ext' using current file's *existing* ctime.
        IMPORTANT: call this BEFORE the file is renamed.
        """
        from datetime import datetime
        ctime = os.path.getctime(path)  # path must exist!
        date_str = datetime.fromtimestamp(ctime).strftime("%Y-%m-%d")
        name, ext = os.path.splitext(os.path.basename(path))
        return f"{name}_{date_str}{ext}"

    def test_single_file(self):
        """When path is a file, rename only that file."""
        expected_name = self._expected_new_name_for_existing(self.a)  # compute BEFORE run
        expected_path = os.path.join(self.base, expected_name)

        args = self.parser.parse_args(["-p", self.a])
        renamed, out = capture_stdout(add_date_feature.run, args)

        self.assertTrue(os.path.exists(expected_path))
        self.assertFalse(os.path.exists(self.a))
        self.assertIsInstance(renamed, list)
        self.assertIn(expected_path, renamed)
        self.assertIn("Renamed:", out)
        self.assertIn("Processed:", out)

    def test_directory_non_recursive(self):
        """Directory without --recursive: rename only top-level files (a.txt)."""
        expected_a = os.path.join(self.base, self._expected_new_name_for_existing(self.a))  # BEFORE run

        args = self.parser.parse_args(["-p", self.base])
        renamed, out = capture_stdout(add_date_feature.run, args)

        # 'a.txt' must be renamed; 'sub/b.txt' untouched
        self.assertTrue(os.path.exists(expected_a))
        self.assertTrue(os.path.exists(self.b))
        self.assertIn(expected_a, renamed)
        # b.txt not renamed, поэтому среди renamed его быть не должно
        self.assertTrue(all("b.txt" not in p for p in renamed))
        self.assertIn("Processed:", out)

    def test_directory_recursive_isolated(self):
        """Directory with --recursive: rename files in subdirectories too (isolated)."""
        # создаём изолированную структуру, чтобы не зависеть от других тестов
        base2 = os.path.join(self.base, "iso")
        os.makedirs(base2, exist_ok=True)
        a2 = os.path.join(base2, "a2.txt")
        with open(a2, "w", encoding="utf-8") as f:
            f.write("A2")
        sub2 = os.path.join(base2, "sub2")
        os.makedirs(sub2, exist_ok=True)
        b2 = os.path.join(sub2, "b2.txt")
        with open(b2, "w", encoding="utf-8") as f:
            f.write("B2")

        expected_a2 = os.path.join(base2, self._expected_new_name_for_existing(a2))
        expected_b2 = os.path.join(sub2, self._expected_new_name_for_existing(b2))

        parser2 = argparse.ArgumentParser()
        parser2.add_argument("-p", "--path", required=True)
        parser2.add_argument("-r", "--recursive", action="store_true")
        args = parser2.parse_args(["-p", base2, "-r"])

        renamed, out = capture_stdout(add_date_feature.run, args)

        self.assertTrue(os.path.exists(expected_a2))
        self.assertTrue(os.path.exists(expected_b2))
        self.assertIn(expected_a2, renamed)
        self.assertIn(expected_b2, renamed)
        self.assertIn("Processed:", out)

    def test_skip_if_already_has_date(self):
        """If filename already contains date string, skip on second run."""
        # 1) rename once
        expected_name = self._expected_new_name_for_existing(self.a)
        expected_path = os.path.join(self.base, expected_name)
        args = self.parser.parse_args(["-p", self.a])
        renamed1, out1 = capture_stdout(add_date_feature.run, args)
        self.assertTrue(os.path.exists(expected_path))
        self.assertIn(expected_path, renamed1)

        # 2) run again on the *new* path -> should skip
        args2 = self.parser.parse_args(["-p", expected_path])
        renamed2, out2 = capture_stdout(add_date_feature.run, args2)

        self.assertEqual(renamed2, [])
        self.assertIn("Skipping (already contains date)", out2)

    def test_target_exists_conflict(self):
        """If target name already exists, print error and keep original."""
        # Create conflict target beforehand
        conflict_name = self._expected_new_name_for_existing(self.a)
        conflict_path = os.path.join(self.base, conflict_name)
        with open(conflict_path, "w", encoding="utf-8") as f:
            f.write("C")

        args = self.parser.parse_args(["-p", self.a])
        renamed, err = capture_stderr(add_date_feature.run, args)

        # Original should remain, conflict target should remain
        self.assertTrue(os.path.exists(self.a))
        self.assertTrue(os.path.exists(conflict_path))
        self.assertEqual(renamed, [])
        self.assertIn("target already exists", err.lower())


if __name__ == "__main__":
    unittest.main()
