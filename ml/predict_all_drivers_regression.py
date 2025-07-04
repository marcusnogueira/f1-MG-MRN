import os
import sys
import joblib
import fastf1
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.feature_engineering import (
    get_track_affinity,
    get_team_strength,
    estimate_momentum
)

# Import-Fix für utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Session wählen
YEAR = 2023
RACE_NAME = "Monaco"

print(f"\n📊 Positionsvorhersage für {RACE_NAME} {YEAR}:")

# Daten & Modell
fastf1.Cache.enable_cache("cache")
session = fastf1.get_session(YEAR, RACE_NAME, "R")
session.load()
laps = session.laps.pick_quicklaps()
drivers = laps["Driver"].unique()

model = joblib.load("models/rf_model_regression.pkl")

results = []

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

        features = pd.DataFrame([{
            "fastest_lap": fastest_lap,
            "avg_lap": avg_lap,
            "stints": stints,
            "pitstops": pitstops,
            "laps_completed": laps_completed,
            "track_affinity": get_track_affinity(RACE_NAME, drv),
            "team_strength": get_team_strength(team),
            "momentum": estimate_momentum(laps_completed, avg_lap)
        }])

        predicted_pos = model.predict(features)[0]
        results.append({
            "year": YEAR,
            "race": RACE_NAME,
            "driver": drv,
            "expected_position": round(predicted_pos, 2)
        })

    except Exception as e:
        print(f"❌ Fehler bei {drv}: {e}")

# Ausgabe
df = pd.DataFrame(results)
os.makedirs("data/processed", exist_ok=True)
out_path = "data/processed/predicted_positions_regression.csv"
df.to_csv(out_path, index=False)

print("\n✅ Vorhersagen gespeichert in:", out_path)
print(df.sort_values(by="expected_position").head(10))
