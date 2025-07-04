import os
import sys
import pandas as pd
import fastf1
from fastf1.core import Laps
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.feature_engineering import (
    get_track_affinity,
    get_team_strength,
    estimate_momentum
)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
fastf1.Cache.enable_cache("cache")

# 📅 Konfiguration
YEARS = [2023, 2024, 2025]
SESSION_TYPE = "R"

# Heimrennen-Map
HOME_TRACKS = {
    "VER": "Netherlands",
    "LEC": "Monaco",
    "HAM": "Great Britain",
    "RUS": "Great Britain",
    "SAI": "Spain",
    "ALO": "Spain",
    "GAS": "France",
    "OCO": "France",
    "BOT": "Finland",
    "TSU": "Japan",
    "ALB": "Thailand",
    "ZHO": "China",
    "HUL": "Germany",
    "PER": "Mexico",
    "NOR": "Great Britain",
    "PIA": "Australia",
    "MAG": "Denmark"
}

all_rows = []

for year in YEARS:
    schedule = fastf1.get_event_schedule(year, include_testing=False)

    for _, row in schedule.iterrows():
        race_name = row["EventName"]
        try:
            session = fastf1.get_session(year, race_name, SESSION_TYPE)
            session.load()
            laps = session.laps.pick_quicklaps()
            if laps.empty:
                continue

            weather = session.weather_data
            results = session.results

            for drv in laps["Driver"].unique():
                d_laps = laps[laps["Driver"] == drv]
                if d_laps.empty:
                    continue

                try:
                    fastest = d_laps["LapTime"].min().total_seconds()
                    avg = d_laps["LapTime"].mean().total_seconds()
                    pitstops = d_laps["PitOutTime"].count()
                    team = d_laps["Team"].iloc[0]
                    track = session.event["EventName"]

                    # Startplatz ermitteln
                    try:
                        start_position = results[results["Abbreviation"] == drv]["GridPosition"].values[0]
                    except:
                        start_position = None

                    # Wettermittelwerte
                    try:
                        air_temp = weather["AirTemp"].mean()
                        humidity = weather["Humidity"].mean()
                        rain = weather["Rainfall"].mean()
                    except:
                        air_temp, humidity, rain = None, None, None

                    all_rows.append({
                        "year": year,
                        "race": race_name,
                        "driver": drv,
                        "team": team,
                        "fastest_lap": fastest,
                        "avg_lap": avg,
                        "pitstops": pitstops,
                        "track_affinity": get_track_affinity(race_name, drv),
                        "team_strength": get_team_strength(team),
                        "momentum": estimate_momentum(drv),
                        "start_position": start_position,
                        "air_temp": air_temp,
                        "humidity": humidity,
                        "rain": rain,
                        "home_race": 1 if HOME_TRACKS.get(drv, "") == race_name else 0,
                        "position": results[results["Abbreviation"] == drv]["Position"].values[0] if drv in results["Abbreviation"].values else None
                    })

                except Exception as e:
                    print(f"⚠️ Fehler bei Fahrer {drv} in {race_name} {year}: {e}")
        except Exception as e:
            print(f"⚠️ Fehler beim Laden von {race_name} {year}: {e}")

# 📝 Speichern
df = pd.DataFrame(all_rows)
os.makedirs("data/full/", exist_ok=True)
df.to_csv("data/full/full_training_data.csv", index=False)

print(f"\n✅ Datengenerierung abgeschlossen mit {len(df)} Einträgen.")
print(df.head())
