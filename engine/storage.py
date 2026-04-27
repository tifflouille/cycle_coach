"""
Local JSON storage for daily check-ins and feedback.

Each day's entry is stored as a JSON file: data/YYYY-MM-DD.json
This keeps things simple, portable, and easy to export to CSV later for analysis.
"""

import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
HKT = timezone(timedelta(hours=8))


def today_hkt() -> str:
    return datetime.now(HKT).strftime("%Y-%m-%d")


def _path(date_str: str) -> Path:
    return DATA_DIR / f"{date_str}.json"


def save_checkin(date_str: str, inputs: dict) -> None:
    """Save or update a daily check-in."""
    existing = load_entry(date_str)
    existing["checkin"] = inputs
    existing["checkin_at"] = datetime.now(HKT).isoformat()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_path(date_str), "w") as f:
        json.dump(existing, f, indent=2)


def save_recommendations(date_str: str, recs: list[dict]) -> None:
    """Save generated recommendations for a date."""
    existing = load_entry(date_str)
    existing["recommendations"] = recs

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_path(date_str), "w") as f:
        json.dump(existing, f, indent=2)


def save_feedback(date_str: str, feedback: dict) -> None:
    """Save end-of-day feedback."""
    existing = load_entry(date_str)
    existing["feedback"] = feedback
    existing["feedback_at"] = datetime.now(HKT).isoformat()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(_path(date_str), "w") as f:
        json.dump(existing, f, indent=2)


def load_entry(date_str: str) -> dict:
    """Load a day's full entry (checkin + recs + feedback)."""
    path = _path(date_str)
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {"date": date_str}


def load_all_entries() -> list[dict]:
    """Load all entries, sorted by date descending. For analysis/export."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    entries = []
    for f in sorted(DATA_DIR.glob("*.json"), reverse=True):
        try:
            with open(f) as fh:
                entries.append(json.load(fh))
        except json.JSONDecodeError:
            continue
    return entries


def export_csv(output_path: str = "data/export.csv") -> str:
    """Export all check-in + feedback data to a flat CSV for analysis."""
    import pandas as pd

    entries = load_all_entries()
    rows = []
    for entry in entries:
        checkin = entry.get("checkin", {})
        feedback = entry.get("feedback", {})
        recs = entry.get("recommendations", [])

        rows.append({
            "date": entry.get("date"),
            "cycle": checkin.get("cycle"),
            "sleep": checkin.get("sleep"),
            "mood": checkin.get("mood"),
            "energy": checkin.get("energy"),
            "soreness": ", ".join(checkin.get("soreness", [])) if isinstance(checkin.get("soreness"), list) else checkin.get("soreness"),
            "num_recommendations": len(recs),
            "rec_categories": ", ".join(sorted(set(r.get("category", "") for r in recs))),
            "followed": feedback.get("followed"),
            "feeling_after": feedback.get("feeling"),
            "feedback_notes": feedback.get("notes"),
        })

    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    return output_path
