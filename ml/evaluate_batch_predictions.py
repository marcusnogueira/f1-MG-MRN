import pandas as pd
import os

# Daten laden
YEAR = 2023
pred_path = f"data/batch/predictions_{YEAR}.csv"
results_path = f"data/batch/actual_results_{YEAR}.csv"

pred = pd.read_csv(pred_path)
true = pd.read_csv(results_path)

# Für Position mit höchster Wahrscheinlichkeit je Fahrer
top_preds = (
    pred.sort_values("probability", ascending=False)
    .groupby(["year", "race", "driver"])
    .first()
    .reset_index()
    .rename(columns={"position": "predicted_position"})
)

# Ergebnisse zuordnen
merged = top_preds.merge(true.rename(columns={"Driver": "driver"}), on=["year", "race", "driver"])
merged["abs_error"] = (merged["predicted_position"] - merged["final_position"]).abs()

# Bewertung
mae = merged["abs_error"].mean()
top3_pred = (
    merged.sort_values("predicted_position")
    .groupby(["year", "race"])
    .head(3)
)
top3_true = (
    merged.sort_values("final_position")
    .groupby(["year", "race"])
    .head(3)
)

top10_pred = (
    merged.sort_values("predicted_position")
    .groupby(["year", "race"])
    .head(10)
)
top10_true = (
    merged.sort_values("final_position")
    .groupby(["year", "race"])
    .head(10)
)

def intersection_count(df1, df2):
    return len(set(df1["driver"]) & set(df2["driver"]))

top3_hits = intersection_count(top3_pred, top3_true)
top10_hits = intersection_count(top10_pred, top10_true)

print(f"\n📊 Evaluation der Predictions {YEAR}:")
print(f"👥 Fahrer insgesamt: {len(merged)}")
print(f"📉 MAE (Ø Fehler in Platzierung): {round(mae, 2)}")
print(f"🥉 Top 3 richtig (gesamt): {top3_hits}")
print(f"🔟 Top 10 richtig (gesamt): {top10_hits}")

# Optional: speichern zur späteren Analyse
out_path = f"data/batch/evaluation_{YEAR}.csv"
os.makedirs("data/batch", exist_ok=True)
merged.to_csv(out_path, index=False)
print(f"✅ Evaluation gespeichert unter: {out_path}")
