import unittest
import os
import shutil
import argparse
from features import mkdir as feat_mkdir


class TestMkdir(unittest.TestCase):
    def setUp(self):
        self.base = 'tests/data_mkdir'
        os.makedirs(self.base, exist_ok=True)
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-p', '--path', required=True)
        self.parser.add_argument('-n', '--name', required=True)

    def tearDown(self):
        if os.path.exists(self.base):
            shutil.rmtree(self.base)

    def test_create_dir_ok(self):
        args = self.parser.parse_args(['-p', self.base, '-n', 'newdir'])
        target = feat_mkdir.run(args)
        self.assertTrue(os.path.isdir(target))

    def test_conflict(self):
        conflict = os.path.join(self.base, 'exists')
        os.makedirs(conflict, exist_ok=True)
        with self.assertRaises(FileExistsError):
            args = self.parser.parse_args(['-p', self.base, '-n', 'exists'])
            feat_mkdir.run(args)

    def test_bad_base(self):
        with self.assertRaises(FileNotFoundError):
            args = self.parser.parse_args(['-p', os.path.join(self.base, 'nope'), '-n', 'x'])
            feat_mkdir.run(args)

    def test_not_a_dir(self):
        not_dir = os.path.join(self.base, 'file.txt')
        with open(not_dir, 'w', encoding='utf-8'):
            pass
        with self.assertRaises(NotADirectoryError):
            args = self.parser.parse_args(['-p', not_dir, '-n', 'x'])
            feat_mkdir.run(args)


if __name__ == '__main__':
    unittest.main()
