import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from fde_accel.mapping import build_mapping
from fde_accel.schema import detect_drift


class MappingTests(unittest.TestCase):
    def test_override_wins(self):
        m = build_mapping(["Client ID"], ["customer_id"], {"Client ID": "customer_id"})[0]
        self.assertEqual((m.source, m.method, m.confidence), ("Client ID", "override", 1.0))

    def test_drift(self):
        d = detect_drift({"a", "c"}, {"a", "b"})
        self.assertEqual(d, {"missing": ["b"], "unexpected": ["c"]})


if __name__ == "__main__":
    unittest.main()
