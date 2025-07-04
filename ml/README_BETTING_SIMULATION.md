# F1 Betting Simulation & Automation System

A comprehensive Python-based system for simulating F1 betting strategies, tracking profit/loss over time, and automating post-race evaluations.

## 🚀 Quick Start

### 1. Run Your First Simulation

```bash
# Create sample data and run simulation
python run_betting_analysis.py simulate --create-sample

# Check system status
python run_betting_analysis.py status
```

### 2. Setup Automated Evaluation

```bash
# Setup directories and sample files
python run_betting_analysis.py setup

# Run single check for new race results
python run_betting_analysis.py auto --mode single

# Start continuous monitoring (checks every 5 minutes)
python run_betting_analysis.py auto --mode continuous
```

## 📁 System Components

### Core Scripts

1. **`bet_simulator.py`** - Main betting simulation engine
2. **`auto_race_evaluator.py`** - Automated post-race evaluation system
3. **`run_betting_analysis.py`** - CLI tool for easy access to all functionality

### Directory Structure

```
ml/
├── bet_simulator.py              # Betting simulation engine
├── auto_race_evaluator.py        # Automated evaluation system
├── run_betting_analysis.py       # CLI interface
└── README_BETTING_SIMULATION.md  # This file

data/
├── live/
│   └── betting_recommendations.csv    # Your betting recommendations
├── batch/
│   └── actual_results_2023.csv       # Historical race results
├── processed/
│   ├── bet_simulation_log.csv         # Detailed simulation log
│   ├── bet_simulation_log_summary.csv # Race-by-race summary
│   └── profit_over_time.png           # Profit graph
├── incoming_results/                  # Drop new race results here
├── archive/                           # Processed files archive
└── config/
    └── auto_evaluator_config.json     # Configuration file
```

## 🎯 Features

### Betting Simulation Engine

- **Fixed Bet Amount**: Simulates placing €10 bets on recommended drivers
- **Success Criteria**: Configurable (default: top 3 finish = win)
- **Profit Calculation**: 
  - Win: `(Quote × Bet Amount) - Bet Amount`
  - Loss: `-Bet Amount`
- **Tracking**: Cumulative profit over time across all races
- **Visualization**: Automatic profit graphs with capital tracking

### Automated Post-Race Evaluation

- **File Monitoring**: Automatically detects new race result files
- **Smart Processing**: Validates file format and extracts race information
- **Log Updates**: Appends new results to master simulation log
- **Graph Updates**: Regenerates profit graphs with latest data
- **Archiving**: Moves processed files to archive with timestamps
- **Notifications**: Console notifications for processed races

## 📊 Input File Formats

### Betting Recommendations CSV

```csv
Driver,Quote,Predicted_Probability,EV,Race_Name
Max Verstappen,1.8,0.55,3.2,Bahrain GP
Lewis Hamilton,4.2,0.24,2.1,Bahrain GP
Charles Leclerc,5.5,0.18,1.8,Bahrain GP
```

**Required Columns:**
- `Driver`: Driver name
- `Quote`: Betting odds (decimal format)
- `Predicted_Probability`: Your model's probability prediction
- `EV`: Expected Value
- `Race_Name`: Race identifier

### Race Results CSV

```csv
Driver,Actual_Position,Race_Name
Max Verstappen,1,Bahrain GP
Lewis Hamilton,2,Bahrain GP
Charles Leclerc,3,Bahrain GP
```

**Required Columns:**
- `Driver`: Driver name (must match betting recommendations)
- `Actual_Position`: Final race position (1-20)
- `Race_Name`: Race identifier (must match betting recommendations)

## 🛠️ Usage Examples

### Basic Simulation

```python
from bet_simulator import F1BetSimulator

# Initialize simulator
simulator = F1BetSimulator(starting_capital=1000, bet_amount=10)

# Load data
simulator.load_betting_recommendations('my_bets.csv')
simulator.load_race_results('my_results.csv')

# Run simulation
total_profit = simulator.simulate_bets(top_n_success=3)

# Save results
simulator.save_simulation_log('simulation_log.csv')
simulator.plot_profit_over_time('profit_graph.png')

# Generate report
performance = simulator.generate_performance_report()
```

### Automated Evaluation

```python
from auto_race_evaluator import AutoRaceEvaluator

# Initialize evaluator
evaluator = AutoRaceEvaluator('config/auto_evaluator_config.json')

# Single check
processed_count = evaluator.run_single_check()

# Continuous monitoring
evaluator.run_continuous_monitoring(check_interval_minutes=5)
```

### CLI Commands

```bash
# Simulation Commands
python run_betting_analysis.py simulate --help
python run_betting_analysis.py simulate --create-sample
python run_betting_analysis.py simulate --betting-file custom_bets.csv --results-file custom_results.csv

# Auto Evaluator Commands
python run_betting_analysis.py auto --mode single
python run_betting_analysis.py auto --mode continuous --interval 10
python run_betting_analysis.py auto --config custom_config.json

# Utility Commands
python run_betting_analysis.py setup
python run_betting_analysis.py status
```

## ⚙️ Configuration

### Auto Evaluator Configuration

The system uses a JSON configuration file (`config/auto_evaluator_config.json`):

