import unittest
import os
import shutil
import argparse
import sys

from features import duplicates


class OutputCapture:
    """A class to capture stdout output"""

    def __init__(self):
        self.output = ''

    def write(self, s):
        self.output += s


class TestDuplicates(unittest.TestCase):
    def setUp(self):
        """Preparing for test"""
        self.test_dir = 'test_duplicates_dir'
        os.makedirs(self.test_dir, exist_ok=True)
        content = 'Duplicate file content'
        for filename in ['file1.txt', 'file2.txt', 'unique.txt']:
            with open(os.path.join(self.test_dir, filename), 'w') as f:
                if 'unique' in filename:
                    f.write('Unique content')
                else:
                    f.write(content)

        parser = argparse.ArgumentParser()
        parser.add_argument('-p', '--path', required=True)
        self.parser = parser

    def tearDown(self):
        """Clean up test folders"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_find_duplicates(self):
        """Check duplicates finder"""
        args = self.parser.parse_args(['-p', self.test_dir])
        capture = OutputCapture()
        original_stdout = sys.stdout

        try:
            sys.stdout = capture
            duplicates.run(args)
        finally:
            sys.stdout = original_stdout

        self.assertIn('Duplicate files', capture.output)
        self.assertIn('file1.txt', capture.output)
        self.assertIn('file2.txt', capture.output)
        self.assertNotIn('unique.txt\n  ', capture.output)


if __name__ == '__main__':
    unittest.main()
