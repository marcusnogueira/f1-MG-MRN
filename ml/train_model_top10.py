import os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

# Daten laden
df = pd.read_csv("data/processed/driver_feature_data.csv")

# Neue Zielvariable: Top-10 erreicht (1) oder nicht (0)
df["top10"] = df["final_position"] <= 10
y = df["top10"].astype(int)

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

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Modell
model = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42)
model.fit(X_train, y_train)

# Prediction
y_pred = model.predict(X_test)

# Bewertung
acc = accuracy_score(y_test, y_pred)
print("✅ Binary Top-10-Modell trainiert")
print(f"🎯 Accuracy: {round(acc, 4)} on {len(y_test)} test samples")

print("\n🧠 Classification Report:")
print(classification_report(y_test, y_pred, target_names=["Nicht Top-10", "Top-10"]))

print("\n🧩 Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Modell speichern
os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/rf_model_top10.pkl")

# Logging
log_path = "data/processed/model_performance_log.csv"
log_entry = pd.DataFrame([{
    "model": "RF-Top10",
    "accuracy": round(acc, 4),
    "n_train": len(X_train),
    "n_test": len(X_test)
}])

if os.path.exists(log_path):
    old = pd.read_csv(log_path)
    log_df = pd.concat([old, log_entry], ignore_index=True)
else:
    log_df = log_entry

log_df.to_csv(log_path, index=False)
print(f"📁 Modell gespeichert & geloggt in {log_path}")
