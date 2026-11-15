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

## Use your own CSV

Required columns: `name,company,channel,status,last_contacted`.
All fields are required. Dates must use `YYYY-MM-DD`; status must be one of `sent`, `replied`, `call_booked`, `closed`, `no_response`. A header-only file is an empty pipeline. Unknown extra columns are ignored.

CSV files exported with a UTF-8 BOM are supported, and surrounding cell whitespace is stripped. Missing columns, duplicate headers, blank cells, extra fields and invalid dates/statuses stop the report with a clear error.

Only `sent` contacts last contacted at least five days before the supplied report date appear as due. This tool prints suggestions only: it does not send messages, read your inbox or change contact statuses. Reply rate counts `replied`, `call_booked` and `closed` contacts as replies. The sample pipeline is fictional. Keep real names and outreach lists outside this public repository.
