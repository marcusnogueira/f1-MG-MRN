#!/usr/bin/env python3
"""
Quick script to fetch and update the current F1 race schedule
"""

import os
import json
import pandas as pd
from datetime import datetime
try:
    import fastf1
except ImportError:
    print("FastF1 not available, using fallback schedule")
    fastf1 = None

def get_2025_f1_schedule_fallback():
    """Fallback F1 2025 schedule if FastF1 is not available"""
    return [
        {
            "race_name": "Australian Grand Prix",
            "country": "Australia", 
            "location": "Melbourne",
            "race_date": "2025-03-16T05:00:00+00:00",
            "qualifying_date": "2025-03-15T06:00:00+00:00",
            "round_number": 1
        },
        {
            "race_name": "Chinese Grand Prix",
            "country": "China",
            "location": "Shanghai", 
            "race_date": "2025-03-23T07:00:00+00:00",
            "qualifying_date": "2025-03-22T08:00:00+00:00",
            "round_number": 2
        },
        {
            "race_name": "Japanese Grand Prix",
            "country": "Japan",
            "location": "Suzuka",
            "race_date": "2025-04-06T05:00:00+00:00", 
            "qualifying_date": "2025-04-05T06:00:00+00:00",
            "round_number": 3
        },
        {
            "race_name": "Bahrain Grand Prix",
            "country": "Bahrain",
            "location": "Sakhir",
            "race_date": "2025-04-13T15:00:00+00:00",
            "qualifying_date": "2025-04-12T16:00:00+00:00", 
            "round_number": 4
        },
        {
            "race_name": "Saudi Arabian Grand Prix",
            "country": "Saudi Arabia",
            "location": "Jeddah",
            "race_date": "2025-04-20T17:00:00+00:00",
            "qualifying_date": "2025-04-19T18:00:00+00:00",
            "round_number": 5
        },
        {
            "race_name": "Miami Grand Prix",
            "country": "United States",
            "location": "Miami",
            "race_date": "2025-05-04T19:30:00+00:00",
            "qualifying_date": "2025-05-03T20:00:00+00:00",
            "round_number": 6
        }
    ]

def get_current_f1_schedule():
    """Get current F1 season schedule"""
    try:
        if fastf1 is None:
            print("Using fallback schedule...")
            return get_2025_f1_schedule_fallback()
            
        current_year = datetime.now().year
        print(f"Fetching F1 {current_year} schedule...")
        
        schedule = fastf1.get_event_schedule(current_year, include_testing=False)
        
        # Convert to our format
        races = []
        for _, race in schedule.iterrows():
            race_data = {
                "race_name": race['EventName'],
                "country": race['Country'],
                "location": race['Location'],
                "race_date": race['Session5Date'].isoformat() if pd.notna(race['Session5Date']) else None,
                "qualifying_date": race['Session4Date'].isoformat() if pd.notna(race['Session4Date']) else None,
                "practice_dates": {
                    "fp1": race['Session1Date'].isoformat() if pd.notna(race['Session1Date']) else None,
                    "fp2": race['Session2Date'].isoformat() if pd.notna(race['Session2Date']) else None,
                    "fp3": race['Session3Date'].isoformat() if pd.notna(race['Session3Date']) else None
                },
                "round_number": race['RoundNumber']
            }
            races.append(race_data)
        
        print(f"✅ Fetched {len(races)} races for {current_year}")
        return races
        
    except Exception as e:
        print(f"Error fetching F1 schedule: {e}")
        print("Using fallback schedule...")
        return get_2025_f1_schedule_fallback()

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

def main():
    """Main function to update race schedule"""
    print("🏎️  F1 Race Schedule Updater")
    print("=" * 40)
    
    # Get current schedule
    races = get_current_f1_schedule()
    
    if not races:
        print("❌ No races found")
        return
    
    # Save schedule
    schedule_file = "data/live/race_schedule.json"
    os.makedirs(os.path.dirname(schedule_file), exist_ok=True)
    
    with open(schedule_file, 'w') as f:
        json.dump(races, f, indent=2)
    
    print(f"💾 Saved schedule to {schedule_file}")
    
    # Show next race
    next_race, race_time = get_next_race(races)
    
    if next_race:
        time_until = race_time - datetime.now()
        days = time_until.days
        hours = int(time_until.total_seconds() // 3600) % 24
        
        print("\n🏁 Next Race:")
        print(f"   {next_race['race_name']}")
        print(f"   📍 {next_race['location']}, {next_race['country']}")
        print(f"   📅 {race_time.strftime('%A, %B %d, %Y at %H:%M')}")
        print(f"   ⏰ {days} days, {hours} hours away")
        
        if time_until.total_seconds() < 7 * 24 * 3600:  # Within a week
            print(f"   🔥 Race week! Time to get ready!")
    else:
        print("\n❌ No upcoming races found")
    
    print("\n✅ Schedule update complete!")

if __name__ == "__main__":
    main()