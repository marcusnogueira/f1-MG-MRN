import requests
import pandas as pd
import os

ODDS_API_KEY = os.getenv("2f9fca6868ae22ca7596e457d8ce7020")  
ODDS_API_URL = "https://api.the-odds-api.com/v4/sports/formula_1/odds/"

def fetch_f1_odds(api_key=ODDS_API_KEY, region="eu", market="outrights"):
    params = {
        "apiKey": api_key,
        "regions": region,
        "markets": market,
    }
    response = requests.get(ODDS_API_URL, params=params)
    if response.status_code != 200:
        raise Exception(f"API request failed: {response.status_code} {response.text}")

    data = response.json()
    odds_data = []

    for entry in data:
        for bookmaker in entry.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                for outcome in market.get("outcomes", []):
                    odds_data.append({
                        "driver": outcome["name"],
                        "odds": outcome["price"],
                        "bookmaker": bookmaker["title"],
                        "market": market["key"],
                        "event": entry["home_team"] + " vs " + entry.get("away_team", "") if entry.get("away_team") else entry.get("home_team")
                    })

    return pd.DataFrame(odds_data)

def save_odds_to_csv(df, path="data/live/odds_latest.csv"):
    df.to_csv(path, index=False)
    print(f"✅ Wettquoten gespeichert unter: {path}")

if __name__ == "__main__":
    df_odds = fetch_f1_odds()
    save_odds_to_csv(df_odds)
