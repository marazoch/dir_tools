import unittest
import os
import shutil
import datetime
from argparse import Namespace
from features import add_date


class TestAddDate(unittest.TestCase):
    def setUp(self):
        """Preparing for test"""
        self.test_dir = 'test_add_date_dir'
        os.makedirs(self.test_dir, exist_ok=True)

        self.file_path = os.path.join(self.test_dir, 'example.txt')
        with open(self.file_path, 'w') as f:
            f.write('Hello World')

        self.creation_date = datetime.datetime.fromtimestamp(
            os.path.getctime(self.file_path)
        ).strftime("%Y-%m-%d")

    def tearDown(self):
        """Clean up test folders"""
        shutil.rmtree(self.test_dir)

    def test_add_date_to_single_file(self):
        """Check that file renamed with date"""
        args = Namespace(path=self.file_path, recursive=False)
        add_date.run(args)

        expected_name = f'{self.creation_date}_example.txt'
        expected_path = os.path.join(self.test_dir, expected_name)
        self.assertTrue(os.path.exists(expected_path))

    def test_add_date_in_folder(self):
        """Check that all files renamed"""
        args = Namespace(path=self.test_dir, recursive=False)
        add_date.run(args)

        files = os.listdir(self.test_dir)
        for filename in files:
            self.assertIn(self.creation_date, filename)

    def test_recursive_add_date(self):
        """Check recursive renaming"""
        subfolder = os.path.join(self.test_dir, 'sub')
        os.makedirs(subfolder, exist_ok=True)

        nested_file = os.path.join(subfolder, 'nested.txt')
        with open(nested_file, 'w') as f:
            f.write('Nested file')

        args = Namespace(path=self.test_dir, recursive=True)
        add_date.run(args)

        all_files = []
        for root, _, files in os.walk(self.test_dir):
            all_files.extend(files)

        for filename in all_files:
            self.assertIn(self.creation_date, filename)


if __name__ == '__main__':
    unittest.main()
