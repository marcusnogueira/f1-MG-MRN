import os
import pandas as pd
import subprocess

# Pfade
DATA_PATH = "data/full_training_data.csv"
RAW_DATA_DIR = "data/raw/"
MODEL_PATH = "models/rf_model_full.pkl"

def get_races_in_dataset():
    if not os.path.exists(DATA_PATH):
        return set()
    df = pd.read_csv(DATA_PATH)
    return set(df['EventName'].dropna().unique())

def get_races_in_raw_data():
    return set(f.replace(".csv", "") for f in os.listdir(RAW_DATA_DIR) if f.endswith(".csv"))

if __name__ == "__main__":
    dataset_races = get_races_in_dataset()
    raw_races = get_races_in_raw_data()

    missing_races = raw_races - dataset_races

    if missing_races:
        print("🆕 Neue Rennen erkannt:", missing_races)
        print("🔄 Starte Datengenerierung...")
        subprocess.run(["python", "ml/generate_full_training_data.py"])
        print("🧠 Starte Modelltraining...")
        subprocess.run(["python", "ml/train_model_full.py"])
        print("✅ Fertig! Modell ist aktualisiert.")
    else:
        print("✅ Kein neues Rennen gefunden – nichts zu tun.")
