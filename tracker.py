"""Outreach follow-up tracker. Reads a CSV of contacts, lists who needs a follow-up and prints funnel stats.

Usage: python tracker.py data/sample_outreach.csv 2026-11-13
Columns: name, company, channel, status, last_contacted (YYYY-MM-DD)
Statuses: sent, replied, call_booked, closed, no_response
"""
import csv
import sys
from collections import Counter
from datetime import date, timedelta

FOLLOW_UP_AFTER_DAYS = 5
STATUSES = ("sent", "replied", "call_booked", "closed", "no_response")


def load(path):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        if r["status"] not in STATUSES:
            raise ValueError(f"bad status {r['status']!r} for {r['name']}")
        r["last_contacted"] = date.fromisoformat(r["last_contacted"])
    return rows


def due_follow_ups(rows, today):
    cutoff = today - timedelta(days=FOLLOW_UP_AFTER_DAYS)
    return [r for r in rows if r["status"] == "sent" and r["last_contacted"] <= cutoff]


def funnel(rows):
    c = Counter(r["status"] for r in rows)
    total = len(rows)
    replied = c["replied"] + c["call_booked"] + c["closed"]
    return {
        "total": total,
        "by_status": {s: c[s] for s in STATUSES},
        "reply_rate_pct": round(replied / total * 100, 1) if total else 0.0,
    }


def report(rows, today):
    f = funnel(rows)
    lines = [f"Contacts: {f['total']}  Reply rate: {f['reply_rate_pct']}%"]
    lines += [f"  {s}: {n}" for s, n in f["by_status"].items()]
    due = due_follow_ups(rows, today)
    lines.append(f"Follow up today ({len(due)}):")
    lines += [f"  - {r['name']} ({r['company']}) via {r['channel']}, last {r['last_contacted']}" for r in due]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    sys.stdout.write(report(load(sys.argv[1]), date.fromisoformat(sys.argv[2])))
