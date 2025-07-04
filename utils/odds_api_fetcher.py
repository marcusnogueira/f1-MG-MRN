import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("ODDS_API_KEY")

def fetch_odds_for_next_f1_race(region="uk", market="winner"):
    url = f"https://api.the-odds-api.com/v4/sports/formula_one/odds"
    params = {
        "apiKey": API_KEY,
        "regions": region,
        "markets": market,
        "oddsFormat": "decimal",
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print("Error fetching odds:", response.status_code, response.text)
        return {}

    data = response.json()
    if not data:
        print("No odds data returned.")
        return {}

    # Nehmen wir einfach das erste Event
    event = data[0]
    outcomes = {}

    for bookmaker in event.get("bookmakers", []):
        for market in bookmaker.get("markets", []):
            for outcome in market.get("outcomes", []):
                driver = outcome.get("name")
                price = outcome.get("price")
                if driver and price:
                    outcomes[driver] = price
        break  # Nur einen Buchmacher verwenden

    return outcomes
