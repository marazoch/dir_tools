import unittest
import os
import sys
import shutil
import subprocess


class TestAnalyseCommand(unittest.TestCase):

    def setUp(self):
        """Preparing for test"""
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.test_dir = os.path.join(self.project_root, 'test_analyse_dir')
        os.makedirs(self.test_dir, exist_ok=True)

        for i in range(3):
            with open(os.path.join(self.test_dir, f'file{i}.txt'), 'w') as f:
                f.write(f'Test file {i}')

    def tearDown(self):
        """Clean up test folders"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_analyse_command(self):
        """Check analyse feature"""
        manager_path = os.path.join(self.project_root, 'manager.py')
        python_executable = sys.executable

        result = subprocess.run(
            [python_executable, manager_path, 'analyse', '-p', self.test_dir],
            capture_output=True,
            text=True,
            cwd=self.project_root
        )

        self.assertEqual(result.returncode, 0, msg=f'Error: {result.stderr}')
        self.assertIn('file0.txt', result.stdout)
        self.assertIn('file1.txt', result.stdout)
        self.assertIn('file2.txt', result.stdout)


if __name__ == '__main__':
    unittest.main()
