import unittest
import os
import shutil
import subprocess

class TestAnalyseCommand(unittest.TestCase):

    def setUp(self):
        """Preparing for test"""
        self.test_dir = 'test_analyse_dir'
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
        result = subprocess.run(
            ['python', 'C:\\file_manager\\dir_tools\\manager.py', 'analyse', '-p', self.test_dir],
            capture_output=True,
            text=True
        )

        self.assertEqual(result.returncode, 0, msg=f'Error: {result.stderr}')
        self.assertIn('file0.txt', result.stdout)
        self.assertIn('file1.txt', result.stdout)
        self.assertIn('file2.txt', result.stdout)


if __name__ == "__main__":
    unittest.main()
