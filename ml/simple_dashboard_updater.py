#!/usr/bin/env python3
"""
Simple dashboard updater that updates race information without complex dependencies
"""

import os
import json
import pandas as pd
from datetime import datetime

def load_race_schedule():
    """Load the race schedule"""
    schedule_file = "data/live/race_schedule.json"
    if os.path.exists(schedule_file):
        with open(schedule_file, 'r') as f:
            return json.load(f)
    return []

def get_next_race(races):
    """Get the next upcoming race"""
    now = datetime.now()
    upcoming_races = []
    
    for race in races:
        if race['race_date']:
            try:
                race_time = datetime.fromisoformat(race['race_date'].replace('Z', '+00:00'))
                # Make race_time timezone naive for comparison
                race_time = race_time.replace(tzinfo=None)
                if race_time > now:
                    upcoming_races.append((race, race_time))
            except Exception as e:
                print(f"Error parsing date for {race['race_name']}: {e}")
    
    if upcoming_races:
        # Sort by date and return the next one
        upcoming_races.sort(key=lambda x: x[1])
        return upcoming_races[0][0], upcoming_races[0][1]
    
    return None, None

def update_next_race_info():
    """Update next race information for dashboard"""
    try:
        races = load_race_schedule()
        next_race, race_time = get_next_race(races)
        
        if not next_race:
            print("❌ No upcoming race found")
            return False
        
        now = datetime.now()
        time_until_race = race_time - now
        
        race_info = {
            "race_name": next_race['race_name'],
            "country": next_race['country'],
            "location": next_race['location'],
            "race_date": race_time.isoformat(),
            "race_date_formatted": race_time.strftime("%A, %B %d, %Y at %H:%M"),
            "days_until": time_until_race.days,
            "hours_until": int(time_until_race.total_seconds() // 3600),
            "minutes_until": int((time_until_race.total_seconds() % 3600) // 60),
            "is_race_weekend": time_until_race.total_seconds() < 72 * 3600,  # Within 3 days
            "is_race_day": time_until_race.total_seconds() < 24 * 3600,  # Within 1 day
            "qualifying_date": next_race.get('qualifying_date'),
            "round_number": next_race.get('round_number'),
            "last_updated": datetime.now().isoformat()
        }
        
        # Save race info
        info_file = "data/live/next_race_info.json"
        os.makedirs(os.path.dirname(info_file), exist_ok=True)
        with open(info_file, 'w') as f:
            json.dump(race_info, f, indent=2)
        
        # Create race countdown data
        countdown_data = {
            "race_name": race_info['race_name'],
            "days": race_info['days_until'],
            "hours": race_info['hours_until'] % 24,
            "minutes": race_info['minutes_until'],
            "total_hours": race_info['hours_until'],
            "is_race_weekend": race_info['is_race_weekend'],
            "is_race_day": race_info['is_race_day'],
            "last_updated": datetime.now().isoformat()
        }
        
        countdown_file = "data/live/race_countdown.json"
        with open(countdown_file, 'w') as f:
            json.dump(countdown_data, f, indent=2)
        
        print(f"✅ Updated race info: {race_info['race_name']}")
        print(f"   📍 {race_info['location']}, {race_info['country']}")
        print(f"   📅 {race_info['race_date_formatted']}")
        print(f"   ⏰ {race_info['days_until']} days, {race_info['hours_until'] % 24} hours away")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating race info: {e}")
        return False

def create_sample_odds():
    """Create sample odds data for demonstration"""
    try:
        # Sample odds for the upcoming race
        sample_odds = [
            {"driver": "Max Verstappen", "odds": 1.85, "bookmaker": "Bet365", "last_updated": "12:30"},
            {"driver": "Lando Norris", "odds": 3.20, "bookmaker": "William Hill", "last_updated": "12:25"},
            {"driver": "Charles Leclerc", "odds": 4.50, "bookmaker": "Betfair", "last_updated": "12:28"},
            {"driver": "Oscar Piastri", "odds": 6.00, "bookmaker": "Paddy Power", "last_updated": "12:20"},
            {"driver": "Carlos Sainz", "odds": 7.50, "bookmaker": "Bet365", "last_updated": "12:30"},
            {"driver": "George Russell", "odds": 9.00, "bookmaker": "William Hill", "last_updated": "12:25"},
            {"driver": "Lewis Hamilton", "odds": 12.00, "bookmaker": "Betfair", "last_updated": "12:28"},
            {"driver": "Sergio Perez", "odds": 15.00, "bookmaker": "Paddy Power", "last_updated": "12:20"}
        ]
        
        odds_df = pd.DataFrame(sample_odds)
        odds_df['odds_formatted'] = odds_df['odds'].apply(lambda x: f"{x:.2f}")
        
        odds_file = "data/live/best_odds_summary.csv"
        os.makedirs(os.path.dirname(odds_file), exist_ok=True)
        odds_df.to_csv(odds_file, index=False)
        
        print(f"✅ Created sample odds for {len(odds_df)} drivers")
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample odds: {e}")
        return False

def create_sample_value_bets():
    """Create sample value betting recommendations"""
    try:
        # Sample value bets
        value_bets = [
            {
                "driver": "Lando Norris",
                "odds": 3.20,
                "probability_pct": 35.0,
                "expected_value": 0.120,
                "bet_recommendation": "BET",
                "potential_profit": 22.00
            },
            {
                "driver": "Oscar Piastri", 
                "odds": 6.00,
                "probability_pct": 20.0,
                "expected_value": 0.200,
                "bet_recommendation": "BET",
                "potential_profit": 50.00
            },
            {
                "driver": "Charles Leclerc",
                "odds": 4.50,
                "probability_pct": 25.0,
                "expected_value": 0.125,
                "bet_recommendation": "BET",
                "potential_profit": 35.00
            }
        ]
        
        bets_df = pd.DataFrame(value_bets)
        bets_df['ev_formatted'] = bets_df['expected_value'].apply(lambda x: f"{x:.3f}")
        bets_df['odds_formatted'] = bets_df['odds'].apply(lambda x: f"{x:.2f}")
        bets_df['probability_formatted'] = bets_df['probability_pct'].apply(lambda x: f"{x:.1f}%")
        bets_df['potential_profit_formatted'] = bets_df['potential_profit'].apply(lambda x: f"€{x:.2f}")
        
        bets_file = "data/live/top_value_bets.csv"
        os.makedirs(os.path.dirname(bets_file), exist_ok=True)
        bets_df.to_csv(bets_file, index=False)
        
        print(f"✅ Created {len(bets_df)} sample value bets")
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample value bets: {e}")
        return False

def main():
    """Main function to update dashboard data"""
    print("🔄 Simple Dashboard Updater")
    print("=" * 40)
    
    success = True
    
    # Update race information
    if not update_next_race_info():
        success = False
    
    # Create sample data for demonstration
    if not create_sample_odds():
        success = False
        
    if not create_sample_value_bets():
        success = False
    
    if success:
        print("\n✅ Dashboard data update completed successfully!")
        print("\n🎯 Dashboard should now show:")
        print("   • Next race information and countdown")
        print("   • Sample betting odds")
        print("   • Sample value betting recommendations")
    else:
        print("\n❌ Some updates failed")

if __name__ == "__main__":
    main()