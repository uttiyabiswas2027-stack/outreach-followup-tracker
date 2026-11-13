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


if __name__ == "__main__":
    unittest.main()
