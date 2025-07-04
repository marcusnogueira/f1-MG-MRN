import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

# Daten laden
df = pd.read_csv("data/processed/driver_feature_data.csv")

# Ziel: Platzierung (z. B. 1.0, 4.0, 11.0)
y = df["final_position"]

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
model = RandomForestRegressor(n_estimators=250, max_depth=10, random_state=42)
model.fit(X_train, y_train)

# Vorhersage
y_pred = model.predict(X_test)

# Fehlermetriken
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print("✅ Regressionsmodell trainiert")
print(f"📊 MAE:  {round(mae, 3)}")
print(f"📉 RMSE: {round(rmse, 3)}")

# Modell speichern
os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/rf_model_regression.pkl")

# Logging
log_path = "data/processed/model_performance_log.csv"
log_entry = pd.DataFrame([{
    "model": "RF-Regression",
    "accuracy": None,
    "mae": round(mae, 3),
    "rmse": round(rmse, 3),
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
