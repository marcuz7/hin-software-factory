import tempfile
import unittest
from pathlib import Path
from hin_p0.core import Factory
from hin_p0.spec import scaffold

class FactoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.factory = Factory(Path(self.temp.name) / "tasks.db")

    def tearDown(self):
        self.factory.close()
        self.temp.cleanup()

    def test_dependency_and_review_gate(self):
        a = self.factory.add("ithaca", "spec")
        b = self.factory.add("ithaca", "implementation", [a])
        with self.assertRaises(ValueError):
            self.factory.claim(b, "worker")
        self.factory.claim(a, "worker")
        self.factory.submit(a, "worker", ["test evidence"])
        with self.assertRaises(ValueError):
            self.factory.approve(a, "worker")
        self.factory.approve(a, "reviewer")
        self.assertEqual(self.factory._row(b)["status"], "READY")

    def test_expired_worker_cannot_submit(self):
        task = self.factory.add("ithaca", "test")
        self.factory.claim(task, "worker", ttl=0.000001)
        import time
        time.sleep(.003)
        with self.assertRaises(ValueError):
            self.factory.submit(task, "worker", ["fake evidence"])
        self.assertEqual(self.factory.expire(), 1)

    def test_scaffold_nonoverwrite(self):
        source = Path(self.temp.name) / "PRD.md"
        source.write_text("# Verified PRD", encoding="utf-8")
        folder = Path(self.temp.name) / "out"
        self.assertEqual(len(scaffold(source, folder)), 4)
        with self.assertRaises(FileExistsError):
            scaffold(source, folder)

if __name__ == "__main__":
    unittest.main()
