"""
Cycle Coach — daily check-in and recommendation app.

Morning: log how you feel → get today's recommendations.
Evening: log whether you followed them and how you feel now.
"""

import streamlit as st
from engine.recommender import evaluate, format_recommendations
from engine.storage import (
    save_checkin, save_recommendations, save_feedback,
    load_entry, today_hkt, load_all_entries
)

st.set_page_config(page_title="Cycle Coach", page_icon="🌙", layout="centered")

# ── Sidebar: date + navigation ────────────────────────────────────

today = today_hkt()
st.sidebar.title("Cycle Coach")
date = st.sidebar.date_input("Date", value=None)
date_str = date.strftime("%Y-%m-%d") if date else today

entry = load_entry(date_str)
has_checkin = "checkin" in entry
has_feedback = "feedback" in entry

mode = st.sidebar.radio(
    "Mode",
    ["Check-in", "Recommendations", "Feedback", "History"],
    index=1 if has_checkin else 0,
)

# ── CHECK-IN ──────────────────────────────────────────────────────

if mode == "Check-in":
    st.title("Morning Check-in")
    st.caption(f"Logging for {date_str}")

    cycle = st.selectbox(
        "Cycle phase",
        ["", "Period", "Follicular", "Ovulation", "Luteal"],
        index=0,
    )
    sleep = st.slider("Hours of sleep", 0.0, 12.0, 7.5, 0.5)
    mood = st.selectbox("Mood", ["", "Happy", "Good", "Okay", "Sad", "Stressed", "Anxious"])
    energy = st.selectbox("Energy", ["", "High", "Medium", "Low"])
    soreness = st.multiselect(
        "Soreness (select all that apply)",
        ["Legs", "Glutes", "Arms", "Shoulders", "Back", "Core", "Full body"],
    )

    if st.button("Save check-in", type="primary"):
        if not cycle:
            st.warning("Please select your cycle phase.")
        else:
            inputs = {
                "cycle": cycle.lower(),
                "sleep": sleep,
                "mood": mood.lower() if mood else "",
                "energy": energy.lower() if energy else "",
                "soreness": [s.lower() for s in soreness],
            }
            save_checkin(date_str, inputs)

            # Generate and save recommendations
            recs = evaluate(inputs)
            save_recommendations(date_str, recs)

            st.success("Saved! Switch to Recommendations to see your plan.")
            st.rerun()

# ── RECOMMENDATIONS ───────────────────────────────────────────────

elif mode == "Recommendations":
    st.title("Today's Recommendations")
    st.caption(date_str)

    if not has_checkin:
        st.info("Complete your morning check-in first.")
    else:
        recs = entry.get("recommendations", [])
        if not recs:
            st.warning("No recommendations generated. Try re-submitting your check-in.")
        else:
            # Group by category
            category_icons = {
                "wellness": "🧘",
                "training": "💪",
                "nutrition": "🥗",
                "recovery": "🛁",
            }
            category_order = ["wellness", "training", "nutrition", "recovery"]

            grouped = {}
            for rec in recs:
                cat = rec["category"]
                grouped.setdefault(cat, []).append(rec["message"])

            for cat in category_order:
                if cat in grouped:
                    icon = category_icons.get(cat, "•")
                    st.subheader(f"{icon} {cat.capitalize()}")
                    for msg in grouped[cat]:
                        st.markdown(f"- {msg}")

            # Show inputs summary in expander
            with st.expander("Your check-in data"):
                checkin = entry.get("checkin", {})
                cols = st.columns(3)
                cols[0].metric("Sleep", f"{checkin.get('sleep', '?')}h")
                cols[1].metric("Energy", checkin.get("energy", "?").capitalize())
                cols[2].metric("Cycle", checkin.get("cycle", "?").capitalize())

# ── FEEDBACK ──────────────────────────────────────────────────────

elif mode == "Feedback":
    st.title("End-of-Day Feedback")
    st.caption(date_str)

    if not has_checkin:
        st.info("No check-in found for this date.")
    else:
        # Show today's recs as a reminder
        recs = entry.get("recommendations", [])
        if recs:
            with st.expander("Today's recommendations", expanded=False):
                for rec in recs:
                    st.markdown(f"- {rec['message']}")

        followed = st.selectbox(
            "Did you follow the recommendations?",
            ["Yes", "Partially", "No"],
        )
        feeling = st.selectbox(
            "How do you feel now?",
            ["Great", "Good", "Okay", "Tired", "Bad"],
        )
        notes = st.text_area("Any notes? (optional)")

        if st.button("Submit feedback", type="primary"):
            save_feedback(date_str, {
                "followed": followed.lower(),
                "feeling": feeling.lower(),
                "notes": notes,
            })
            st.success("Feedback saved!")

            if has_feedback:
                st.info("(Updated existing feedback for this date.)")

# ── HISTORY ───────────────────────────────────────────────────────

elif mode == "History":
    st.title("Check-in History")

    entries = load_all_entries()
    if not entries:
        st.info("No entries yet. Start with a check-in!")
    else:
        for entry in entries[:14]:  # show last 2 weeks
            d = entry.get("date", "?")
            checkin = entry.get("checkin", {})
            feedback = entry.get("feedback", {})
            recs = entry.get("recommendations", [])

            cycle = checkin.get("cycle", "—").capitalize()
            sleep = checkin.get("sleep", "—")
            energy = checkin.get("energy", "—").capitalize()
            followed = feedback.get("followed", "—").capitalize() if feedback else "—"

            with st.expander(f"{d}  |  {cycle}  |  Sleep: {sleep}h  |  Followed: {followed}"):
                if checkin:
                    st.markdown(f"**Mood:** {checkin.get('mood', '—').capitalize()}  \n"
                                f"**Energy:** {energy}  \n"
                                f"**Soreness:** {', '.join(checkin.get('soreness', [])) or 'None'}")
                if recs:
                    st.markdown("**Recommendations:**")
                    for rec in recs:
                        st.markdown(f"- {rec['message']}")
                if feedback:
                    st.markdown(f"**Feeling after:** {feedback.get('feeling', '—').capitalize()}  \n"
                                f"**Notes:** {feedback.get('notes', '—') or '—'}")
