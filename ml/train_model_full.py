import os
import sys
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Import-Fix
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 📥 Daten laden
DATA_PATH = "data/full/full_training_data.csv"
df = pd.read_csv(DATA_PATH)

# 🧹 Features & Zielspalte
features = [
    "fastest_lap", "avg_lap", "pitstops", "track_affinity",
    "team_strength", "momentum", "start_position",
    "air_temp", "humidity", "rain", "home_race"
]

target = "position"

# 🔁 Fehlende Werte entfernen
df = df.dropna(subset=features + [target])

# 🧪 Trainingssplit
X = df[features]
y = df[target].astype(int)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 🧠 Modell trainieren
model = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
model.fit(X_train, y_train)

# 📊 Auswertung
y_pred = model.predict(X_test)
print("\n📈 Modellbewertung (Testdaten):")
print(classification_report(y_test, y_pred))

# 💾 Speichern
os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/rf_model_full.pkl")
print("\n✅ Modell gespeichert unter: models/rf_model_full.pkl")
