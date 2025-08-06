import os
import shutil
import unittest
import argparse

from features import move

class TestMove(unittest.TestCase):

    def setUp(self):
        """Preparing for test"""
        os.makedirs('test_src_dir', exist_ok=True)
        os.makedirs('test_dst_dir', exist_ok=True)

        with open('test_src_dir/test_file.txt', 'w') as f:
            f.write('test content')

    def tearDown(self):
        """Clean up test folders"""
        if os.path.exists('test_src_dir'):
            shutil.rmtree('test_src_dir')
        if os.path.exists('test_dst_dir'):
            shutil.rmtree('test_dst_dir')

    def test_successful_move(self):
        """Check file moving"""
        # Emulate manger.py
        parser = argparse.ArgumentParser()
        parser.add_argument('--src')
        parser.add_argument('--dst')
        args = parser.parse_args(['--src', 'test_src_dir/test_file.txt', '--dst', 'test_dst_dir'])

        move.run(args)

        # check that file moved
        self.assertFalse(os.path.exists('test_src_dir/test_file.txt'))
        self.assertTrue(os.path.exists('test_dst_dir/test_file.txt'))

    def test_move_file_already_exists(self):
        """Check move when file already exists"""
        # Preparing for test (existed file)
        with open('test_dst_dir/test_file.txt', 'w') as f:
            f.write('existing')

        # Emulate manger.py
        parser = argparse.ArgumentParser()
        parser.add_argument('--src')
        parser.add_argument('--dst')
        args = parser.parse_args(['--src', 'test_src_dir/test_file.txt', '--dst', 'test_dst_dir'])

        with self.assertRaises(FileExistsError):
            move.run(args)

    def test_move_to_same_folder(self):
        """Check move same folder"""
        # Preparing for test with same folder
        parser = argparse.ArgumentParser()
        parser.add_argument('--src')
        parser.add_argument('--dst')
        args = parser.parse_args(['--src', 'test_src_dir/test_file.txt', '--dst', 'test_src_dir'])

        with self.assertRaises(FileExistsError):
            move.run(args)

    def test_source_not_found(self):
        """Check move none existing file"""
        parser = argparse.ArgumentParser()
        parser.add_argument('--src')
        parser.add_argument('--dst')
        args = parser.parse_args(['--src', 'not_exists.txt', '--dst', 'test_dst_dir'])

        with self.assertRaises(FileNotFoundError):
            move.run(args)

    def test_destination_not_folder(self):
        """Check move when destination not a directory"""
        # Preparing for test (not a folder dst)
        with open('not_a_folder.txt', 'w') as f:
            f.write('not a folder')

        parser = argparse.ArgumentParser()
        parser.add_argument('--src')
        parser.add_argument('--dst')
        args = parser.parse_args(['--src', 'test_src_dir/test_file.txt', '--dst', 'not_a_folder.txt'])

        with self.assertRaises(NotADirectoryError):
            move.run(args)

        os.remove('not_a_folder.txt')


if __name__ == '__main__':
    unittest.main()
