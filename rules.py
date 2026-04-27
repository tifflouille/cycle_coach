"""
Rule definitions for cycle-synced wellness recommendations.

Each rule is a dict with:
    - id: unique identifier
    - condition: callable(inputs) -> bool
    - message: recommendation text
    - weight: priority (higher = more important)
    - category: one of "nutrition", "training", "recovery", "wellness"
    - excludes: list of rule IDs this rule is incompatible with (optional)
"""


def build_rules():
    """Returns the full list of recommendation rules."""

    rules = []

    def rule(id, condition, message, weight, category, excludes=None):
        rules.append({
            "id": id,
            "condition": condition,
            "message": message,
            "weight": weight,
            "category": category,
            "excludes": excludes or [],
        })

    # ── CYCLE: PERIOD ──────────────────────────────────────────────

    rule(
        "period_rest",
        lambda i: i["cycle"] == "period",
        "You're on your period — prioritize rest, gentle yoga, or stretching today.",
        10, "wellness",
        excludes=["ovulation_push", "follicular_hiit", "energy_high_train"],
    )
    rule(
        "period_nutrition",
        lambda i: i["cycle"] == "period",
        "Eat iron- and magnesium-rich foods: dark leafy greens, quinoa, dark chocolate, nuts.",
        9, "nutrition",
    )
    rule(
        "period_avoid",
        lambda i: i["cycle"] == "period",
        "Avoid coffee, alcohol, and refined sugar today — they worsen cramps and inflammation.",
        8, "nutrition",
    )
    rule(
        "period_sleep",
        lambda i: i["cycle"] == "period" and i["sleep"] < 7,
        "Sleep is especially important during your period. Try to get to bed earlier tonight.",
        9, "wellness",
    )

    # ── CYCLE: LUTEAL ──────────────────────────────────────────────

    rule(
        "luteal_chill",
        lambda i: i["cycle"] == "luteal",
        "Luteal phase — stick to gentle movement: yoga, walking, swimming, sauna.",
        9, "wellness",
        excludes=["ovulation_push", "follicular_hiit"],
    )
    rule(
        "luteal_nutrition",
        lambda i: i["cycle"] == "luteal",
        "Support progesterone with vitamin B6 and magnesium: bananas, oats, salmon, pumpkin seeds.",
        8, "nutrition",
    )
    rule(
        "luteal_high_energy",
        lambda i: i["cycle"] == "luteal" and i["energy"] == "high",
        "Energy is high despite luteal phase — a light run or moderate session is fine if it feels right.",
        5, "training",
    )

    # ── CYCLE: FOLLICULAR ──────────────────────────────────────────

    rule(
        "follicular_hiit",
        lambda i: i["cycle"] == "follicular",
        "Follicular phase — great time for high-intensity work: HIIT, sprints, heavy lifts.",
        9, "training",
        excludes=["period_rest", "luteal_chill", "full_rest_day"],
    )
    rule(
        "follicular_nutrition",
        lambda i: i["cycle"] == "follicular",
        "Eat estrogen-balancing foods: cruciferous veggies, flaxseed, fermented foods, healthy fats.",
        7, "nutrition",
    )
    rule(
        "follicular_creativity",
        lambda i: i["cycle"] == "follicular",
        "Your brain is primed for creativity and planning in the follicular phase — use it.",
        6, "wellness",
    )

    # ── CYCLE: OVULATION ───────────────────────────────────────────

    rule(
        "ovulation_push",
        lambda i: i["cycle"] == "ovulation",
        "Ovulation = peak strength and energy. Push your limits — PRs live here.",
        10, "training",
        excludes=["period_rest", "luteal_chill", "full_rest_day"],
    )
    rule(
        "ovulation_nutrition",
        lambda i: i["cycle"] == "ovulation",
        "Fuel peak performance: lean protein, complex carbs, anti-inflammatory foods (berries, turmeric).",
        7, "nutrition",
    )

    # ── SLEEP ──────────────────────────────────────────────────────

    rule(
        "sleep_critical",
        lambda i: i["sleep"] < 5,
        "Under 5 hours of sleep — skip intense training. Restorative activities only: sauna, yoga, walk.",
        10, "wellness",
        excludes=["ovulation_push", "follicular_hiit", "energy_high_train"],
    )
    rule(
        "sleep_low",
        lambda i: 5 <= i["sleep"] < 7,
        "Sleep was short. Keep intensity moderate today and prioritize an early night.",
        7, "wellness",
    )
    rule(
        "sleep_good",
        lambda i: i["sleep"] >= 8,
        "Good sleep — you're well recovered. Make the most of today's session.",
        4, "wellness",
    )

    # ── ENERGY ─────────────────────────────────────────────────────

    rule(
        "energy_low",
        lambda i: i["energy"] == "low",
        "Energy is low. Walk, yoga, or gentle movement — don't force intensity.",
        8, "wellness",
        excludes=["energy_high_train"],
    )
    rule(
        "energy_high_train",
        lambda i: i["energy"] == "high" and i["cycle"] not in ("period", "luteal"),
        "Energy is high — great day for a challenging workout.",
        8, "training",
        excludes=["energy_low", "full_rest_day"],
    )

    # ── MOOD ───────────────────────────────────────────────────────

    rule(
        "mood_low",
        lambda i: i["mood"] in ("sad", "stressed", "anxious"),
        "Mood is low — try a walk outside, yoga, or meditation. Movement helps, but don't push.",
        8, "wellness",
    )
    rule(
        "mood_happy",
        lambda i: i["mood"] == "happy",
        "Feeling good — pick a workout you genuinely enjoy today.",
        5, "training",
    )

    # ── SORENESS ───────────────────────────────────────────────────

    rule(
        "soreness_legs",
        lambda i: any(s in i["soreness"] for s in ["legs", "glutes", "quads", "hamstrings"]),
        "Lower body is sore — do upper body work or active recovery today.",
        7, "training",
    )
    rule(
        "soreness_upper",
        lambda i: any(s in i["soreness"] for s in ["arms", "shoulders", "back", "chest"]),
        "Upper body sore — lower body or cardio today.",
        6, "training",
    )
    rule(
        "soreness_full",
        lambda i: len(i["soreness"]) >= 3,
        "Multiple areas sore — full recovery day. Foam roll, stretch, sauna.",
        9, "recovery",
        excludes=["ovulation_push", "follicular_hiit", "energy_high_train"],
    )

    # ── INTERACTION RULES (combinations) ───────────────────────────

    rule(
        "full_rest_day",
        lambda i: i["cycle"] in ("period", "luteal") and i["sleep"] < 6 and i["energy"] == "low",
        "Period/luteal + poor sleep + low energy — this is a full rest day. No guilt.",
        12, "recovery",
        excludes=["ovulation_push", "follicular_hiit", "energy_high_train"],
    )
    rule(
        "power_day",
        lambda i: (i["cycle"] in ("follicular", "ovulation")
                   and i["sleep"] >= 7
                   and i["energy"] == "high"
                   and len(i["soreness"]) == 0),
        "Everything is aligned — cycle, sleep, energy, no soreness. Go all out today.",
        11, "training",
        excludes=["period_rest", "luteal_chill", "full_rest_day", "energy_low"],
    )
    rule(
        "gentle_movement",
        lambda i: i["mood"] in ("sad", "stressed") and i["energy"] == "low",
        "Low mood + low energy. A gentle 20-minute walk outside will help more than forcing a workout.",
        10, "wellness",
        excludes=["energy_high_train", "ovulation_push"],
    )

    # ── RECOVERY / GENERAL ─────────────────────────────────────────

    rule(
        "hydration",
        lambda i: i["sleep"] < 6 or i["energy"] == "low",
        "Drink at least 2L of water today — dehydration amplifies fatigue.",
        6, "wellness",
    )
    rule(
        "stretch_reminder",
        lambda i: len(i["soreness"]) > 0,
        "Include 10 minutes of stretching today — it makes a real difference.",
        5, "recovery",
    )

    return rules
