#!/usr/bin/env python3
"""
F1 Race Timing and Odds Fetching Demo

This script demonstrates how the automated F1 betting system handles:
1. Race schedule monitoring
2. Automatic odds fetching timing
3. Prediction generation timing
4. Post-race result processing
"""

import os
import json
from datetime import datetime, timedelta

def get_example_next_race():
    """Get an example next F1 race (using 2025 Australian GP as example)"""
    # Example: 2025 Australian Grand Prix
    return {
        'name': '2025 Australian Grand Prix',
        'location': 'Melbourne',
        'country': 'Australia', 
        'date': datetime(2025, 3, 16, 6, 0),  # March 16, 2025 at 6:00 AM local time
        'round': 1
    }

def calculate_timing_windows(race_date):
    """Calculate when different automated actions will trigger"""
    now = datetime.now()
    
    # Configuration from auto_race_monitor.py
    odds_fetch_hours = [72, 48, 24, 12, 6, 2]  # Hours before race
    prediction_hours = 24  # Hours before race
    result_process_hours = 4  # Hours after race
    
    timing_info = {
        'race_date': race_date,
        'current_time': now,
        'hours_until_race': (race_date - now).total_seconds() / 3600,
        'odds_fetch_windows': [],
        'prediction_window': None,
        'result_processing_window': None
    }
    
    # Calculate odds fetching windows
    for hours_before in odds_fetch_hours:
        fetch_time = race_date - timedelta(hours=hours_before)
        window_start = fetch_time - timedelta(hours=1)
        window_end = fetch_time + timedelta(hours=1)
        
        timing_info['odds_fetch_windows'].append({
            'hours_before_race': hours_before,
            'target_time': fetch_time,
            'window_start': window_start,
            'window_end': window_end,
            'is_active': window_start <= now <= window_end,
            'is_upcoming': now < window_start
        })
    
    # Calculate prediction window
    pred_time = race_date - timedelta(hours=prediction_hours)
    pred_window_start = pred_time - timedelta(hours=1)
    pred_window_end = pred_time + timedelta(hours=1)
    
    timing_info['prediction_window'] = {
        'hours_before_race': prediction_hours,
        'target_time': pred_time,
        'window_start': pred_window_start,
        'window_end': pred_window_end,
        'is_active': pred_window_start <= now <= pred_window_end,
        'is_upcoming': now < pred_window_start
    }
    
    # Calculate result processing window
    result_time = race_date + timedelta(hours=result_process_hours)
    timing_info['result_processing_window'] = {
        'hours_after_race': result_process_hours,
        'target_time': result_time,
        'is_active': race_date <= now <= result_time,
        'is_upcoming': now < race_date
    }
    
    return timing_info

