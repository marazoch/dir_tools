import unittest
import os
import shutil
import argparse
from features import find

class TestFind(unittest.TestCase):
    def setUp(self):
        """Preparing for test"""
        self.test_dir = 'test_find_argparse'
        os.makedirs(os.path.join(self.test_dir, 'subdir'), exist_ok=True)

        with open(os.path.join(self.test_dir, 'a.txt'), 'w') as f:
            f.write('abc')

        with open(os.path.join(self.test_dir, 'b.md'), 'w') as f:
            f.write('markdown')

        with open(os.path.join(self.test_dir, 'subdir', 'c.txt'), 'w') as f:
            f.write('nested')

        # Emulate manager.py
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('path')
        self.parser.add_argument('regex')

    def tearDown(self):
        """Clean up test folders"""
        shutil.rmtree(self.test_dir)

    def test_find_txt_files(self):
        """Check file finding .txt"""
        args = self.parser.parse_args([self.test_dir, r'.*\.txt$'])
        result = find.run(args)
        basenames = [os.path.basename(path) for path in result]
        self.assertIn('a.txt', basenames)
        self.assertIn('c.txt', basenames)
        self.assertNotIn('b.md', basenames)

    def test_find_md_files(self):
        """Check file finding .md"""
        args = self.parser.parse_args([self.test_dir, r'.*\.md$'])
        result = find.run(args)
        basenames = [os.path.basename(path) for path in result]
        self.assertIn('b.md', basenames)
        self.assertNotIn('a.txt', basenames)

    def test_invalid_path(self):
        """Check file finding with invalid path"""
        args = self.parser.parse_args(['nonexistent', r'.*\.txt$'])
        with self.assertRaises(FileNotFoundError):
            find.run(args)

    def test_invalid_regex(self):
        """Check file finding with invalid regex"""
        args = self.parser.parse_args([self.test_dir, r'*invalid['])
        with self.assertRaises(ValueError):
            find.run(args)

if __name__ == '__main__':
    unittest.main()
