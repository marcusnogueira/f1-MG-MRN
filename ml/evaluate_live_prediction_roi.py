import os
import pandas as pd

# 📂 Konfiguration
YEAR = 2025
RACE_NAME = "Spanish Grand Prix"
FILENAME = f"data/live/predicted_probabilities_{YEAR}_{RACE_NAME}.csv"

# 📈 Fiktive Wettquoten
odds = {1: 5.0, 2: 6.0, 3: 8.0}
stake = 10  # € Einsatz pro Wette

# 📥 Daten laden
if not os.path.exists(FILENAME):
    print(f"❌ Datei nicht gefunden: {FILENAME}")
    exit()

df = pd.read_csv(FILENAME)

# 📊 Nur Top-Prognose je Fahrer
top_preds = (
    df.sort_values("probability", ascending=False)
    .groupby("driver")
    .first()
    .reset_index()
)

# 🎯 Nur Platz 1–3 werden als Wette betrachtet
bettable = top_preds[top_preds["position"].isin([1, 2, 3])].copy()
bettable["odds"] = bettable["position"].map(odds)
bettable["cost"] = stake
bettable["hit"] = 0  # Live-Ergebnis noch unbekannt (Simulation)
bettable["payout"] = bettable["odds"] * stake

# 📈 ROI-Berechnung (simuliert: alle wetten gewinnen = maximaler ROI)
total_invest = bettable["cost"].sum()
total_return = bettable["payout"].sum()
roi = (total_return - total_invest) / total_invest

# 📊 Ausgabe
print(f"\n📊 ROI-Vorschau: {RACE_NAME} {YEAR}")
print(f"🧾 Anzahl Wetten: {len(bettable)}")
print(f"💰 Einsatz gesamt: {total_invest:.2f} €")
print(f"🏆 Möglicher Gewinn: {total_return:.2f} €")
print(f"📈 Max. ROI (wenn alles trifft): {roi*100:.2f} %")

# Optional: Wetten anzeigen
print("\n🎯 Platzierte Wetten:")
print(bettable[["driver", "position", "probability", "odds", "payout"]].sort_values(by="probability", ascending=False))
