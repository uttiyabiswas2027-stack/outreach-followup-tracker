import unittest
from datetime import date
from tracker import load, due_follow_ups, funnel, report


class TrackerTests(unittest.TestCase):
    def setUp(self):
        self.rows = load("data/sample_outreach.csv")
        self.today = date(2026, 11, 13)

    def test_due(self):
        names = [r["name"] for r in due_follow_ups(self.rows, self.today)]
        self.assertEqual(names, ["Founder A", "Founder E"])

    def test_funnel(self):
        f = funnel(self.rows)
        self.assertEqual(f["total"], 5)
        self.assertEqual(f["reply_rate_pct"], 40.0)

    def test_report_text(self):
        self.assertIn("Follow up today (2):", report(self.rows, self.today))

    def test_bad_status(self):
        import csv, tempfile, os
        p = os.path.join(tempfile.mkdtemp(), "x.csv")
        with open(p, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["name", "company", "channel", "status", "last_contacted"])
            w.writerow(["A", "B", "email", "ghosted", "2026-11-01"])
        with self.assertRaises(ValueError):
            load(p)


class CsvValidationTests(unittest.TestCase):
    def load_csv(self, text):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "input.csv"
            path.write_text(text, encoding="utf-8")
            return load(path)

    def test_cli_validation_error(self):
        import subprocess, sys, tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.csv"
            path.write_text("wrong\nvalue\n", encoding="utf-8")
            command = [sys.executable, "tracker.py", str(path)] + ["2026-11-13"]
            result = subprocess.run(command, text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("Error: missing columns", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_missing_header(self):
        with self.assertRaisesRegex(ValueError, "missing columns"):
            self.load_csv("wrong\nvalue\n")

    def test_empty_file(self):
        with self.assertRaisesRegex(ValueError, "missing columns"):
            self.load_csv("")

    def test_duplicate_header(self):
        with self.assertRaisesRegex(ValueError, "duplicate column"):
            self.load_csv(self.header.rstrip("\n") + ",name,name\n")

    def test_extra_field(self):
        with self.assertRaisesRegex(ValueError, "row 2: too many fields"):
            self.load_csv(self.header + self.good.rstrip("\n") + ",extra\n")

    def test_missing_field(self):
        with self.assertRaisesRegex(ValueError, "row 2:.*required"):
            self.load_csv(self.header + ",".join(self.good.strip().split(",")[:-1]) + "\n")

    def test_utf8_bom(self):
        self.assertEqual(len(self.load_csv("\ufeff" + self.header + self.good)), 1)

    def test_whitespace(self):
        row = ",".join(" " + value + " " for value in self.good.strip().split(","))
        self.assertEqual(self.load_csv(self.header + row), self.load_csv(self.header + self.good))

    header = "name,company,channel,status,last_contacted\n"
    good = "A,Example,email,sent,2026-11-01\n"

    def test_invalid_dates(self):
        for value in ("2026-02-30", "20261101", "yesterday"):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "valid YYYY-MM-DD"):
                self.load_csv(self.header + self.good.replace("2026-11-01", value))

    def test_blank_identity(self):
        with self.assertRaisesRegex(ValueError, "row 2: name is required"):
            self.load_csv(self.header + self.good.replace("A,", " ,", 1))

    def test_header_only_is_empty_pipeline(self):
        rows = self.load_csv(self.header)
        self.assertEqual(funnel(rows)["reply_rate_pct"], 0.0)
        self.assertEqual(due_follow_ups(rows, date(2026, 11, 13)), [])

    def test_due_boundary_and_terminal_statuses(self):
        rows = self.load_csv(self.header + "A,Example,email,sent,2026-11-08\n"
                             + "B,Example,email,sent,2026-11-09\n"
                             + "C,Example,email,closed,2026-11-01\n")
        self.assertEqual([r["name"] for r in due_follow_ups(rows, date(2026, 11, 13))], ["A"])


if __name__ == "__main__":
    unittest.main()
