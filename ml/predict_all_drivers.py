import pandas as pd
import joblib
import fastf1
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.feature_engineering import (
    get_track_affinity,
    get_team_strength,
    estimate_momentum
)

fastf1.Cache.enable_cache("cache")

# Konfiguration
RACE_NAME = "Monaco"
YEAR = 2023

# Modell laden
model = joblib.load("models/rf_model.pkl")

# Daten laden
event = fastf1.get_event(YEAR, RACE_NAME)
session = event.get_session("R")
session.load()

laps = session.laps.pick_quicklaps()
drivers = laps["Driver"].unique()

results = []

for driver in drivers:
    d_laps = laps[laps["Driver"] == driver]

    if d_laps.empty:
        continue

    try:
        # Feature-Berechnung
        fastest_lap = d_laps["LapTime"].min().total_seconds()
        avg_lap = d_laps["LapTime"].mean().total_seconds()
        stints = d_laps["Stint"].nunique()
        pitstops = d_laps["PitOutTime"].count()
        laps_completed = d_laps["LapNumber"].max()
        team = d_laps["Team"].iloc[0]

        # Feature-Vektor mit neuen Features
        X = pd.DataFrame([{
            "fastest_lap": fastest_lap,
            "avg_lap": avg_lap,
            "stints": stints,
            "pitstops": pitstops,
            "laps_completed": laps_completed,
            "track_affinity": get_track_affinity(RACE_NAME, driver),
            "team_strength": get_team_strength(team),
            "momentum": estimate_momentum(laps_completed, avg_lap)
        }])

        pred = model.predict(X)[0]
        proba = model.predict_proba(X)[0]

        result = {
            "driver": driver,
            "predicted_position": int(pred)
        }

        # Wahrscheinlichkeiten pro Platz hinzufügen
        for i, p in enumerate(proba):
            label = f"p_place_{model.classes_[i]}"
            result[label] = round(p, 4)

        results.append(result)

    except Exception as e:
        print(f"⚠️ Fehler bei {driver}: {e}")

# Speichern
df = pd.DataFrame(results)
os.makedirs("data/processed", exist_ok=True)
df.to_csv("data/processed/predicted_driver_positions.csv", index=False)
print("✅ Ergebnisse gespeichert unter data/processed/predicted_driver_positions.csv")
