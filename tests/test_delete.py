import unittest
import os
import shutil
import argparse
from features import delete

class TestDelete(unittest.TestCase):
    def setUp(self):
        """Preparing for test"""
        self.test_dir = 'tests/data_delete'
        os.makedirs(self.test_dir, exist_ok=True)

        self.file_path = os.path.join(self.test_dir, 'file1.txt')
        with open(self.file_path, 'w') as f:
            f.write('Test file 1')

        self.subdir = os.path.join(self.test_dir, 'subfolder')
        os.makedirs(self.subdir, exist_ok=True)
        with open(os.path.join(self.subdir, 'file2.txt'), 'w') as f:
            f.write('Test file 2')

        # Emulate manager.py
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-s', '--src', required=True)

    def tearDown(self):
        """Clean up test folders"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_delete_file(self):
        """Check delete file"""
        args = self.parser.parse_args(['-s', self.file_path])
        delete.run(args)
        self.assertFalse(os.path.exists(self.file_path))

    def test_delete_directory(self):
        """Check delete directory"""
        args = self.parser.parse_args(['-s', self.subdir])
        delete.run(args)
        self.assertFalse(os.path.exists(self.subdir))

    def test_delete_nonexistent(self):
        """Check delete nothing"""
        args = self.parser.parse_args(['-s', 'nonexistent_path'])
        with self.assertRaises(FileNotFoundError):
            delete.run(args)

if __name__ == '__main__':
    unittest.main()
