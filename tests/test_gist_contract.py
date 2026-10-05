"""公開Gistと同じ単独テストをリポジトリのCIでも実行する。"""

from pathlib import Path
import subprocess
import sys
import unittest


class PublishedSearchContractTests(unittest.TestCase):
    def test_standalone_contract_suite(self):
        folder = Path(__file__).resolve().parents[1] / "examples" / "03-ai-workflow"
        result = subprocess.run([sys.executable, "test_contract.py"], cwd=folder,
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "8 tests passed; exhaustive contract: 1764 cases\n")
        self.assertEqual(result.stderr, "")


class PublishedLearningContractTests(unittest.TestCase):
    def test_standalone_learning_suite(self):
        folder = Path(__file__).resolve().parents[1] / "examples" / "03-ai-workflow"
        result = subprocess.run([sys.executable, "test_highest.py"], cwd=folder,
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "10 tests passed; highest: 3906 integer lists\n")
        self.assertEqual(result.stderr, "")
