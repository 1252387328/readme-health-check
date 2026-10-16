import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(project):
    spec = importlib.util.spec_from_file_location(project.replace('-', '_'), ROOT / 'cli.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ProjectTests(unittest.TestCase):
    def test_all_help_and_invalid_arguments(self):
        for path in [ROOT / 'cli.py']:
            with self.subTest(project=path.parent.name):
                result = subprocess.run([sys.executable, str(path), '--help'], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                result = subprocess.run([sys.executable, str(path), '--not-a-real-option'], capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)
                self.assertNotIn('Traceback', result.stderr)

    def test_readme_empty_and_complete(self):
        module = load('readme-health-check')
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            self.assertEqual(module.inspect(folder)['passed'], 0)
            (folder / 'README.md').write_text('# Demo\nInstallation\nUsage\nContributing\n')
            (folder / 'LICENSE').write_text('Fixture only')
            self.assertEqual(module.inspect(folder)['passed'], 5)

if __name__ == '__main__':
    unittest.main()
