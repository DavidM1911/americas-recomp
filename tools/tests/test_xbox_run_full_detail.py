import os
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS / "xbox"))
os.environ["XBOX_RDNA2"] = "recomp"

import run_full

PRINT_FILE = "import sys; sys.stdout.write(open(sys.argv[1], encoding='utf-8').read())"


class ThrowDetailTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def classify(self, line):
        out = self.root / "driver_output.txt"
        out.write_text(line, encoding="utf-8")
        return run_full.classify([sys.executable, "-c", PRINT_FILE, str(out)], str(self.root / "unused.spv"), None)

    def test_short_detail_is_kept_whole(self):
        self.assertEqual(self.classify("THROW short reason RecompileRequest: AAAA"), ("THROW", "short reason"))

    def test_long_detail_keeps_the_give_up_reason(self):
        reason = "; descriptor web: more than 512 descriptor states"
        head = "GetSamplerResource dword 0 is not a valid runtime value; chain: "
        status, detail = self.classify("THROW " + head + "Phi(" * 20000 + reason + " RecompileRequest: AAAA")
        self.assertEqual(status, "THROW")
        self.assertLessEqual(len(detail), 255)
        self.assertTrue(detail.startswith(head))
        self.assertTrue(detail.endswith(reason))


if __name__ == "__main__":
    unittest.main()
