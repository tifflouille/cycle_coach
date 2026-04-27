"""
Recommendation engine.

Takes daily inputs, evaluates rules, resolves conflicts via mutual exclusivity,
and returns a prioritized, categorized set of recommendations.
"""

from engine.rules import build_rules


def normalize_inputs(raw: dict) -> dict:
    """
    Normalize raw user inputs into the format rules expect.

    Expected raw keys: cycle, sleep, mood, energy, soreness
    """
    def clean(val):
        if val is None:
            return ""
        return str(val).strip().lower()

    soreness_raw = raw.get("soreness", "")
    if isinstance(soreness_raw, list):
        soreness = [s.strip().lower() for s in soreness_raw if s]
    elif isinstance(soreness_raw, str) and soreness_raw.strip():
        soreness = [s.strip().lower() for s in soreness_raw.split(",") if s.strip()]
    else:
        soreness = []

    sleep_val = raw.get("sleep", 8)
    try:
        sleep_val = float(sleep_val)
    except (ValueError, TypeError):
        sleep_val = 8.0

    return {
        "cycle": clean(raw.get("cycle", "")),
        "sleep": sleep_val,
        "mood": clean(raw.get("mood", "")),
        "energy": clean(raw.get("energy", "")),
        "soreness": soreness,
    }


def evaluate(raw_inputs: dict, max_recommendations: int = 5) -> list[dict]:
    """
    Evaluate all rules against inputs and return top recommendations.

    Returns list of dicts:
        [{"message": str, "category": str, "weight": int, "id": str}, ...]
    """
    inputs = normalize_inputs(raw_inputs)
    rules = build_rules()

    # Step 1: find all triggered rules
    triggered = []
    for rule in rules:
        try:
            if rule["condition"](inputs):
                triggered.append(rule)
        except Exception:
            continue

    # Step 2: sort by weight descending
    triggered.sort(key=lambda r: r["weight"], reverse=True)

    # Step 3: resolve mutual exclusivity (higher weight wins)
    selected = []
    excluded_ids = set()

    for rule in triggered:
        if rule["id"] in excluded_ids:
            continue
        selected.append(rule)
        excluded_ids.update(rule.get("excludes", []))

    # Step 4: ensure category diversity — at least one nutrition rec if available
    categories_present = {r["category"] for r in selected[:max_recommendations]}
    final = selected[:max_recommendations]

    if "nutrition" not in categories_present:
        nutrition_recs = [r for r in selected if r["category"] == "nutrition" and r["id"] not in excluded_ids]
        if nutrition_recs:
            # swap the lowest-weight rec for the top nutrition one
            final[-1] = nutrition_recs[0]

    # Step 5: format output
    return [
        {
            "id": r["id"],
            "message": r["message"],
            "category": r["category"],
            "weight": r["weight"],
        }
        for r in final
    ]


def format_recommendations(recs: list[dict]) -> str:
    """Format recommendations as readable text grouped by category."""
    category_labels = {
        "nutrition": "Nutrition",
        "training": "Training",
        "recovery": "Recovery",
        "wellness": "Wellness",
    }
    category_order = ["wellness", "training", "nutrition", "recovery"]

    grouped = {}
    for rec in recs:
        cat = rec["category"]
        grouped.setdefault(cat, []).append(rec["message"])

    lines = []
    for cat in category_order:
        if cat in grouped:
            lines.append(f"\n{category_labels[cat]}")
            lines.append("-" * len(category_labels[cat]))
            for msg in grouped[cat]:
                lines.append(f"  • {msg}")

    return "\n".join(lines)
