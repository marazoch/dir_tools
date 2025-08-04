import unittest
import os
import shutil
import argparse
from features import copy as copy_feature


class TestCopyCommand(unittest.TestCase):
    def setUp(self):
        # Preparing for test
        self.test_dir = 'tests/data'
        self.src_file = os.path.join(self.test_dir, 'example.txt')
        self.dst_dir = self.test_dir  # та же папка
        self.dst_file = os.path.join(self.dst_dir, 'example.txt')
        self.copy_file = os.path.join(self.dst_dir, 'copy_example.txt')

        os.makedirs(self.test_dir, exist_ok=True)

        with open(self.src_file, 'w') as f:
            f.write('Hello, world!')

        # Emulate manager.py
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-s', '--src', required=True)
        self.parser.add_argument('-d', '--dst', required=True)

    def tearDown(self):
        # Clean up test folders
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_copy_to_other_folder(self):
        other_dir = os.path.join(self.test_dir, 'copy_target')
        os.makedirs(other_dir, exist_ok=True)
        args = self.parser.parse_args(['-s', self.src_file, '-d', other_dir])

        copy_feature.run(args)

        expected_path = os.path.join(other_dir, 'example.txt')
        self.assertTrue(os.path.exists(expected_path))

        with open(expected_path, 'r') as f:
            self.assertEqual(f.read(), 'Hello, world!')

    def test_copy_to_same_folder_renamed(self):
        # Create same file in dst folder
        with open(self.dst_file, 'w') as f:
            f.write('Hello, world!')

        # Testing copy in the same folder
        args = self.parser.parse_args(['-s', self.src_file, '-d', self.dst_dir])
        copy_feature.run(args)

        self.assertTrue(os.path.exists(self.copy_file))

        with open(self.copy_file, 'r') as f:
            self.assertEqual(f.read(), 'Hello, world!')


if __name__ == '__main__':
    unittest.main()
