import unittest
import os
import shutil
import argparse
from features import count

class TestCount(unittest.TestCase):
    def setUp(self):
        self.test_dir = 'tests/data_count'
        os.makedirs(self.test_dir, exist_ok=True)

        # Preparing for test
        with open(os.path.join(self.test_dir, 'file1.txt'), 'w') as f:
            f.write('Test file 1')
        with open(os.path.join(self.test_dir, 'file2.txt'), 'w') as f:
            f.write('Test file 2')

        subdir = os.path.join(self.test_dir, 'subfolder')
        os.makedirs(subdir, exist_ok=True)
        with open(os.path.join(subdir, 'file3.txt'), 'w') as f:
            f.write('Test file 3')

        # Emulate manager.py
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-p', '--path', required=True)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_count_files(self):
        args = self.parser.parse_args(['-p', self.test_dir])
        result = count.run(args)
        self.assertEqual(result, 3)

    def test_nonexistent_path(self):
        args = self.parser.parse_args(['-p', 'nonexistent_path'])
        with self.assertRaises(FileNotFoundError):
            count.run(args)

    def test_path_is_not_dir(self):
        file_path = os.path.join(self.test_dir, 'file1.txt')
        args = self.parser.parse_args(['-p', file_path])
        with self.assertRaises(NotADirectoryError):
            count.run(args)

if __name__ == '__main__':
    unittest.main()
