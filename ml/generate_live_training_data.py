import os
import sys
import pandas as pd
import fastf1
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.feature_engineering import (
    get_track_affinity,
    get_team_strength,
    estimate_momentum
)

# Fix für utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
fastf1.Cache.enable_cache("cache")

# Konfiguration
YEAR = 2025
RACE = "Canada"
SESSION = "R"

# Session laden
session = fastf1.get_session(YEAR, RACE, SESSION)
session.load()
laps = session.laps.pick_quicklaps()
drivers = laps["Driver"].unique()

features = []

for drv in drivers:
    d_laps = laps[laps["Driver"] == drv]
    if d_laps.empty:
        continue

    try:
        fastest_lap = d_laps["LapTime"].min().total_seconds()
        avg_lap = d_laps["LapTime"].mean().total_seconds()
        stints = d_laps["Stint"].nunique()
        pitstops = d_laps["PitOutTime"].count()
        laps_completed = d_laps["LapNumber"].max()
        team = d_laps["Team"].iloc[0]

        features.append({
            "year": YEAR,
            "race": RACE,
            "driver": drv,
            "fastest_lap": fastest_lap,
            "avg_lap": avg_lap,
            "stints": stints,
            "pitstops": pitstops,
            "laps_completed": laps_completed,
            "track_affinity": get_track_affinity(RACE, drv),
            "team_strength": get_team_strength(team),
            "momentum": estimate_momentum(drv)
        })

    except Exception as e:
        print(f"❌ Fehler bei {drv}: {e}")

# Speichern
df = pd.DataFrame(features)
os.makedirs("data/live", exist_ok=True)
path = f"data/live/driver_feature_data_{YEAR}_{RACE}.csv"
df.to_csv(path, index=False)

print(f"\n✅ Live-Trainingsdaten gespeichert unter: {path}")
print(df.head())
