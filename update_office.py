#!/usr/bin/env python3
"""
Lamplit Office Lite - write office-data.js from a simple list (Python 3.8+, standard library only).

Keep your team in a CSV file (a spreadsheet export) or a JSON file. This script turns
that list into office-data.js, the one file the page reads.

  python3 update_office.py team.sample.csv
  python3 update_office.py team.sample.json
  python3 update_office.py team.csv --title "My agents" --goal "Ship v2 by Friday"
  python3 update_office.py team.csv --watch          rewrite whenever team.csv is saved
  python3 update_office.py team.csv --history log    also keep a time-stamped copy in ./log

CSV columns (first line is the header, order does not matter, comma or semicolon):
  code, name, role, desk, status, progress, says, started, minutes
Only "name" is required.

JSON: either a list of team members, or one object with "team" plus the page fields
(title, kicker, subtitle, goal, refreshSeconds, theme, room, note).

NOTE: this overwrites office-data.js (the page always reads that one name).
It never changes your CSV or JSON file.
"""
import argparse
import csv
import json
import os
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATUSES = ("working", "waiting", "done", "review", "blocked")
DESKS = ("board", "review", "browser", "terminal", "chart", "notes")
MEMBER_FIELDS = ("code", "name", "role", "desk", "status", "progress", "says", "started", "minutes")
PAGE_FIELDS = ("title", "kicker", "subtitle", "goal", "refreshSeconds", "theme", "room", "note")
MAX_DESKS = 6


class InputError(Exception):
    """The list could not be read. The message says what to fix."""


def warn(text):
    print("warning:", text, file=sys.stderr)


def read_csv(path):
    text = Path(path).read_text(encoding="utf-8-sig")
    first = text.split("\n", 1)[0]
    delimiter = ";" if first.count(";") > first.count(",") else ","
    rows = list(csv.reader(text.splitlines(), delimiter=delimiter))
    if not rows:
        raise InputError("%s is empty." % path)
    header = [h.strip().lower() for h in rows[0]]
    if "name" not in header:
        raise InputError('%s: the first line must be a header with at least a "name" column. Found: %s'
                         % (path, ", ".join(header) or "(nothing)"))
    for h in header:
        if h and h not in MEMBER_FIELDS:
            warn('column "%s" is not used by the page and is left out.' % h)
    team = []
    for cells in rows[1:]:
        if not any(c.strip() for c in cells):
            continue
        team.append({h: c.strip() for h, c in zip(header, cells) if h in MEMBER_FIELDS and c.strip()})
    return {"team": team}


