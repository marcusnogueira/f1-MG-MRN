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

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
fastf1.Cache.enable_cache("cache")

# 🧠 Modell & Feature Setup
MODEL_PATH = "models/rf_model_full.pkl"
FEATURES = [
    "fastest_lap", "avg_lap", "pitstops", "track_affinity",
    "team_strength", "momentum", "start_position",
    "air_temp", "humidity", "rain", "home_race"
]

# 📅 Jahr & Session
YEAR = 2025
SESSION_TYPE = "R"
HOME_TRACKS = {
    "VER": "Netherlands", "LEC": "Monaco", "HAM": "Great Britain", "RUS": "Great Britain",
    "SAI": "Spain", "ALO": "Spain", "GAS": "France", "OCO": "France", "BOT": "Finland",
    "TSU": "Japan", "ALB": "Thailand", "ZHO": "China", "HUL": "Germany", "PER": "Mexico",
    "NOR": "Great Britain", "PIA": "Australia", "MAG": "Denmark"
}

# 📅 Letztes beendetes Rennen finden
schedule = fastf1.get_event_schedule(YEAR)
now = pd.Timestamp.now(tz="UTC")
available = schedule[schedule["Session5Date"] < now]

if available.empty:
    print("⚠️ Noch kein Rennen abgeschlossen in dieser Saison.")
    exit()

race_name = available.iloc[-1]["EventName"]
print(f"\n🟢 Live-Vorhersage für: {race_name} {YEAR}")

# 🧠 Modell laden
model = joblib.load(MODEL_PATH)

# 📥 Daten abrufen
session = fastf1.get_session(YEAR, race_name, SESSION_TYPE)
session.load()
laps = session.laps.pick_quicklaps()
results = session.results
weather = session.weather_data
drivers = laps["Driver"].unique()

# 📊 Features erzeugen
rows = []

for drv in drivers:
    d_laps = laps[laps["Driver"] == drv]
    if d_laps.empty: continue

    try:
        fastest = d_laps["LapTime"].min().total_seconds()
        avg = d_laps["LapTime"].mean().total_seconds()
        pitstops = d_laps["PitOutTime"].count()
        team = d_laps["Team"].iloc[0]

        start_pos = results[results["Abbreviation"] == drv]["GridPosition"].values[0] if drv in results["Abbreviation"].values else None
        air_temp = weather["AirTemp"].mean() if not weather.empty else None
        humidity = weather["Humidity"].mean() if not weather.empty else None
        rain = weather["Rainfall"].mean() if not weather.empty else None
        home = 1 if HOME_TRACKS.get(drv, "") == race_name else 0

        X = pd.DataFrame([{
            "fastest_lap": fastest,
            "avg_lap": avg,
            "pitstops": pitstops,
            "track_affinity": get_track_affinity(race_name, drv),
            "team_strength": get_team_strength(team),
            "momentum": estimate_momentum(drv),
            "start_position": start_pos,
            "air_temp": air_temp,
            "humidity": humidity,
            "rain": rain,
            "home_race": home
        }])

        proba = model.predict_proba(X)[0]
        for i, p in enumerate(proba, start=1):
            rows.append({
                "year": YEAR,
                "race": race_name,
                "driver": drv,
                "position": i,
                "probability": round(p * 100, 2)
            })

    except Exception as e:
        print(f"⚠️ Fehler bei {drv}: {e}")

# 💾 Speichern
df = pd.DataFrame(rows)
os.makedirs("data/live", exist_ok=True)
path = f"data/live/predicted_probabilities_{YEAR}_{race_name.replace(' ', '_')}_full.csv"
df.to_csv(path, index=False)

print(f"\n✅ Vorhersage gespeichert: {path}")
print(df[df["position"] <= 3].sort_values(by="probability", ascending=False).head(10))
