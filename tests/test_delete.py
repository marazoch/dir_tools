import unittest
import os
import shutil
import argparse
from io import StringIO
from features import delete


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


class TestDelete(unittest.TestCase):
    def setUp(self):
        """Preparing for test"""
        self.test_dir = 'tests/data_delete'
        os.makedirs(self.test_dir, exist_ok=True)

        self.file_path = os.path.join(self.test_dir, 'file1.txt')
        with open(self.file_path, 'w', encoding='utf-8') as f:
            f.write('Test file 1')

        self.subdir = os.path.join(self.test_dir, 'subfolder')
        os.makedirs(self.subdir, exist_ok=True)
        with open(os.path.join(self.subdir, 'file2.txt'), 'w', encoding='utf-8') as f:
            f.write('Test file 2')

        # Emulate manager.py
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-s', '--src', required=True)

    def tearDown(self):
        """Clean up test folders"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_delete_file(self):
        """Check delete file"""
        self.assertTrue(os.path.exists(self.file_path))
        args = self.parser.parse_args(['-s', self.file_path])

        ok, out = capture_stdout(delete.run, args)

        self.assertTrue(ok)
        self.assertFalse(os.path.exists(self.file_path))
        self.assertIn('Deleted:', out)  # функция печатает успешное сообщение

    def test_delete_directory(self):
        """Check delete directory (recursive)"""
        self.assertTrue(os.path.isdir(self.subdir))
        args = self.parser.parse_args(['-s', self.subdir])

        ok, out = capture_stdout(delete.run, args)

        self.assertTrue(ok)
        self.assertFalse(os.path.exists(self.subdir))
        self.assertIn('Deleted:', out)

    def test_delete_nonexistent(self):
        """Check delete nonexistent path -> no exception, False + stderr message"""
        missing = os.path.join(self.test_dir, 'nonexistent_path')
        self.assertFalse(os.path.exists(missing))

        args = self.parser.parse_args(['-s', missing])

        ok, err = capture_stderr(delete.run, args)

        self.assertFalse(ok)
        self.assertIn('Error', err)
        self.assertIn('path not found', err.lower())


if __name__ == '__main__':
    unittest.main()