def read_json(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as e:
        raise InputError("%s is not valid JSON: %s" % (path, e))
    if isinstance(data, list):
        return {"team": data}
    if isinstance(data, dict) and isinstance(data.get("team"), list):
        return data
    raise InputError('%s must be a list of team members, or an object with a "team" list.' % path)


def initials(name):
    parts = [p for p in name.replace("-", " ").split() if p]
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    return name[:2].upper() or "??"


def number(value, what, who):
    try:
        return float(str(value).replace("%", "").replace(",", ".").strip())
    except ValueError:
        warn('%s: %s "%s" is not a number, using 0.' % (who, what, value))
        return 0.0


def clean_member(raw, row):
    if not isinstance(raw, dict):
        raise InputError("team member %d is not an object." % row)
    name = str(raw.get("name") or "").strip()
    if not name:
        raise InputError('team member %d has no "name".' % row)
    m = {"code": (str(raw.get("code") or "").strip() or initials(name))[:4], "name": name}
    if raw.get("role"):
        m["role"] = str(raw["role"]).strip()
    desk = str(raw.get("desk") or "notes").strip().lower()
    if desk not in DESKS:
        warn('%s: desk "%s" is unknown, using "notes". Allowed: %s' % (name, desk, ", ".join(DESKS)))
        desk = "notes"
    m["desk"] = desk
    status = str(raw.get("status") or "waiting").strip().lower()
    if status not in STATUSES:
        warn('%s: status "%s" is unknown and will be shown as written. Allowed: %s'
             % (name, status, ", ".join(STATUSES)))
    m["status"] = status
    progress = number(raw.get("progress") or 0, "progress", name)
    m["progress"] = int(round(max(0.0, min(100.0, progress))))
    if raw.get("says"):
        m["says"] = str(raw["says"]).strip()
    if raw.get("started") and raw.get("minutes"):
        m["started"] = str(raw["started"]).strip()
        minutes = number(raw["minutes"], "minutes", name)
        m["minutes"] = int(minutes) if minutes == int(minutes) else minutes
    return m


def build_office(source, args):
    """Turn the list into the object the page expects. Command-line options win over the file."""
    office = {k: source[k] for k in PAGE_FIELDS if k in source}
    for key, value in (("title", args.title), ("kicker", args.kicker), ("subtitle", args.subtitle),
                       ("goal", args.goal), ("note", args.note), ("theme", args.theme),
                       ("refreshSeconds", args.refresh)):
        if value is not None:
            office[key] = value
    if args.room is not None or args.room_note is not None:
        room = dict(office.get("room") or {}) if isinstance(office.get("room"), dict) else {}
        if args.room is not None:
            room["title"] = args.room
        if args.room_note is not None:
            room["note"] = args.room_note
        office["room"] = room
    office.setdefault("title", "Agent Office")
    office.setdefault("refreshSeconds", 30)
    team = [clean_member(raw, i + 1) for i, raw in enumerate(source["team"])]
    if not team:
        warn("the list has no team members; the page will show an empty room.")
    if len(team) > MAX_DESKS:
        warn("the list has %d team members; Lite shows the first %d." % (len(team), MAX_DESKS))
    office["team"] = team
    return office


def write_office(office, out_path, made_by):
    """Write the data file in one step, so the page never reads a half-written file."""
    office = dict(office)
    office["updated"] = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    text = "// Written by update_office.py from %s - it is overwritten on every run.\n" % made_by
    text += "window.OFFICE = " + json.dumps(office, ensure_ascii=False, indent=2) + ";\n"
    out_path = Path(out_path)
    fd, tmp = tempfile.mkstemp(dir=str(out_path.parent), prefix=".office-", suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
    os.chmod(tmp, 0o644)
    os.replace(tmp, out_path)
    return text


def run_once(args):
    src = Path(args.list)
    if not src.is_file():
        raise InputError("cannot find %s" % src)
    source = read_json(src) if src.suffix.lower() == ".json" else read_csv(src)
    office = build_office(source, args)
    text = write_office(office, args.out, src.name)
    n = len(office["team"])
    line = "wrote %s (%d team member%s)" % (args.out, n, "" if n == 1 else "s")
    if args.history:
        folder = Path(args.history)
        folder.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
        copy = folder / ("office-data_%s.js" % stamp)
        copy.write_text(text, encoding="utf-8")
        line += ", copy: %s" % copy
    print(line)


def main():
    ap = argparse.ArgumentParser(description="Write office-data.js for Lamplit Office Lite from a CSV or JSON list.")
    ap.add_argument("list", help="your team list: a .csv or .json file")
    ap.add_argument("--out", default=str(HERE / "office-data.js"), help="path of the data file (default: next to this script)")
    ap.add_argument("--title", help="big title in the header")
    ap.add_argument("--kicker", help="small line above the title")
    ap.add_argument("--subtitle", help="line below the title")
    ap.add_argument("--goal", help="one sentence: what the team is working towards")
    ap.add_argument("--room", help="name of the room")
    ap.add_argument("--room-note", help="small line under the room name")
    ap.add_argument("--note", help="small print at the bottom of the page")
    ap.add_argument("--theme", choices=("dark", "light", "auto"), help="colours the page starts with")
    ap.add_argument("--refresh", type=int, help="how often the page re-reads the file, in seconds (5 to 3600)")
    ap.add_argument("--watch", nargs="?", type=float, const=2.0, default=None, metavar="SECONDS",
                    help="keep running and rewrite the data file whenever the list is saved (checks every 2 seconds)")
    ap.add_argument("--history", metavar="FOLDER", help="also save a time-stamped copy of every written file in this folder")
    args = ap.parse_args()

    if args.watch is None:
        try:
            run_once(args)
        except InputError as e:
            print("error:", e, file=sys.stderr)
            return 2
        return 0

    print("watching %s - stop with Ctrl+C" % args.list)
    last = None
    try:
        while True:
            try:
                stamp = os.stat(args.list).st_mtime_ns
            except OSError:
                stamp = None
            if stamp != last:
                last = stamp
                try:
                    run_once(args)
                except InputError as e:
                    print("error:", e, "- waiting for the next save.", file=sys.stderr)
            time.sleep(max(0.5, args.watch))
    except KeyboardInterrupt:
        print("stopped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
