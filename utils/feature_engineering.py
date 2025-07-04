import pandas as pd
import numpy as np

# 🧠 Historische Track-Affinity aus echten Resultaten
# Format: {(Race, Driver): avg_position}
TRACK_RESULTS = {
    ("Monaco", "VER"): 1.5,
    ("Monaco", "HAM"): 2.2,
    ("Monaco", "LEC"): 5.8,
    ("Monaco", "ALO"): 4.1,
    ("Monaco", "SAI"): 5.0,
    # ... ggf. mehr hinzufügen
}

# Simulierter Momentum-Speicher aus vorherigen Rennen
LAST_FINISHES = {
    "VER": [1, 1, 3],
    "HAM": [4, 2, 5],
    "LEC": [6, 5, 7],
    "ALO": [4, 6, 4],
    "SAI": [8, 10, 9],
    "RUS": [3, 2, 5],
    # ...
}

TEAM_STRENGTH = {
    "Red Bull": 1.0,
    "Mercedes": 0.9,
    "Ferrari": 0.85,
    "Aston Martin": 0.8,
    "McLaren": 0.75,
    "Alpine": 0.7,
    "Williams": 0.5,
    "Haas": 0.45,
    "Alfa Romeo": 0.4,
    "AlphaTauri": 0.4,
}

def get_track_affinity(race: str, driver: str) -> float:
    return 1.0 / TRACK_RESULTS.get((race, driver), 10.0)

def get_team_strength(team: str) -> float:
    return TEAM_STRENGTH.get(team, 0.5)

def estimate_momentum(driver: str) -> float:
    history = LAST_FINISHES.get(driver, [10, 10, 10])
    return 1.0 / (np.mean(history) + 1e-6)  # besser = höherer Score