```json
{
  "watch_directory": "data/incoming_results",
  "betting_recommendations_file": "data/live/betting_recommendations.csv",
  "master_log_file": "data/processed/bet_simulation_log.csv",
  "profit_graph_file": "data/processed/profit_over_time.png",
  "bet_amount": 10,
  "starting_capital": 1000,
  "success_threshold": 3,
  "file_patterns": ["*results*.csv", "*race_results*.csv", "*actual*.csv"],
  "min_file_age_seconds": 30,
  "enable_model_retraining": false,
  "notification_enabled": true
}
```

### Key Configuration Options

- **`success_threshold`**: Position threshold for successful bets (default: 3 = top 3)
- **`bet_amount`**: Fixed bet amount in euros (default: 10)
- **`starting_capital`**: Starting capital for profit tracking (default: 1000)
- **`file_patterns`**: Patterns to match incoming race result files
- **`min_file_age_seconds`**: Minimum file age before processing (prevents incomplete files)

## 📈 Output Files

### Simulation Log (`bet_simulation_log.csv`)

Detailed log of every bet placed:

```csv
Race_Name,Driver,Quote,Predicted_Probability,EV,Actual_Position,Bet_Amount,Outcome,Profit_Loss,Success_Threshold
Bahrain GP,Max Verstappen,1.8,0.55,3.2,1,10,WIN,8.0,3
Bahrain GP,Lewis Hamilton,4.2,0.24,2.1,2,10,WIN,32.0,3
```

### Race Summary (`bet_simulation_log_summary.csv`)

Race-by-race performance summary:

```csv
Race_Name,Race_Profit,Cumulative_Profit,Total_Capital,Bets_Placed,Bets_Won,Win_Rate
Bahrain GP,25.0,25.0,1025.0,5,3,0.6
Saudi Arabia GP,-15.0,10.0,1010.0,5,2,0.4
```

### Profit Graph (`profit_over_time.png`)

Visual representation showing:
- Total capital over time
- Cumulative profit/loss per race
- Starting capital reference line
- Automatic timestamps

## 🔄 Automated Workflow

### Post-Race Automation Steps

1. **File Detection**: Monitor `data/incoming_results/` for new CSV files
2. **Validation**: Check file format and required columns
3. **Race Matching**: Match results with existing betting recommendations
4. **Simulation**: Calculate profit/loss for the race
5. **Log Update**: Append results to master simulation log
6. **Graph Update**: Regenerate profit visualization
7. **Archiving**: Move processed file to archive with timestamp
8. **Notification**: Display processing summary

### Setting Up Automation

1. **Setup directories**:
   ```bash
   python run_betting_analysis.py setup
   ```

2. **Place race result files** in `data/incoming_results/`

3. **Run automated processing**:
   ```bash
   # Single check
   python run_betting_analysis.py auto --mode single
   
   # Continuous monitoring
   python run_betting_analysis.py auto --mode continuous
   ```

## 📊 Performance Metrics

The system tracks comprehensive performance metrics:

- **Total Bets Placed**: Count of all bets
- **Win Rate**: Percentage of successful bets
- **Total Profit/Loss**: Cumulative profit in euros
- **ROI**: Return on Investment percentage
- **Best/Worst Races**: Highest and lowest profit races
- **Driver Performance**: Profit by driver
- **Race-by-Race Tracking**: Detailed progression over time

## 🚨 Error Handling

The system includes robust error handling:

- **File Validation**: Checks for required columns and data types
- **Missing Data**: Handles missing race results gracefully
- **Duplicate Prevention**: Avoids reprocessing the same race
- **Logging**: Comprehensive logging to files and console
- **Recovery**: Continues processing even if individual races fail

## 🔧 Troubleshooting

### Common Issues

1. **"No betting recommendations found for race"**
   - Ensure race names match exactly between betting and results files
   - Check for typos in race names

2. **"Missing required columns"**
   - Verify CSV files have all required columns
   - Check column name spelling and capitalization

3. **"File not found"**
   - Use `python run_betting_analysis.py status` to check file locations
   - Use `--create-sample` flag to generate test data

4. **Graph not updating**
   - Check write permissions in output directory
   - Ensure matplotlib is installed: `pip install matplotlib`

### Debug Mode

For detailed debugging, check the log files in the `logs/` directory:

```bash
# View latest log
tail -f logs/auto_evaluator_*.log
```

## 🎯 Integration with F1 PredictPro

This betting simulation system integrates seamlessly with the main F1 PredictPro dashboard:

1. **Export betting recommendations** from the dashboard
2. **Place files** in the appropriate directories
3. **Run simulations** to track performance
4. **Use results** to refine your betting strategy

### Dashboard Integration Points

- Export betting recommendations from "Betting Recommendations" page
- Use simulation results to validate model performance
- Feed profit data back into strategy optimization

## 📝 License

This betting simulation system is part of the F1 PredictPro project and follows the same licensing terms.

## 🤝 Contributing

To extend the system:

1. **Add new metrics** in `bet_simulator.py`
2. **Enhance automation** in `auto_race_evaluator.py`
3. **Extend CLI** in `run_betting_analysis.py`
4. **Update documentation** in this README

---

**Happy Betting! 🏎️💰**