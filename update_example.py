#!/usr/bin/env python3
"""
Lamplit Office Lite - example updater (Python 3.8+, standard library only).

It writes office-data.js, the one file the page reads.

  python3 update_example.py                 write the file once
  python3 update_example.py --simulate      rewrite it every 5 seconds with made-up progress
  python3 update_example.py --out /path/to/office-data.js

NOTE: this overwrites office-data.js (the page always reads that one name).
To connect your own agents, replace status_from_my_agents() below.
"""
import argparse
import json
import os
import random
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent


def write_office(office, out_path):
    """Write the data file in one step, so the page never reads a half-written file."""
    office["updated"] = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    text = "// Written by update_example.py - it is overwritten on every run.\n"
    text += "window.OFFICE = " + json.dumps(office, ensure_ascii=False, indent=2) + ";\n"
    out_path = Path(out_path)
    fd, tmp = tempfile.mkstemp(dir=str(out_path.parent), prefix=".office-", suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, out_path)


def status_from_my_agents():
    """REPLACE THIS with your own data. Everything here is invented sample data.
    Allowed status values: working, waiting, done, review, blocked. Up to six team members."""
    def m(code, name, role, desk, status, progress, says):
        return {"code": code, "name": name, "role": role, "desk": desk, "status": status, "progress": progress, "says": says}
    return {
        "title": "Harbor Lane Office",
        "kicker": "Night shift",
        "subtitle": "Who is working on what, right now",
        "goal": "Ship the spring newsletter by Friday.",
        "refreshSeconds": 5,
        "room": {"title": "Workshop", "note": "Where things get built"},
        "team": [
            m("MO", "Morgan", "Lead: plans and signs off", "board", "working", 30, "Handing out today's tasks."),
            m("KA", "Kai", "Builder: writes the code", "terminal", "working", 5, "Starting the sign-up form."),
            m("SA", "Sam", "Writer: newsletter copy", "browser", "working", 20, "Writing the first draft."),
            m("JO", "Jo", "Reviewer: honest feedback", "review", "waiting", 0, "Nothing to review yet."),
            m("RA", "Ravi", "Data: counts what happened", "chart", "working", 60, "Adding up last week's numbers."),
            m("NO", "Noor", "QA: clicks through everything", "notes", "waiting", 0, "Waiting for the first build."),
        ],
        "note": "Sample data written by update_example.py. Everything on this page is invented.",
    }


def simulate_step(office, rng):
    """Made-up progress for a first look. Not needed in real use."""
    for m in office["team"]:
        if m["status"] == "working":
            m["progress"] = min(100, m["progress"] + rng.randint(4, 14))
            if m["progress"] >= 100:
                m["status"], m["says"] = "review", "Finished. Handing it to review."
        elif m["status"] == "review" and rng.random() < 0.35:
            m["status"], m["says"] = "done", "Review passed."
        elif m["status"] in ("waiting", "done") and rng.random() < 0.2:
            m["status"], m["progress"], m["says"] = "working", 5, "Next task picked up."


def main():
    ap = argparse.ArgumentParser(description="Write office-data.js for Lamplit Office Lite.")
    ap.add_argument("--out", default=str(HERE / "office-data.js"), help="path of the data file")
    ap.add_argument("--simulate", action="store_true", help="keep rewriting with made-up progress")
    ap.add_argument("--every", type=float, default=5.0, help="seconds between writes in --simulate")
    ap.add_argument("--steps", type=int, default=0, help="stop after this many writes (0 = until Ctrl+C)")
    args = ap.parse_args()
    office = status_from_my_agents()
    write_office(office, args.out)
    print("wrote", args.out)
    if not args.simulate:
        return
    rng, n = random.Random(), 1
    try:
        while not args.steps or n < args.steps:
            time.sleep(max(1.0, args.every))
            simulate_step(office, rng)
            write_office(office, args.out)
            n += 1
            print("wrote", args.out, "step", n)
    except KeyboardInterrupt:
        print("stopped")


if __name__ == "__main__":
    main()
