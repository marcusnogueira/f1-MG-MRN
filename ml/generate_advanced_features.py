import pandas as pd
import numpy as np
import os

# Eingabedatei (z. B. von generate_training_data_all.py erzeugt)
INPUT_FILE = "data/processed/driver_feature_data.csv"
OUTPUT_FILE = "data/processed/driver_feature_data_advanced.csv"

if not os.path.exists(INPUT_FILE):
    print(f"❌ Eingabedatei nicht gefunden: {INPUT_FILE}")
    exit()

# Daten laden
df = pd.read_csv(INPUT_FILE)

# -----------------------------
# 📌 Neue Feature-Generierung
# -----------------------------

# 1. Relativer Startplatzverlust/Gewinn (Delta)
df["position_delta"] = df["start_position"] - df["position"]

# 2. Platzierungskategorie (P1–P5, P6–P10, P11–P15, P16–P20)
def categorize_position(pos):
    if pos <= 5:
        return "P1-5"
    elif pos <= 10:
        return "P6-10"
    elif pos <= 15:
        return "P11-15"
    else:
        return "P16-20"
df["position_group"] = df["position"].apply(categorize_position)

# 3. Erfahrung des Fahrers (Anzahl Rennen bisher)
df["driver_race_count"] = (
    df.groupby("driver").cumcount()
)

# 4. Team-Form der letzten 3 Rennen (durchschnittliche Position aller Fahrer im Team)
df["team_avg_pos"] = df.groupby(["team"])["position"].transform(lambda x: x.rolling(window=3, min_periods=1).mean())

# 5. Stability Score – wie stabil fährt ein Fahrer (Varianz in den letzten 3 Rennen)
def stability(x):
    return x.rolling(window=3, min_periods=1).std()
df["stability"] = df.groupby("driver")["position"].transform(stability)

# 6. Wetterindikator: Hitzetage / Regenrennen / Normale Bedingungen
conditions = [
    (df["air_temp"] >= 30),
    (df["rain"] > 0),
]
choices = ["hot", "rain"]
df["weather_condition"] = np.select(conditions, choices, default="normal")

# -----------------------------
# 📤 Speichern
# -----------------------------
df.to_csv(OUTPUT_FILE, index=False)
print(f"✅ Neue Features gespeichert unter: {OUTPUT_FILE}")
