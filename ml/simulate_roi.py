import pandas as pd

# Daten laden
YEAR = 2023
pred = pd.read_csv(f"data/batch/predictions_{YEAR}.csv")
results = pd.read_csv(f"data/batch/actual_results_{YEAR}.csv").rename(columns={"Driver": "driver"})

# 🔢 Fiktive Quoten für Platz 1–3
odds = {1: 5.0, 2: 6.0, 3: 8.0}
stake = 10  # Einsatz pro Wette

# Nur höchste Wahrscheinlichkeit je Fahrer
top_preds = (
    pred.sort_values("probability", ascending=False)
    .groupby(["year", "race", "driver"])
    .first()
    .reset_index()
)

# Mergen mit echten Ergebnissen
merged = top_preds.merge(results, on=["year", "race", "driver"])

# Nur Top-3-Platzierungen als Wetteinsatz
bettable = merged[merged["position"] <= 3].copy()
bettable["hit"] = (bettable["position"] == bettable["final_position"]).astype(int)
bettable["odds"] = bettable["position"].map(odds)
bettable["payout"] = bettable["hit"] * bettable["odds"] * stake
bettable["cost"] = stake

# ROI berechnen
total_invest = bettable["cost"].sum()
total_return = bettable["payout"].sum()
roi = (total_return - total_invest) / total_invest

# Ausgabe
print("\n💸 ROI-Simulation (Top-3 Platzwetten)")
print(f"🎯 Treffer: {bettable['hit'].sum()} von {len(bettable)}")
print(f"💰 Total eingesetzt: {total_invest:.2f} €")
print(f"💵 Total gewonnen: {total_return:.2f} €")
print(f"📈 ROI: {roi*100:.2f} %")
