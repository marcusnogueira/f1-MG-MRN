import pandas as pd
import numpy as np
import os
from typing import Dict, List, Tuple

def calculate_expected_value(probability: float, odds: float, stake: float = 1.0) -> float:
    """
    Berechnet den Expected Value (EV) einer Wette.
    
    Args:
        probability: Wahrscheinlichkeit des Ereignisses (0-1)
        odds: Wettquote (Dezimal)
        stake: Einsatz (Standard: 1€)
    
    Returns:
        Expected Value in €
    """
    win_amount = odds * stake
    lose_amount = stake
    
    ev = (probability * win_amount) - ((1 - probability) * lose_amount)
    return ev

def calculate_value_bets(probabilities_df: pd.DataFrame, odds_dict: Dict[str, float], 
                        positions: List[int] = [1, 2, 3], stake: float = 10.0) -> pd.DataFrame:
    """
    Berechnet Value Bets für P1, P2, P3 basierend auf Wahrscheinlichkeiten und Quoten.
    
    Args:
        probabilities_df: DataFrame mit Spalten ['driver', 'position', 'probability']
        odds_dict: Dictionary mit {driver: odds} für die jeweilige Position
        positions: Liste der Positionen für die Berechnung
        stake: Einsatz pro Wette
    
    Returns:
        DataFrame mit Value Bet Empfehlungen
    """
    results = []
    
    for position in positions:
        pos_data = probabilities_df[probabilities_df['position'] == position].copy()
        
        for _, row in pos_data.iterrows():
            driver = row['driver']
            probability = row['probability'] / 100.0  # Convert percentage to decimal
            
            if driver in odds_dict:
                odds = odds_dict[driver]
                ev = calculate_expected_value(probability, odds, stake)
                
                results.append({
                    'driver': driver,
                    'position': f'P{position}',
                    'probability': row['probability'],
                    'odds': odds,
                    'stake': stake,
                    'expected_value': round(ev, 2),
                    'recommendation': 'BET' if ev > 0 else 'SKIP'
                })
    
    return pd.DataFrame(results)

def analyze_value_bets_from_files(probabilities_file: str, odds_file: str, 
                                 output_file: str = "data/live/value_bets.csv") -> pd.DataFrame:
    """
    Lädt Wahrscheinlichkeiten und Quoten aus Dateien und berechnet Value Bets.
    
    Args:
        probabilities_file: Pfad zur Wahrscheinlichkeits-CSV
        odds_file: Pfad zur Quoten-CSV
        output_file: Pfad für die Ausgabe-CSV
    
    Returns:
        DataFrame mit Value Bet Analyse
    """
    # Lade Wahrscheinlichkeiten
    if not os.path.exists(probabilities_file):
        raise FileNotFoundError(f"Wahrscheinlichkeits-Datei nicht gefunden: {probabilities_file}")
    
    prob_df = pd.read_csv(probabilities_file)
    
    # Lade Quoten
    if not os.path.exists(odds_file):
        raise FileNotFoundError(f"Quoten-Datei nicht gefunden: {odds_file}")
    
    odds_df = pd.read_csv(odds_file)
    odds_dict = dict(zip(odds_df['driver'], odds_df['odds']))
    
    # Berechne Value Bets
    value_bets = calculate_value_bets(prob_df, odds_dict)
    
    # Speichere Ergebnisse
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    value_bets.to_csv(output_file, index=False)
    
    print(f"✅ Value Bets gespeichert unter: {output_file}")
    print(f"📊 {len(value_bets[value_bets['recommendation'] == 'BET'])} profitable Wetten gefunden")
    
    return value_bets

def create_sample_odds_file(output_path: str = "data/live/sample_odds.csv"):
    """
    Erstellt eine Beispiel-Quoten-Datei für Tests.
    """
    sample_odds = {
        'VER': 1.8,
        'HAM': 4.5,
        'LEC': 6.0,
        'RUS': 8.0,
        'ALO': 12.0,
        'SAI': 15.0,
        'NOR': 20.0,
        'PIA': 25.0,
        'GAS': 30.0,
        'OCO': 35.0
    }
    
    odds_df = pd.DataFrame(list(sample_odds.items()), columns=['driver', 'odds'])
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    odds_df.to_csv(output_path, index=False)
    print(f"✅ Beispiel-Quoten erstellt: {output_path}")

if __name__ == "__main__":
    # Beispiel-Verwendung
    YEAR = 2025
    RACE = "Spanish_Grand_Prix_full"
    
    prob_file = f"data/live/predicted_probabilities_{YEAR}_{RACE}.csv"
    odds_file = "data/live/sample_odds.csv"
    
    # Erstelle Beispiel-Quoten falls nicht vorhanden
    if not os.path.exists(odds_file):
        create_sample_odds_file(odds_file)
    
    # Berechne Value Bets
    try:
        value_bets = analyze_value_bets_from_files(prob_file, odds_file)
        print("\n📋 Top Value Bets:")
        top_bets = value_bets[value_bets['recommendation'] == 'BET'].sort_values('expected_value', ascending=False)
        print(top_bets.head(10).to_string(index=False))
    except FileNotFoundError as e:
        print(f"❌ Fehler: {e}")