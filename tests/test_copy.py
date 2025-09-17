import unittest
import os
import shutil
import argparse
from io import StringIO
from features import copy as copy_feature


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


class TestCopyCommand(unittest.TestCase):
    def setUp(self):
        """Preparing for test"""
        self.test_dir = 'tests/data_copy'
        self.src_file = os.path.join(self.test_dir, 'example.txt')
        self.dst_dir = os.path.join(self.test_dir, 'dst')
        os.makedirs(self.test_dir, exist_ok=True)
        os.makedirs(self.dst_dir, exist_ok=True)

        with open(self.src_file, 'w', encoding='utf-8') as f:
            f.write('Hello, world!')

        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-s', '--src', required=True)
        self.parser.add_argument('-d', '--dst', required=True)

    def tearDown(self):
        """Clean up test folders"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_copy_to_other_folder(self):
        """Copy file to another (empty) folder"""
        args = self.parser.parse_args(['-s', self.src_file, '-d', self.dst_dir])

        result_path, out = capture_stdout(copy_feature.run, args)

        expected_path = os.path.join(self.dst_dir, 'example.txt')
        self.assertTrue(os.path.exists(expected_path))
        self.assertEqual(os.path.abspath(expected_path), result_path)
        self.assertIn('Copied:', out)

        with open(expected_path, 'r', encoding='utf-8') as f:
            self.assertEqual(f.read(), 'Hello, world!')

    def test_copy_to_same_folder_renamed(self):
        """If same name exists, create copy_<name> (or copy_(n)_<name>)"""
        conflict_path = os.path.join(self.dst_dir, 'example.txt')
        with open(conflict_path, 'w', encoding='utf-8') as f:
            f.write('Existing')

        args = self.parser.parse_args(['-s', self.src_file, '-d', self.dst_dir])
        result_path, out = capture_stdout(copy_feature.run, args)

        # Should create a new non-colliding name
        self.assertIsNotNone(result_path)
        self.assertTrue(os.path.exists(result_path))
        self.assertIn(os.path.basename(result_path), os.listdir(self.dst_dir))
        self.assertIn('Copied:', out)
        with open(result_path, 'r', encoding='utf-8') as f:
            self.assertEqual(f.read(), 'Hello, world!')

    def test_copy_nonexistent_source(self):
        """Nonexistent src: return None and emit error to stderr"""
        missing = os.path.join(self.test_dir, 'no_such_file.txt')
        args = self.parser.parse_args(['-s', missing, '-d', self.dst_dir])

        result, err = capture_stderr(copy_feature.run, args)

        self.assertIsNone(result)
        self.assertIn('error', err.lower())
        self.assertIn('source path not found', err.lower())

    def test_copy_when_dst_is_not_directory(self):
        """Destination is not a directory -> error"""
        not_dir = os.path.join(self.test_dir, 'not_a_dir.txt')
        with open(not_dir, 'w', encoding='utf-8') as f:
            f.write('x')

        args = self.parser.parse_args(['-s', self.src_file, '-d', not_dir])
        result, err = capture_stderr(copy_feature.run, args)

        self.assertIsNone(result)
        self.assertIn('error', err.lower())
        self.assertIn('destination is not a directory', err.lower())


if __name__ == '__main__':
    unittest.main()
