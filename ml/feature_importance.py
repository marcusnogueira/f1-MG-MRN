import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

# Lade das Modell
model = joblib.load("models/rf_model.pkl")

# Lade das Trainings-Feature-Set
df = pd.read_csv("data/processed/driver_feature_data.csv")
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


# Extrahiere Feature-Importances
importances = model.feature_importances_
features = X.columns
print(f"Features: {len(features)}, Importances: {len(importances)}")
importance_df = pd.DataFrame({"feature": features, "importance": importances})
importance_df = importance_df.sort_values(by="importance", ascending=False)

# 📊 Plotten
plt.figure(figsize=(10, 6))
sns.barplot(x="importance", y="feature", data=importance_df, palette="Blues_d")
plt.title("Feature Importance – Random Forest")
plt.tight_layout()
plt.savefig("data/processed/feature_importance_plot.png")
plt.show()

# 💾 CSV speichern
importance_df.to_csv("data/processed/feature_importance.csv", index=False)
print("✅ Feature Importances gespeichert.")
