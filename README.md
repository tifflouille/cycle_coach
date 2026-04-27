# Cycle Coach

A cycle-synced wellness recommendation engine. Log how you feel each morning, get personalized daily recommendations based on your cycle phase, sleep, energy, mood, and soreness. Log feedback in the evening to build a dataset for future model training.

## What it does

**Morning check-in** → 5 inputs (cycle phase, sleep, mood, energy, soreness)  
**Engine** → evaluates ~25 rules with weighted priorities, mutual exclusivity, and interaction effects  
**Recommendations** → top 5 categorized suggestions (wellness, training, nutrition, recovery)  
**Evening feedback** → did you follow them? how do you feel now?  
**Data** → stored as daily JSON files, exportable to CSV for analysis  

## Structure

```
cycle-coach/
│   ├── rules.py          # All recommendation rules (add/edit here)
│   ├── recommender.py    # Rule evaluation + conflict resolution
│   └── storage.py        # JSON-based daily data storage
├── app/
│   └── streamlit_app.py  # Daily check-in + feedback UI
├── data/                  # Daily JSON entries (auto-created)
├── analysis/              # Notebooks for exploring your data
└── requirements.txt
```

## Setup

```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

## How to add rules

Edit `engine/rules.py`. Each rule needs:
- **condition**: a function that takes the day's inputs and returns True/False
- **message**: what to recommend
- **weight**: priority (higher wins)
- **category**: nutrition / training / recovery / wellness
- **excludes** (optional): rule IDs that can't coexist (e.g., "full rest day" excludes "go all out")

## Roadmap

- [ ] 30 days of consistent daily data
- [ ] Analysis notebook: which recommendations correlate with "feeling great" feedback?
- [ ] Cycle pattern detection (auto-suggest phase based on history)
- [ ] Replace hardcoded rules with learned preferences
- [ ] Optional Strava integration (re-add when exercising regularly)
- [ ] Move beyond Streamlit if pursuing product validation
