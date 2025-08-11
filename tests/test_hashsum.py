import unittest
import os
import shutil
import argparse
import sys

from features import hashsum


class OutputCapture:
    """A class to capture stdout output"""
    def __init__(self):
        self.output = ''

    def write(self, s):
        self.output += s


class TestHashSum(unittest.TestCase):
    def setUp(self):
        """Preparing for test"""
        self.test_dir = 'test_hash_sum_dir'
        os.makedirs(self.test_dir, exist_ok=True)
        with open(os.path.join(self.test_dir, 'file.txt'), 'w') as f:
            f.write('Hello World!')

        parser = argparse.ArgumentParser()
        parser.add_argument('-p', '--path', required=True)
        parser.add_argument('-m', '--method', choices=['sha256', 'md5'], default='sha256')
        self.parser = parser

    def tearDown(self):
        """Clean up test folders"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_hash_file_sha256(self):
        """Check collecting hashsum of file with sha256"""
        args = self.parser.parse_args(['-p', os.path.join(self.test_dir, 'file.txt'), '-m', 'sha256'])
        capture = OutputCapture()
        original_stdout = sys.stdout

        try:
            sys.stdout = capture
            hashsum.run(args)
        finally:
            sys.stdout = original_stdout

        self.assertIn('sha256', capture.output.lower())
        self.assertIn('file.txt', capture.output)

    def test_hash_dir_md5(self):
        """Check collecting hashsum of file with md5"""
        args = self.parser.parse_args(['-p', self.test_dir, '-m', 'md5'])
        capture = OutputCapture()
        original_stdout = sys.stdout

        try:
            sys.stdout = capture
            hashsum.run(args)
        finally:
            sys.stdout = original_stdout

        self.assertIn('md5', capture.output.lower())
        self.assertIn('file.txt', capture.output)


if __name__ == '__main__':
    unittest.main()