def print_timing_summary(timing_info, race_info):
    """Print a human-readable summary of the timing information"""
    print("\n🏎️  F1 AUTOMATED BETTING SYSTEM - TIMING OVERVIEW")
    print("=" * 60)
    
    race_date = timing_info['race_date']
    hours_until = timing_info['hours_until_race']
    
    print(f"\n🏁 Next Race: {race_info['name']}")
    print(f"📍 Location: {race_info['location']}, {race_info['country']}")
    print(f"📅 Date: {race_date.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if hours_until > 0:
        days = int(hours_until // 24)
        remaining_hours = int(hours_until % 24)
        print(f"⏰ Time until race: {days} days, {remaining_hours} hours")
    else:
        print(f"🏁 Race finished {abs(hours_until):.1f} hours ago")
    
    print("\n📊 ODDS FETCHING SCHEDULE:")
    print("-" * 40)
    print("The system automatically fetches odds at these times:")
    
    for i, window in enumerate(timing_info['odds_fetch_windows']):
        if window['is_active']:
            status = "🟢 ACTIVE NOW - Fetching odds!"
        elif window['is_upcoming']:
            status = "🔵 UPCOMING"
        else:
            status = "⚪ PASSED"
        
        print(f"{window['hours_before_race']:2d}h before race: {window['target_time'].strftime('%m-%d %H:%M')} {status}")
    
    print("\n🤖 PREDICTION GENERATION:")
    print("-" * 40)
    pred_window = timing_info['prediction_window']
    if pred_window['is_active']:
        pred_status = "🟢 ACTIVE NOW - Generating predictions!"
    elif pred_window['is_upcoming']:
        pred_status = "🔵 UPCOMING"
    else:
        pred_status = "⚪ PASSED"
    
    print(f"{pred_window['hours_before_race']:2d}h before race: {pred_window['target_time'].strftime('%m-%d %H:%M')} {pred_status}")
    
    print("\n📈 RESULT PROCESSING:")
    print("-" * 40)
    result_window = timing_info['result_processing_window']
    if result_window['is_active']:
        result_status = "🟢 ACTIVE NOW - Processing results!"
    elif result_window['is_upcoming']:
        result_status = "🔵 UPCOMING"
    else:
        result_status = "⚪ PASSED"
    
    print(f"{result_window['hours_after_race']:2d}h after race: {result_window['target_time'].strftime('%m-%d %H:%M')} {result_status}")
    
    print("\n💡 HOW THE AUTOMATION WORKS:")
    print("-" * 40)
    print("• 🔄 System checks every 6 hours + every 30 minutes")
    print("• 📊 Odds are fetched at 6 different time windows (72h, 48h, 24h, 12h, 6h, 2h before race)")
    print("• 🤖 Predictions are generated 24 hours before the race")
    print("• 💰 Betting recommendations are updated when both odds and predictions are available")
    print("• 🏁 Race results are automatically processed 4 hours after the race")
    print("• 📱 Dashboard shows live countdown and best odds")
    print("• 📝 All data is logged and archived for analysis")
    
    print("\n🎯 CURRENT SYSTEM STATUS:")
    print("-" * 40)
    
    active_processes = []
    if any(w['is_active'] for w in timing_info['odds_fetch_windows']):
        active_processes.append("Fetching odds")
    if timing_info['prediction_window']['is_active']:
        active_processes.append("Generating predictions")
    if timing_info['result_processing_window']['is_active']:
        active_processes.append("Processing race results")
    
    if active_processes:
        print(f"🟢 Currently active: {', '.join(active_processes)}")
    else:
        print("⏸️  No active processes (waiting for next scheduled time)")
    
    # Show next action
    next_actions = []
    for window in timing_info['odds_fetch_windows']:
        if window['is_upcoming']:
            next_actions.append((window['target_time'], f"Fetch odds ({window['hours_before_race']}h before race)"))
    
    if timing_info['prediction_window']['is_upcoming']:
        next_actions.append((timing_info['prediction_window']['target_time'], "Generate predictions"))
    
    if timing_info['result_processing_window']['is_upcoming']:
        next_actions.append((timing_info['result_processing_window']['target_time'], "Process race results"))
    
    if next_actions:
        next_actions.sort(key=lambda x: x[0])
        next_time, next_action = next_actions[0]
        hours_until_next = (next_time - datetime.now()).total_seconds() / 3600
        print(f"⏭️  Next action: {next_action} in {hours_until_next:.1f} hours ({next_time.strftime('%m-%d %H:%M')})")

def check_current_files():
    """Check what files currently exist in the system"""
    print("\n📁 CURRENT SYSTEM FILES:")
    print("-" * 40)
    
    files_to_check = {
        'Live Odds': 'data/live/current_odds.csv',
        'Predictions': 'data/live/next_race_predictions.csv', 
        'Betting Recommendations': 'data/live/betting_recommendations.csv',
        'Race Schedule': 'data/live/race_schedule.json',
        'Monitor Config': 'config/race_monitor_config.json'
    }
    
    for name, path in files_to_check.items():
        if os.path.exists(path):
            stat = os.stat(path)
            age_hours = (datetime.now().timestamp() - stat.st_mtime) / 3600
            print(f"✅ {name}: {path} (updated {age_hours:.1f}h ago)")
        else:
            print(f"❌ {name}: {path} (not found)")

def main():
    """Main demonstration function"""
    print("🚀 F1 Automated Betting System - Race Timing Demo")
    print("\n📝 This demo shows how the automated system handles race timing and odds fetching")
    
    # Get example race (2025 Australian GP)
    race_info = get_example_next_race()
    
    # Calculate timing windows
    timing_info = calculate_timing_windows(race_info['date'])
    
    # Print detailed timing summary
    print_timing_summary(timing_info, race_info)
    
    # Check current files
    check_current_files()
    
    print("\n🔧 TO START AUTOMATED MONITORING:")
    print("-" * 40)
    print("1. Install missing dependencies: pip install schedule")
    print("2. Configure API keys in config/race_monitor_config.json")
    print("3. Run: python ml/run_betting_analysis.py monitor --action start")
    print("4. Or run: python ml/auto_race_monitor.py start")
    
    print("\n📊 DASHBOARD ACCESS:")
    print("-" * 40)
    print("• Live dashboard: http://localhost:8501")
    print("• Shows countdown to next race")
    print("• Displays current best odds")
    print("• Updates betting recommendations automatically")
    
    print("\n🎮 MANUAL TESTING:")
    print("-" * 40)
    print("• Run single check: python ml/auto_race_monitor.py check")
    print("• View status: python ml/auto_race_monitor.py status")
    print("• Test betting simulation: python ml/run_betting_analysis.py simulate")

if __name__ == "__main__":
    main()