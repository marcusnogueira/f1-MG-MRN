import os
import pandas as pd
import fastf1

# 🔧 Konfiguration
YEAR = 2023
RACE_NAME = "Monaco"
SESSION_TYPE = "R"

# 📁 Speicherort
os.makedirs("data/logged", exist_ok=True)
output_path = f"data/logged/results_{YEAR}_{RACE_NAME}.csv"

# 📡 Lade Session
fastf1.Cache.enable_cache("cache")
session = fastf1.get_session(YEAR, RACE_NAME, SESSION_TYPE)
session.load()

# 📊 Ergebnisse extrahieren
laps = session.laps
results = (
    laps.groupby("Driver")["Position"]
    .min()
    .reset_index()
    .rename(columns={"Position": "final_position"})
    .sort_values("final_position")
)

# 📦 Zusätzliche Metadaten
results.insert(0, "year", YEAR)
results.insert(1, "race", RACE_NAME)

# 💾 Speichern
results.to_csv(output_path, index=False)
print(f"\n✅ Ergebnisse gespeichert unter {output_path}")
print(results.head(10).to_string(index=False))
