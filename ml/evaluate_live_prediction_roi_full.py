import os
import glob
import pandas as pd

# 📁 Ordner mit den Vorhersagedateien
PREDICTION_DIR = "data/live/"

# 🔍 Neueste Datei mit „_full.csv“ erkennen
prediction_files = sorted(
    glob.glob(os.path.join(PREDICTION_DIR, "predicted_probabilities_*_full.csv")),
    key=os.path.getmtime,
    reverse=True
)

if not prediction_files:
    print("❌ Keine Vorhersage-Dateien gefunden.")
    exit()

FILENAME = prediction_files[0]
print(f"📂 Verwende Vorhersage-Datei: {FILENAME}")

# 🧠 Rennen extrahieren (für spätere Anzeige)
race_info = os.path.basename(FILENAME).replace("predicted_probabilities_", "").replace("_full.csv", "")
race_info_clean = race_info.replace("_", " ")

# 📥 Laden
df = pd.read_csv(FILENAME)

# 🏦 Beispielquoten (kann durch echte Quoten ersetzt werden)
default_odds = {1: 5.0, 2: 6.0, 3: 8.0}
odds = default_odds.copy()  # TODO: Live-API später integrieren
stake = 10

# 📊 Wahrscheinlichkeiten für Position 1–3 mit ROI
top3 = df[df["position"].isin(odds.keys())].copy()
top3["odds"] = top3["position"].map(odds)
top3["payout"] = top3["odds"] * stake
top3["ev"] = (top3["probability"] / 100) * top3["payout"] - stake

# 📈 ROI berechnen
total_stake = len(top3) * stake
max_return = top3["payout"].sum()
roi_max = (max_return - total_stake) / total_stake * 100

# 🖼️ Übersicht pro Fahrer
print(f"\n🔍 Wahrscheinlichkeiten pro Fahrer (Top 10):")
for drv in df["driver"].unique():
    probs = df[df["driver"] == drv].sort_values("position")
    s = ", ".join([f"P{int(r['position'])}: {r['probability']}%" for _, r in probs.iterrows() if r['position'] <= 10])
    print(f"  {drv}: {s}")

# 🧾 Zusammenfassung
print(f"\n📈 ROI-Simulation: {race_info_clean}")
print(f"🎯 Anzahl Wetten: {len(top3)} | Einsatz gesamt: {total_stake:.2f} €")
print(f"🏆 Max Return: {max_return:.2f} € | ROI Max: {roi_max:.2f} %")

# 💡 Beste Chancen (höchster Erwartungswert)
print("\n💡 Top-Wetten (höchster Erwartungswert):")
print(top3.sort_values("ev", ascending=False)[["driver", "position", "probability", "odds", "payout", "ev"]].head(10).to_string(index=False))

print(f"\n📈 ROI-Simulation abgeschlossen für: {race_info_clean}")
