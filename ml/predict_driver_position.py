import pandas as pd
import joblib
import fastf1
import sys
import os

fastf1.Cache.enable_cache("cache")

# Nutzer-Eingabe
RACE_NAME = "Monaco"
YEAR = 2023
DRIVER_CODE = "VER"  # 3-Buchstaben Kürzel

# Modell laden
model = joblib.load("models/rf_model.pkl")

# Session laden
event = fastf1.get_event(YEAR, RACE_NAME)
session = event.get_session("R")
session.load()

laps = session.laps.pick_quicklaps().pick_driver(DRIVER_CODE)

if laps.empty:
    print(f"❌ No lap data for {DRIVER_CODE} in {RACE_NAME} {YEAR}")
    sys.exit()

# Features berechnen
fastest_lap = laps["LapTime"].min().total_seconds()
avg_lap = laps["LapTime"].mean().total_seconds()
stints = laps["Stint"].nunique()
pitstops = laps["PitOutTime"].count()
laps_completed = laps["LapNumber"].max()

X = pd.DataFrame([{
    "fastest_lap": fastest_lap,
    "avg_lap": avg_lap,
    "stints": stints,
    "pitstops": pitstops,
    "laps_completed": laps_completed
}])

# Prediction
pred = model.predict(X)[0]
proba = model.predict_proba(X)

print(f"\n🔮 Prediction for {DRIVER_CODE} in {RACE_NAME} {YEAR}:")
print(f"📍 Predicted Position: {pred}")

# Wahrscheinlichkeiten je Platz
print("🔢 Class Probabilities:")
for i, p in enumerate(proba[0]):
    print(f"Place {model.classes_[i]}: {round(p*100, 2)}%")

