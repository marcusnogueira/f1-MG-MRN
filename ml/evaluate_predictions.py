import pandas as pd
import fastf1
import os

# Evaluation für Monaco 2023
RACE_NAME = "Monaco"
YEAR = 2023
PREDICTION_PATH = "data/processed/predicted_driver_positions.csv"

# FastF1 Daten holen (echte Ergebnisse)
fastf1.Cache.enable_cache("cache")
event = fastf1.get_event(YEAR, RACE_NAME)
session = event.get_session("R")
session.load()

# Ergebnis laden
results = session.results[["Abbreviation", "Position"]].copy()
results["Position"] = results["Position"].astype(int)

# Vorhersagen laden
preds = pd.read_csv(PREDICTION_PATH)
preds.rename(columns={"driver": "Abbreviation"}, inplace=True)

# Merge
df = pd.merge(preds, results, on="Abbreviation", how="inner")

# Bewertung
def evaluate(row):
    pred = row["predicted_position"]
    actual = row["Position"]
    return pd.Series({
        "hit_top_1": int(pred == actual),
        "hit_top_3": int(actual <= 3 and pred <= 3),
        "hit_top_10": int(actual <= 10 and pred <= 10)
    })

df = pd.concat([df, df.apply(evaluate, axis=1)], axis=1)

# Stats
total = len(df)
top_1 = df["hit_top_1"].sum()
top_3 = df["hit_top_3"].sum()
top_10 = df["hit_top_10"].sum()

print(f"\n📊 Evaluation für {RACE_NAME} {YEAR}:")
print(f"🔹 Fahrer insgesamt: {total}")
print(f"🥇 Genau richtige Platzierung: {top_1} ({round(top_1/total*100,1)}%)")
print(f"🥉 Top-3 korrekt vorhergesagt: {top_3} ({round(top_3/total*100,1)}%)")
print(f"🔟 Top-10 korrekt vorhergesagt: {top_10} ({round(top_10/total*100,1)}%)")

# Optional speichern
df.to_csv("data/processed/evaluation_results.csv", index=False)
