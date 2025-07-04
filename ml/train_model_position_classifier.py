import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Daten laden
df = pd.read_csv("data/processed/driver_feature_data.csv")

# Ziel: Platz (Integer 1–20) → Klassifikation
y = df["final_position"].astype(int)

# Features
X = df[[
    "fastest_lap",
    "avg_lap",
    "stints",
    "pitstops",
    "laps_completed",
    "track_affinity",
    "team_strength",
    "momentum"
]]

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Modell
model = RandomForestClassifier(n_estimators=300, max_depth=10, random_state=42)
model.fit(X_train, y_train)

# Evaluation
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"✅ Platz-Klassifizierungsmodell trainiert")
print(f"🎯 Accuracy (exakter Platz): {round(acc, 4)}")

# Speichern
os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/rf_model_position_classifier.pkl")
