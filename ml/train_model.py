import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Daten laden
df = pd.read_csv("data/processed/driver_feature_data.csv")

# Zielvariable
y = df["final_position"].astype(int)

# Input-Features
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


# Train-Test-Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Modell
model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

# Prediction & Evaluation
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)

# Logging
log = {
    "model": "RandomForest",
    "accuracy": round(acc, 4),
    "n_train": len(X_train),
    "n_test": len(X_test)
}

# Ausgabe
print("✅ Modell trainiert")
print(f"📊 Accuracy: {log['accuracy']} on {log['n_test']} test samples")

# Speichern
os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/rf_model.pkl")

# Log speichern
log_path = "data/processed/model_performance_log.csv"
os.makedirs("data/processed", exist_ok=True)
if os.path.exists(log_path):
    old = pd.read_csv(log_path)
    log_id = len(old) + 1
    df_log = pd.concat([old, pd.DataFrame([log])], ignore_index=True)
else:
    df_log = pd.DataFrame([log])
    log_id = 1

df_log.to_csv(log_path, index=False)
print(f"🧠 Modell #{log_id} gespeichert & geloggt in {log_path}")
