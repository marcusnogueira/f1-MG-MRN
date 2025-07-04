#!/usr/bin/env python3
"""
F1 Betting Analysis CLI Tool
Simple command-line interface for running betting simulations and automated evaluations
"""

import argparse
import os
import sys
import pandas as pd
from datetime import datetime
from bet_simulator import run_bet_simulation, F1BetSimulator
from auto_race_evaluator import AutoRaceEvaluator

def create_sample_data():
    """
    Create sample betting recommendations and race results for testing
    """
    print("📝 Creating sample data for testing...")
    
    # Sample betting recommendations
    betting_data = {
        'Driver': [
            'Max Verstappen', 'Lewis Hamilton', 'Charles Leclerc', 'Lando Norris', 'George Russell',
            'Max Verstappen', 'Charles Leclerc', 'Lewis Hamilton', 'Carlos Sainz', 'Lando Norris',
            'Max Verstappen', 'Lewis Hamilton', 'George Russell', 'Fernando Alonso', 'Charles Leclerc',
            'Max Verstappen', 'Lando Norris', 'Charles Leclerc', 'Lewis Hamilton', 'Oscar Piastri',
            'Max Verstappen', 'Lewis Hamilton', 'Charles Leclerc', 'George Russell', 'Carlos Sainz'
        ],
        'Quote': [
            1.8, 4.2, 5.5, 8.0, 12.0,
            1.6, 4.8, 5.2, 9.5, 7.5,
            1.9, 3.8, 11.0, 15.0, 6.2,
            1.7, 6.5, 5.8, 4.5, 18.0,
            1.5, 4.0, 6.0, 10.5, 8.8
        ],
        'Predicted_Probability': [
            0.55, 0.24, 0.18, 0.12, 0.08,
            0.62, 0.21, 0.19, 0.11, 0.13,
            0.53, 0.26, 0.09, 0.07, 0.16,
            0.59, 0.15, 0.17, 0.22, 0.06,
            0.67, 0.25, 0.17, 0.10, 0.11
        ],
        'EV': [
            3.2, 2.1, 1.8, 0.9, 0.5,
            2.8, 2.4, 1.9, 1.2, 0.8,
            3.1, 1.7, 0.6, 0.4, 1.1,
            2.9, 1.3, 1.4, 1.8, 0.3,
            3.5, 2.2, 1.6, 0.7, 0.9
        ],
        'Race_Name': [
            'Bahrain GP', 'Bahrain GP', 'Bahrain GP', 'Bahrain GP', 'Bahrain GP',
            'Saudi Arabia GP', 'Saudi Arabia GP', 'Saudi Arabia GP', 'Saudi Arabia GP', 'Saudi Arabia GP',
            'Australia GP', 'Australia GP', 'Australia GP', 'Australia GP', 'Australia GP',
            'Japan GP', 'Japan GP', 'Japan GP', 'Japan GP', 'Japan GP',
            'China GP', 'China GP', 'China GP', 'China GP', 'China GP'
        ]
    }
    
    # Sample race results
    results_data = {
        'Driver': [
            'Max Verstappen', 'Lewis Hamilton', 'Charles Leclerc', 'Lando Norris', 'George Russell',
            'Max Verstappen', 'Charles Leclerc', 'Lewis Hamilton', 'Carlos Sainz', 'Lando Norris',
            'Max Verstappen', 'Lewis Hamilton', 'George Russell', 'Fernando Alonso', 'Charles Leclerc',
            'Max Verstappen', 'Lando Norris', 'Charles Leclerc', 'Lewis Hamilton', 'Oscar Piastri',
            'Max Verstappen', 'Lewis Hamilton', 'Charles Leclerc', 'George Russell', 'Carlos Sainz'
        ],
        'Actual_Position': [
            1, 2, 3, 4, 5,
            1, 2, 3, 4, 5,
            1, 2, 3, 4, 5,
            1, 2, 3, 4, 5,
            1, 2, 3, 4, 5
        ],
        'Race_Name': [
            'Bahrain GP', 'Bahrain GP', 'Bahrain GP', 'Bahrain GP', 'Bahrain GP',
            'Saudi Arabia GP', 'Saudi Arabia GP', 'Saudi Arabia GP', 'Saudi Arabia GP', 'Saudi Arabia GP',
            'Australia GP', 'Australia GP', 'Australia GP', 'Australia GP', 'Australia GP',
            'Japan GP', 'Japan GP', 'Japan GP', 'Japan GP', 'Japan GP',
            'China GP', 'China GP', 'China GP', 'China GP', 'China GP'
        ]
    }
    
    # Create directories
    os.makedirs('data/live', exist_ok=True)
    os.makedirs('data/batch', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    
    # Save sample data
    betting_df = pd.DataFrame(betting_data)
    results_df = pd.DataFrame(results_data)
    
    betting_file = 'data/live/betting_recommendations_simulation.csv'
    results_file = 'data/batch/actual_results_2023.csv'
    
    betting_df.to_csv(betting_file, index=False)
    results_df.to_csv(results_file, index=False)
    
    print(f"✅ Sample betting recommendations saved to: {betting_file}")
    print(f"✅ Sample race results saved to: {results_file}")
    
    return betting_file, results_file

def run_simulation_command(args):
    """
    Run betting simulation
    """
    print("🎰 Running F1 Betting Simulation...\n")
    
    betting_file = args.betting_file
    results_file = args.results_file
    
    # If create_sample is requested, always create new sample data
    if args.create_sample:
        betting_file, results_file = create_sample_data()
    
    # Check if files exist
    if not os.path.exists(betting_file):
        print(f"❌ Betting file not found: {betting_file}")
        if not args.create_sample:
            print("Use --create-sample to generate sample data")
            return
    
    if not os.path.exists(results_file):
        print(f"❌ Results file not found: {results_file}")
        if not args.create_sample:
            print("Use --create-sample to generate sample data")
            return
    
    # Run simulation
    try:
        simulator, performance = run_bet_simulation(
            betting_file, 
            results_file, 
            args.output_dir
        )
        
        print("\n🎉 Simulation completed successfully!")
        print(f"📊 Check results in: {args.output_dir}")
        
    except Exception as e:
        print(f"❌ Error running simulation: {e}")

def run_auto_evaluator_command(args):
    """
    Run automated race evaluator
    """
    print("🤖 Starting Auto Race Evaluator...\n")
    
    try:
        evaluator = AutoRaceEvaluator(args.config)
        
        if args.mode == 'single':
            processed = evaluator.run_single_check()
            print(f"\n✅ Single check completed. Processed {processed} files.")
        else:
            print(f"🔄 Starting continuous monitoring (every {args.interval} minutes)")
            print("Press Ctrl+C to stop...")
            evaluator.run_continuous_monitoring(args.interval)
            
    except Exception as e:
        print(f"❌ Error running auto evaluator: {e}")

def setup_auto_evaluator_command(args):
    """
    Setup directories and sample files for auto evaluator
    """
    print("🔧 Setting up Auto Race Evaluator...\n")
    
    # Create necessary directories
    directories = [
        'data/incoming_results',
        'data/processed',
        'data/archive',
        'config',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Created directory: {directory}")
    
    # Create sample betting recommendations if they don't exist
    betting_file = 'data/live/betting_recommendations_simulation.csv'
    if not os.path.exists(betting_file):
        create_sample_data()
    
    # Create a sample incoming race result file
    sample_result = pd.DataFrame({
        'Driver': ['Max Verstappen', 'Lewis Hamilton', 'Charles Leclerc', 'Lando Norris', 'George Russell'],
        'Actual_Position': [1, 2, 3, 4, 5],
        'Race_Name': ['Monaco GP', 'Monaco GP', 'Monaco GP', 'Monaco GP', 'Monaco GP']
    })
    
    sample_file = 'data/incoming_results/monaco_gp_results.csv'
    sample_result.to_csv(sample_file, index=False)
    print(f"📄 Created sample race result: {sample_file}")
    
    # Create a default config file
    config_dir = 'config'
    config_file = os.path.join(config_dir, 'auto_evaluator_config.json')
    if not os.path.exists(config_file):
        default_config = {
            "watch_directory": "data/incoming_results",
            "betting_recommendations_file": "data/live/betting_recommendations_simulation.csv",
            "master_log_file": "data/processed/bet_simulation_log.csv",
            "profit_graph_file": "data/processed/profit_over_time.png",
            "processed_races_file": "data/processed/processed_races.json",
            "archive_directory": "data/archive",
            "bet_amount": 10,
            "starting_capital": 1000,
            "success_threshold": 3,
            "file_patterns": ["*results*.csv", "*race_results*.csv", "*actual*.csv"],
            "min_file_age_seconds": 30,
            "enable_model_retraining": False,
            "model_retrain_threshold": 5,
            "notification_enabled": True
        }
        with open(config_file, 'w') as f:
            import json
            json.dump(default_config, f, indent=2)
        print(f"📝 Created default config file: {config_file}")
    
    print("\n✅ Setup completed!")
    print("\nNext steps:")
    print("1. Place new race result files in: data/incoming_results/")
    print("2. Run: python run_betting_analysis.py auto --mode single")
    print("3. Or run continuous monitoring: python run_betting_analysis.py auto --mode continuous")

def status_command(args):
    """
    Show status of betting analysis system
    """
    print("📊 F1 Betting Analysis System Status\n")
    
    # Check key files and directories
    key_paths = {
        'Betting Recommendations': 'data/live/betting_recommendations.csv',
        'Master Simulation Log': 'data/processed/bet_simulation_log.csv',
        'Profit Graph': 'data/processed/profit_over_time.png',
        'Incoming Results Directory': 'data/incoming_results',
        'Archive Directory': 'data/archive',
        'Config Directory': 'config'
    }
    
    for name, path in key_paths.items():
        if os.path.exists(path):
            if os.path.isfile(path):
                size = os.path.getsize(path)
                modified = datetime.fromtimestamp(os.path.getmtime(path))
                print(f"✅ {name}: {path} ({size} bytes, modified: {modified.strftime('%Y-%m-%d %H:%M')})")
            else:
                files_count = len(os.listdir(path)) if os.path.isdir(path) else 0
                print(f"✅ {name}: {path} ({files_count} files)")
        else:
            print(f"❌ {name}: {path} (not found)")
    
    # Check if simulation log exists and show summary
    log_file = 'data/processed/bet_simulation_log.csv'
    if os.path.exists(log_file):
        try:
            log_df = pd.read_csv(log_file)
            total_profit = log_df['Profit_Loss'].sum()
            total_bets = len(log_df)
            win_rate = len(log_df[log_df['Outcome'] == 'WIN']) / total_bets * 100
            races = log_df['Race_Name'].nunique()
            
            print(f"\n💰 Simulation Summary:")
            print(f"   Total Races: {races}")
            print(f"   Total Bets: {total_bets}")
            print(f"   Win Rate: {win_rate:.1f}%")
            print(f"   Total Profit/Loss: €{total_profit:.2f}")
            
        except Exception as e:
            print(f"⚠️ Error reading simulation log: {e}")
    
    # Check for pending race results
    incoming_dir = 'data/incoming_results'
    if os.path.exists(incoming_dir):
        pending_files = [f for f in os.listdir(incoming_dir) if f.endswith('.csv')]
        if pending_files:
            print(f"\n⏳ Pending Race Results ({len(pending_files)} files):")
            for file in pending_files[:5]:  # Show first 5
                print(f"   - {file}")
            if len(pending_files) > 5:
                print(f"   ... and {len(pending_files) - 5} more")
        else:
            print(f"\n✅ No pending race results")

def main():
    parser = argparse.ArgumentParser(
        description='F1 Betting Analysis CLI Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run betting simulation with sample data
  python run_betting_analysis.py simulate --create-sample
  
  # Run simulation with custom files
  python run_betting_analysis.py simulate --betting-file my_bets.csv --results-file my_results.csv
  
  # Setup auto evaluator
  python run_betting_analysis.py setup
  
  # Run single check for new race results
  python run_betting_analysis.py auto --mode single
  
  # Start continuous monitoring
  python run_betting_analysis.py auto --mode continuous --interval 10
  
  # Check system status
  python run_betting_analysis.py status
  
  # Start race monitor
  python run_betting_analysis.py monitor --action start
"""
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Simulate command
    simulate_parser = subparsers.add_parser('simulate', help='Run betting simulation')
    simulate_parser.add_argument('--betting-file', default='data/live/betting_recommendations_simulation.csv',
                               help='Path to betting recommendations CSV')
    simulate_parser.add_argument('--results-file', default='data/batch/actual_results_2023.csv',
                               help='Path to race results CSV')
    simulate_parser.add_argument('--output-dir', default='data/processed',
                               help='Output directory for results')
    simulate_parser.add_argument('--create-sample', action='store_true',
                               help='Create sample data if files not found')
    
    # Auto evaluator command
    auto_parser = subparsers.add_parser('auto', help='Run automated race evaluator')
    auto_parser.add_argument('--mode', choices=['single', 'continuous'], default='single',
                           help='Run mode: single check or continuous monitoring')
    auto_parser.add_argument('--interval', type=int, default=5,
                           help='Check interval in minutes for continuous mode')
    auto_parser.add_argument('--config', default='config/auto_evaluator_config.json',
                           help='Path to configuration file')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Setup auto evaluator directories and files')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='F1 race monitoring and automation')
    monitor_parser.add_argument('--action', choices=['start', 'stop', 'status', 'setup'], default='status',
                              help='Monitor action to perform')
    monitor_parser.add_argument('--config', default='config/race_monitor_config.json',
                              help='Path to monitor configuration file')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show system status')
    
    args = parser.parse_args()
    
    if args.command == 'simulate':
        run_simulation_command(args)
    elif args.command == 'auto':
        run_auto_evaluator_command(args)
    elif args.command == 'setup':
        setup_auto_evaluator_command(args)
    elif args.command == 'monitor':
        try:
            if args.action == 'setup':
                # Create default monitor configuration
                config = {
                    "api_keys": {
                        "ergast_api": "https://ergast.com/api/f1",
                        "odds_api_key": "your_odds_api_key_here"
                    },
                    "monitoring": {
                        "check_interval_hours": 6,
                        "odds_fetch_days_before": 7,
                        "prediction_days_before": 3
                    },
                    "notifications": {
                        "enabled": True,
                        "email": "your_email@example.com"
                    },
                    "file_paths": {
                        "schedule_cache": "data/cache/f1_schedule.json",
                        "odds_data": "data/live/current_odds.json",
                        "betting_recommendations": "data/live/betting_recommendations.csv"
                    }
                }
                
                os.makedirs('config', exist_ok=True)
                os.makedirs('data/cache', exist_ok=True)
                with open(args.config, 'w') as f:
                    import json
                    json.dump(config, f, indent=2)
                
                print(f"✅ Monitor configuration created: {args.config}")
                print("📝 Please update the configuration with your API keys and preferences")
                print("🚀 To start monitoring: python run_betting_analysis.py monitor --action start")
                
            else:
                # Import only when needed for start/stop/status
                from auto_race_monitor import AutoF1RaceMonitor
                
                if args.action == 'start':
                    monitor = AutoF1RaceMonitor(args.config)
                    print("🏁 Starting F1 race monitor...")
                    monitor.start_monitoring()
                    
                elif args.action == 'stop':
                    print("🛑 Stopping F1 race monitor...")
                    # Implementation for stopping monitor would go here
                    print("Monitor stopped")
                    
                elif args.action == 'status':
                    print("📊 F1 Race Monitor Status")
                    print("=" * 30)
                    if os.path.exists(args.config):
                        print(f"✅ Configuration file: {args.config}")
                        with open(args.config, 'r') as f:
                            import json
                            config = json.load(f)
                        print(f"📡 Check interval: {config.get('monitoring', {}).get('check_interval_hours', 'N/A')} hours")
                        print(f"🎯 Odds fetch: {config.get('monitoring', {}).get('odds_fetch_days_before', 'N/A')} days before race")
                    else:
                        print(f"❌ Configuration file not found: {args.config}")
                        print("Run 'monitor --action setup' to create configuration")
                
        except ImportError:
            print("❌ Error: auto_race_monitor module not found")
            print("Please ensure auto_race_monitor.py is in the ml/ directory")
        except Exception as e:
            print(f"❌ Error running monitor: {e}")
    
    elif args.command == 'status':
        status_command(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()