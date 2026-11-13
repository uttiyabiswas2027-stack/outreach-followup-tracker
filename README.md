# outreach-followup-tracker

A small tool for running cold outreach to founders as a pipeline instead of a pile of emails. It reads a CSV of contacts and prints the reply rate, the funnel by status and who is due a follow-up (status `sent` for 5+ days).

The CSV in `data/` uses placeholder names. Real contact lists are never committed.

## Run it

```
python tracker.py data/sample_outreach.csv 2026-11-13
python -m unittest -v
```

Python 3.9+, standard library only.

## Automation

`.github/workflows/daily-followups.yml` runs the tests and the follow-up report every day and on every push, and writes the result to the Actions run summary.

## Why it exists

Cold outreach only works if follow-ups are consistent. This turns "who do I chase today" into a one-command answer and tracks the reply rate so the message can be tested and improved.
