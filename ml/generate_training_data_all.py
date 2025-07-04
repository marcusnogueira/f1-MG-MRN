import os
import sys
import pandas as pd
import fastf1
from tqdm import tqdm

# Projektroot zum Importieren von utils hinzufügen
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from utils.feature_engineering import (
    get_track_affinity,
    get_team_strength,
    estimate_momentum
)

fastf1.Cache.enable_cache("cache")

# Konfiguration
YEAR = 2023
SESSIONS = ["R"]  # nur Rennen

output_path = "data/processed/driver_feature_data.csv"
os.makedirs("data/processed", exist_ok=True)

all_data = []

# Alle Events der Saison laden
events = fastf1.get_event_schedule(YEAR, include_testing=False)

for _, event in tqdm(events.iterrows(), total=len(events), desc=f"Lade Saison {YEAR}"):
    gp_name = event["EventName"]

    try:
        session = fastf1.get_session(YEAR, gp_name, "R")
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
                position = d_laps["Position"].iloc[-1]

                row = {
                    "year": YEAR,
                    "race": gp_name,
                    "driver": drv,
                    "fastest_lap": fastest_lap,
                    "avg_lap": avg_lap,
                    "stints": stints,
                    "pitstops": pitstops,
                    "laps_completed": laps_completed,
                    "track_affinity": get_track_affinity(gp_name, drv),
                    "team_strength": get_team_strength(team),
                    "momentum": estimate_momentum(drv),
                    "final_position": int(position)
                }

                all_data.append(row)

            except Exception as inner:
                print(f"⚠️ Fehler bei Fahrer {drv} in {gp_name}: {inner}")
                continue

    except Exception as outer:
        print(f"❌ GP {gp_name} übersprungen: {outer}")
        continue

# Speichern
df = pd.DataFrame(all_data)
df.to_csv(output_path, index=False)
print(f"✅ Gespeichert unter {output_path} mit {len(df)} Einträgen.")
