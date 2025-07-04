import os
import sys
import pandas as pd
import fastf1
import joblib
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.feature_engineering import (
    get_track_affinity,
    get_team_strength,
    estimate_momentum
)

# Import-Fix
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
fastf1.Cache.enable_cache("cache")

# Konfiguration
YEAR = 2025
SESSION_TYPE = "R"  # Race

# Event-Zeitplan abrufen
schedule = fastf1.get_event_schedule(YEAR, include_testing=False)
now = pd.Timestamp.now(tz="UTC")
available_races = schedule[schedule["Session5Date"] < now]

# Letztes abgeschlossenes Rennen bestimmen
if available_races.empty:
    print("⚠️ Es gibt noch kein abgeschlossenes Rennen in dieser Saison.")
    exit()

last_race = available_races.iloc[-1]
RACE_NAME = last_race["EventName"]

print(f"\n🟢 Letztes abgeschlossenes Rennen erkannt: {RACE_NAME} ({YEAR})")

# Modell laden
model = joblib.load("models/rf_model_position_classifier.pkl")

# Session laden
session = fastf1.get_session(YEAR, RACE_NAME, SESSION_TYPE)
session.load()
laps = session.laps.pick_quicklaps()
drivers = laps["Driver"].unique()

# Vorhersagen generieren
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

        X = pd.DataFrame([{
            "fastest_lap": fastest_lap,
            "avg_lap": avg_lap,
            "stints": stints,
            "pitstops": pitstops,
            "laps_completed": laps_completed,
            "track_affinity": get_track_affinity(RACE_NAME, drv),
            "team_strength": get_team_strength(team),
            "momentum": estimate_momentum(drv)
        }])

        proba = model.predict_proba(X)[0]
        for i, p in enumerate(proba, start=1):
            results.append({
                "year": YEAR,
                "race": RACE_NAME,
                "driver": drv,
                "position": i,
                "probability": round(p * 100, 2)
            })

    except Exception as e:
        print(f"❌ Fehler bei {drv}: {e}")

# Speichern
df = pd.DataFrame(results)
os.makedirs("data/live", exist_ok=True)
out_path = f"data/live/predicted_probabilities_{YEAR}_{RACE_NAME}.csv"
df.to_csv(out_path, index=False)

print(f"\n✅ Live-Prognose gespeichert unter: {out_path}")
print(df[df["position"] <= 3].sort_values(by="probability", ascending=False).head(10))
