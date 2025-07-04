import pandas as pd
from fastf1 import get_session
from fastf1.core import Laps

# Prediction laden
pred_path = "data/processed/predicted_positions_regression.csv"
pred_df = pd.read_csv(pred_path)

# Session laden (wir nutzen Monaco 2023)
session = get_session(2023, "Monaco", "R")
session.load()
laps = session.laps

# Beste Platzierung pro Fahrer (echtes Ergebnis)
results = (
    laps.groupby("Driver")["Position"]
    .min()
    .reset_index()
    .rename(columns={"Position": "actual_position"})
)

# Join mit Prediction
merged = pred_df.merge(results, how="inner", left_on="driver", right_on="Driver")

# Fehler berechnen
merged["abs_error"] = (merged["expected_position"] - merged["actual_position"]).abs()

# Durchschnittlicher Fehler
mae = merged["abs_error"].mean()

# Trefferquote
top3_actual = set(merged.sort_values("actual_position").head(3)["driver"])
top3_pred = set(merged.sort_values("expected_position").head(3)["driver"])
top10_actual = set(merged.sort_values("actual_position").head(10)["driver"])
top10_pred = set(merged.sort_values("expected_position").head(10)["driver"])

top3_hits = len(top3_actual & top3_pred)
top10_hits = len(top10_actual & top10_pred)

# Ausgabe
print("\n📊 Regression Evaluation für Monaco 2023:")
print(f"👥 Fahrer ausgewertet: {len(merged)}")
print(f"📉 MAE (Ø Fehler in Positionen): {mae:.2f}")
print(f"🥉 Top 3 Treffer: {top3_hits} von 3")
print(f"🔟 Top 10 Treffer: {top10_hits} von 10")

# Detaillierter Fehler je Fahrer (optional)
print("\n❌ Größte Abweichungen:")
print(merged.sort_values("abs_error", ascending=False)[["driver", "expected_position", "actual_position", "abs_error"]].head(5).to_string(index=False))
