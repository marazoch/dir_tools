import unittest
import os
import sys
import shutil
import subprocess

class TestCLI(unittest.TestCase):
    def setUp(self):
        """Preparing for test"""
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.test_dir = os.path.join(self.project_root, 'test_cli_dir')
        os.makedirs(self.test_dir, exist_ok=True)

        for i in range(3):
            with open(os.path.join(self.test_dir, f'file{i}.txt'), 'w') as f:
                f.write(f'Test file {i}')

    def tearDown(self):
        """Clean up test folders"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def run_command(self, args):
        """Method for running manager.py with args"""
        manager_path = os.path.join(self.project_root, 'manager.py')
        result = subprocess.run(
            [sys.executable, manager_path] + args,
            capture_output=True,
            text=True,
            cwd=self.project_root
        )
        return result

    def test_copy(self):
        dst_dir = os.path.join(self.test_dir, 'copy_dst')
        os.makedirs(dst_dir, exist_ok=True)

        src_file = os.path.abspath(os.path.join(self.test_dir, 'file0.txt'))
        dst_dir_abs = os.path.abspath(dst_dir)

        args = ['copy', '-s', src_file, '-d', dst_dir_abs]

        result = self.run_command(args)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        expected_file = os.path.join(dst_dir_abs, 'file0.txt')
        self.assertTrue(os.path.exists(expected_file))

    def test_count(self):
        abs_test_dir = os.path.abspath(self.test_dir)
        args = ['count', '-p', abs_test_dir]

        result = self.run_command(args)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn('Total files in', result.stdout)

    def test_delete(self):
        file_to_delete = os.path.abspath(os.path.join(self.test_dir, 'file1.txt'))
        args = ['delete', '-s', file_to_delete]

        result = self.run_command(args)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertFalse(os.path.exists(file_to_delete))

    def test_find(self):
        abs_test_dir = os.path.abspath(self.test_dir)
        args = ['find', '-p', abs_test_dir, '-r', 'file[0-9]+\\.txt']

        result = self.run_command(args)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn('file0.txt', result.stdout)
        self.assertIn('file1.txt', result.stdout)

    def test_move(self):
        dst_dir = os.path.join(self.test_dir, 'move_dst')
        os.makedirs(dst_dir, exist_ok=True)

        src_file = os.path.abspath(os.path.join(self.test_dir, 'file2.txt'))
        dst_dir_abs = os.path.abspath(dst_dir)

        args = ['move', '-s', src_file, '-d', dst_dir_abs]

        result = self.run_command(args)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        expected_file = os.path.join(dst_dir_abs, 'file2.txt')
        self.assertTrue(os.path.exists(expected_file))
        self.assertFalse(os.path.exists(src_file))

    def test_add_date(self):
        file_path = os.path.abspath(os.path.join(self.test_dir, 'file0.txt'))
        args = ['add_date', '-p', file_path]

        result = self.run_command(args)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        files = os.listdir(os.path.dirname(file_path))
        date_prefixed_files = [f for f in files if f.endswith('file0.txt') and len(f) > len('file0.txt')]
        self.assertTrue(len(date_prefixed_files) > 0)

    def test_analyse(self):
        abs_test_dir = os.path.abspath(self.test_dir)
        args = ['analyse', '-p', abs_test_dir]

        result = self.run_command(args)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn('full size:', result.stdout)
        self.assertIn('file0.txt', result.stdout)

if __name__ == '__main__':
    unittest.main()
