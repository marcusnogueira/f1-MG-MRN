import pandas as pd

# Daten einlesen
df = pd.read_csv("data/processed/predicted_positions_regression.csv")

# Sortieren nach erwarteter Zielposition
df_sorted = df.sort_values(by="expected_position")

# Top 3
top_3 = df_sorted.head(3)
print("\n🏆 Top 3 Prediction:")
print(top_3[["driver", "expected_position"]].to_string(index=False))

# Top 10
top_10 = df_sorted.head(10)
print("\n🔟 Top 10 Prediction:")
print(top_10[["driver", "expected_position"]].to_string(index=False))

# Underdogs (Platz 11+)
underdogs = df_sorted[df_sorted["expected_position"] > 10]
print("\n🎯 Underdog Candidates (Expected > 10):")
print(underdogs[["driver", "expected_position"]].to_string(index=False))

# Optional: als Datei speichern
out_path = "data/processed/generated_ranking_summary.csv"
df_sorted.to_csv(out_path, index=False)
print(f"\n✅ Ranking-Übersicht gespeichert unter: {out_path}")
