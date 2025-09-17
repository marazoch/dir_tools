import unittest
import os
import sys
import shutil
import subprocess
import re


class TestCLI(unittest.TestCase):
    def setUp(self):
        """Preparing for test"""
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.test_dir = os.path.join(self.project_root, 'test_cli_dir')
        os.makedirs(self.test_dir, exist_ok=True)

        for i in range(3):
            with open(os.path.join(self.test_dir, f'file{i}.txt'), 'w', encoding='utf-8') as f:
                f.write(f'Test file {i}')

    def tearDown(self):
        """Clean up test folders"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def run_command(self, args):
        """Run manager.py with args and return CompletedProcess"""
        manager_path = os.path.join(self.project_root, 'manager.py')
        return subprocess.run(
            [sys.executable, manager_path] + args,
            capture_output=True,
            text=True,
            cwd=self.project_root
        )

    # ---- helpers for tolerant matching ----
    @staticmethod
    def has_any(haystack: str, *needles: str) -> bool:
        s = haystack.lower()
        return any(n.lower() in s for n in needles)

    @staticmethod
    def sha_line_present(stdout: str, method: str, path_tail: str) -> bool:
        """
        Accept both formats:
          - 'sha256(<path>) = <hex>'
          - 'sha256  <hex>  <path>'
        and path match by tail (file name).
        """
        method = method.lower()
        for line in stdout.splitlines():
            ll = line.lower()
            if method not in ll:
                continue
            if path_tail.lower() not in ll:
                continue
            # must contain a hex digest (32 for md5, 64 for sha256)
            hexes = re.findall(r'\b[a-f0-9]{32,64}\b', ll)
            if hexes:
                return True
        return False

    # --------------------------------------

    def test_copy(self):
        dst_dir = os.path.join(self.test_dir, 'copy_dst')
        os.makedirs(dst_dir, exist_ok=True)

        src_file = os.path.abspath(os.path.join(self.test_dir, 'file0.txt'))
        dst_dir_abs = os.path.abspath(dst_dir)

        result = self.run_command(['copy', '-s', src_file, '-d', dst_dir_abs])
        self.assertEqual(result.returncode, 0, msg=result.stderr)

        expected_file = os.path.join(dst_dir_abs, 'file0.txt')
        self.assertTrue(os.path.exists(expected_file))

    def test_count(self):
        abs_test_dir = os.path.abspath(self.test_dir)
        result = self.run_command(['count', '-p', abs_test_dir])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(self.has_any(result.stdout, 'Total files in', 'Total files:'))

    def test_delete(self):
        file_to_delete = os.path.abspath(os.path.join(self.test_dir, 'file1.txt'))
        result = self.run_command(['delete', '-s', file_to_delete])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertFalse(os.path.exists(file_to_delete))

    def test_find(self):
        abs_test_dir = os.path.abspath(self.test_dir)
        result = self.run_command(['find', '-p', abs_test_dir, '-r', r'file[0-9]+\.txt'])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn('file0.txt', result.stdout)
        self.assertIn('file1.txt', result.stdout)

    def test_move(self):
        dst_dir = os.path.join(self.test_dir, 'move_dst')
        os.makedirs(dst_dir, exist_ok=True)

        src_file = os.path.abspath(os.path.join(self.test_dir, 'file2.txt'))
        dst_dir_abs = os.path.abspath(dst_dir)

        result = self.run_command(['move', '-s', src_file, '-d', dst_dir_abs])
        self.assertEqual(result.returncode, 0, msg=result.stderr)

        expected_file = os.path.join(dst_dir_abs, 'file2.txt')
        self.assertTrue(os.path.exists(expected_file))
        self.assertFalse(os.path.exists(src_file))

    def test_add_date(self):
        file_path = os.path.abspath(os.path.join(self.test_dir, 'file0.txt'))
        result = self.run_command(['add_date', '-p', file_path])
        self.assertEqual(result.returncode, 0, msg=result.stderr)

        # Accept both naming schemes:
        #   YYYY-MM-DD_file0.txt   (date prefix)
        #   file0_YYYY-MM-DD.txt   (date suffix before extension)
        files = os.listdir(os.path.dirname(file_path))
        patt_prefix = re.compile(r'^\d{4}-\d{2}-\d{2}_file0\.txt$', re.IGNORECASE)
        patt_suffix = re.compile(r'^file0_\d{4}-\d{2}-\d{2}\.txt$', re.IGNORECASE)

        matched = [f for f in files if patt_prefix.match(f) or patt_suffix.match(f)]
        self.assertTrue(len(matched) > 0, msg=f'No dated file found; files: {files}')

    def test_analyse(self):
        abs_test_dir = os.path.abspath(self.test_dir)
        result = self.run_command(['analyse', '-p', abs_test_dir])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn('full size:', result.stdout.lower())
        self.assertTrue(self.has_any(result.stdout, 'file0.txt'))

    def test_hashsum_file(self):
        file_path = os.path.abspath(os.path.join(self.test_dir, 'file0.txt'))
        result = self.run_command(['hashsum', '-p', file_path, '-m', 'sha256'])
        self.assertEqual(result.returncode, 0, msg=result.stderr)

        # Accept both formats
        self.assertTrue(
            self.sha_line_present(result.stdout, 'sha256', 'file0.txt'),
            msg=f'Unexpected hashsum output:\n{result.stdout}'
        )
        # Extract a sha256-length digest from output and check length = 64
        m = re.search(r'\b[a-f0-9]{64}\b', result.stdout.lower())
        self.assertIsNotNone(m, msg=f'No sha256 digest in output:\n{result.stdout}')

    def test_hashsum_directory(self):
        abs_test_dir = os.path.abspath(self.test_dir)
        result = self.run_command(['hashsum', '-p', abs_test_dir, '-m', 'md5'])
        self.assertEqual(result.returncode, 0, msg=result.stderr)

        # Accept both formats per-file, just check at least one line matches and mentions a test file
        ok_any = (
            self.sha_line_present(result.stdout, 'md5', 'file0.txt') or
            self.sha_line_present(result.stdout, 'md5', 'file1.txt') or
            self.sha_line_present(result.stdout, 'md5', 'file2.txt')
        )
        self.assertTrue(ok_any, msg=f'Unexpected md5 output:\n{result.stdout}')
        # md5 hex length is 32; ensure at least one appears
        m = re.search(r'\b[a-f0-9]{32}\b', result.stdout.lower())
        self.assertIsNotNone(m, msg=f'No md5 digest in output:\n{result.stdout}')

    def test_duplicates(self):
        file1 = os.path.abspath(os.path.join(self.test_dir, 'dup1.txt'))
        file2 = os.path.abspath(os.path.join(self.test_dir, 'dup2.txt'))

        content = 'duplicate content for testing'
        with open(file1, 'w', encoding='utf-8') as f:
            f.write(content)
        with open(file2, 'w', encoding='utf-8') as f:
            f.write(content)

        result = self.run_command(['duplicates', '-p', os.path.abspath(self.test_dir)])
        self.assertEqual(result.returncode, 0, msg=result.stderr)

        # Accept both group headers
        self.assertTrue(
            self.has_any(result.stdout, 'Duplicate files', 'Duplicate group #'),
            msg=f'Unexpected duplicates header:\n{result.stdout}'
        )
        self.assertIn('dup1.txt', result.stdout)
        self.assertIn('dup2.txt', result.stdout)


if __name__ == '__main__':
    unittest.main()
