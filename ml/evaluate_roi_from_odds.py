import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.odds_api_fetcher import fetch_odds_for_next_f1_race
import pandas as pd


PREDICTIONS_PATH = os.path.abspath("data/live/predicted_probabilities_2025_Spanish_Grand_Prix_full.csv")

def evaluate_roi():
    # Lade ML-Vorhersagen
    df = pd.read_csv(PREDICTIONS_PATH)

    # Hole Quoten
    odds_dict = fetch_odds_for_next_f1_race()
    if not odds_dict:
        print("Keine Quoten verfügbar.")
        return

    results = []

    for _, row in df.iterrows():
        driver = row['Driver']
        prob = row['P1'] / 100  # Prozent in Dezimal
        quote = odds_dict.get(driver)

        if quote:
            implied_prob = 1 / quote
            edge = prob - implied_prob
            roi = (quote * prob - 1) * 100  # Erwarteter ROI in %

            results.append({
                "Driver": driver,
                "Predicted_Prob_P1": round(prob * 100, 2),
                "Bookmaker_Quote": quote,
                "Implied_Prob": round(implied_prob * 100, 2),
                "Edge": round(edge * 100, 2),
                "Expected_ROI_%": round(roi, 2)
            })

    roi_df = pd.DataFrame(results)
    roi_df.sort_values(by="Expected_ROI_%", ascending=False, inplace=True)

    print(roi_df)
    roi_df.to_csv("data/roi_analysis.csv", index=False)
    print("Gespeichert unter data/roi_analysis.csv ✅")

if __name__ == "__main__":
    evaluate_roi()
