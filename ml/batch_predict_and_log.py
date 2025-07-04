import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pandas as pd
import fastf1
import joblib
from utils.feature_engineering import (
    get_track_affinity,
    get_team_strength,
    estimate_momentum
)

# Fix für utils import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

fastf1.Cache.enable_cache("cache")

# Konfiguration
YEAR = 2023
model = joblib.load("models/rf_model_position_classifier.pkl")

# Rennen laden
schedule = fastf1.get_event_schedule(YEAR, include_testing=False)
race_names = schedule["EventName"].tolist()

all_predictions = []
all_results = []

for race in race_names:
    try:
        print(f"\n🔄 Lade: {race} {YEAR}")
        session = fastf1.get_session(YEAR, race, "R")
        session.load()
        laps = session.laps.pick_quicklaps()
        drivers = laps["Driver"].unique()

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

                X = pd.DataFrame([{
                    "fastest_lap": fastest_lap,
                    "avg_lap": avg_lap,
                    "stints": stints,
                    "pitstops": pitstops,
                    "laps_completed": laps_completed,
                    "track_affinity": get_track_affinity(race, drv),
                    "team_strength": get_team_strength(team),
                    "momentum": estimate_momentum(drv)
                }])

                proba = model.predict_proba(X)[0]
                for i, p in enumerate(proba, start=1):
                    all_predictions.append({
                        "year": YEAR,
                        "race": race,
                        "driver": drv,
                        "position": i,
                        "probability": round(p * 100, 2)
                    })

            except Exception as e:
                print(f"❌ Fehler bei {drv} in {race}: {e}")

        # Logge echte Resultate
        results = (
            session.laps.groupby("Driver")["Position"]
            .min()
            .reset_index()
            .rename(columns={"Position": "final_position"})
        )
        results["year"] = YEAR
        results["race"] = race
        all_results.append(results)

    except Exception as e:
        print(f"⚠️ Rennen übersprungen ({race}): {e}")

# Speichern
os.makedirs("data/batch", exist_ok=True)
pd.DataFrame(all_predictions).to_csv(f"data/batch/predictions_{YEAR}.csv", index=False)
pd.concat(all_results).to_csv(f"data/batch/actual_results_{YEAR}.csv", index=False)

print("\n✅ Multirennen-Batch abgeschlossen!")
