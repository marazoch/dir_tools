import unittest
import os
import shutil
import argparse
from features import rename as feat_rename


class TestRename(unittest.TestCase):
    def setUp(self):
        self.base = 'tests/data_rename'
        os.makedirs(self.base, exist_ok=True)
        self.src = os.path.join(self.base, 'a.txt')
        with open(self.src, 'w', encoding='utf-8') as f:
            f.write('hello')

        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-s', '--src', required=True)
        self.parser.add_argument('-n', '--name', required=True)

    def tearDown(self):
        if os.path.exists(self.base):
            shutil.rmtree(self.base)

    def test_rename_ok(self):
        args = self.parser.parse_args(['-s', self.src, '-n', 'b.txt'])
        new_path = feat_rename.run(args)
        self.assertTrue(os.path.exists(new_path))
        self.assertFalse(os.path.exists(self.src))

    def test_rename_conflict(self):
        conflict = os.path.join(self.base, 'b.txt')
        with open(conflict, 'w', encoding='utf-8') as f:
            f.write('x')
        with self.assertRaises(FileExistsError):
            args = self.parser.parse_args(['-s', self.src, '-n', 'b.txt'])
            feat_rename.run(args)

    def test_rename_invalid(self):
        with self.assertRaises(ValueError):
            args = self.parser.parse_args(['-s', self.src, '-n', 'bad/name.txt'])
            feat_rename.run(args)

    def test_rename_missing(self):
        with self.assertRaises(FileNotFoundError):
            args = self.parser.parse_args(['-s', os.path.join(self.base, 'missing.txt'), '-n', 'b.txt'])
            feat_rename.run(args)


if __name__ == '__main__':
    unittest.main()
