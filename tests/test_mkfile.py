import unittest
import os
import shutil
import argparse
from features import mkfile as feat_mkfile


class TestMkfile(unittest.TestCase):
    def setUp(self):
        self.base = 'tests/data_mkfile'
        os.makedirs(self.base, exist_ok=True)
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-p', '--path', required=True)
        self.parser.add_argument('-n', '--name', required=True)

    def tearDown(self):
        if os.path.exists(self.base):
            shutil.rmtree(self.base)

    def test_create_file_ok(self):
        args = self.parser.parse_args(['-p', self.base, '-n', 'new.txt'])
        target = feat_mkfile.run(args)
        self.assertTrue(os.path.exists(target))
        with open(target, 'r', encoding='utf-8') as f:
            self.assertEqual(f.read(), '')

    def test_conflict(self):
        existing = os.path.join(self.base, 'exists.txt')
        with open(existing, 'w', encoding='utf-8'):
            pass
        with self.assertRaises(FileExistsError):
            args = self.parser.parse_args(['-p', self.base, '-n', 'exists.txt'])
            feat_mkfile.run(args)

    def test_bad_base(self):
        with self.assertRaises(FileNotFoundError):
            args = self.parser.parse_args(['-p', os.path.join(self.base, 'nope'), '-n', 'x.txt'])
            feat_mkfile.run(args)

    def test_not_a_dir(self):
        not_dir = os.path.join(self.base, 'file.txt')
        with open(not_dir, 'w', encoding='utf-8'):
            pass
        with self.assertRaises(NotADirectoryError):
            args = self.parser.parse_args(['-p', not_dir, '-n', 'x.txt'])
            feat_mkfile.run(args)


if __name__ == '__main__':
    unittest.main()
