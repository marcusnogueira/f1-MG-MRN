import os
import sys
import joblib
import fastf1
import pandas as pd

# Import-Fix für utils (nur wenn du das Skript direkt ausführst)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.feature_engineering import (
    get_track_affinity,
    get_team_strength,
    estimate_momentum
)

# Fix: Pfad zur utils importieren
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# GP auswählen
YEAR = 2023
RACE_NAME = "Monaco"

print(f"\n📊 Prediction für {RACE_NAME} {YEAR}:")

# Session laden
fastf1.Cache.enable_cache("cache")
session = fastf1.get_session(YEAR, RACE_NAME, "R")
session.load()
laps = session.laps.pick_quicklaps()
drivers = laps["Driver"].unique()

# Modell laden
model = joblib.load("models/rf_model_top10.pkl")

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

        prob = model.predict_proba(features)[0][1]
        results.append({
            "year": YEAR,
            "race": RACE_NAME,
            "driver": drv,
            "top10_probability": round(prob * 100, 2)
        })

    except Exception as e:
        print(f"❌ Fehler bei {drv}: {e}")

# Ausgabe speichern
df = pd.DataFrame(results)
os.makedirs("data/processed", exist_ok=True)
out_path = "data/processed/predicted_top10_probabilities.csv"
df.to_csv(out_path, index=False)

print("\n✅ Vorhersagen gespeichert in:", out_path)
print(df.sort_values(by="top10_probability", ascending=False).head(10))
