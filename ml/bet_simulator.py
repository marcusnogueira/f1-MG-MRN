import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime
import seaborn as sns

class F1BetSimulator:
    """
    F1 Betting Simulator that tracks profit/loss over time
    """
    
    def __init__(self, starting_capital=1000, bet_amount=10):
        self.starting_capital = starting_capital
        self.bet_amount = bet_amount
        self.simulation_log = []
        
    def load_betting_recommendations(self, csv_path):
        """
        Load betting recommendations from CSV
        Expected columns: Driver, Quote, Predicted_Probability, EV, Race_Name
        """
        try:
            self.betting_df = pd.read_csv(csv_path)
            print(f"✅ Loaded {len(self.betting_df)} betting recommendations")
            return True
        except Exception as e:
            print(f"❌ Error loading betting recommendations: {e}")
            return False
    
    def load_race_results(self, csv_path):
        """
        Load actual race results from CSV
        Expected columns: Driver, Actual_Position, Race_Name
        """
        try:
            self.results_df = pd.read_csv(csv_path)
            print(f"✅ Loaded results for {len(self.results_df)} drivers")
            return True
        except Exception as e:
            print(f"❌ Error loading race results: {e}")
            return False
    
    def simulate_bets(self, top_n_success=3):
        """
        Simulate betting outcomes
        
        Args:
            top_n_success (int): Consider bet successful if driver finishes in top N positions
        """
        if not hasattr(self, 'betting_df') or not hasattr(self, 'results_df'):
            print("❌ Please load both betting recommendations and race results first")
            return
        
        # Merge betting recommendations with actual results
        merged_df = pd.merge(
            self.betting_df, 
            self.results_df, 
            on=['Driver', 'Race_Name'], 
            how='inner'
        )
        
        print(f"📊 Simulating bets for {len(merged_df)} matched entries")
        
        cumulative_profit = 0
        race_profits = {}
        
        # Group by race to track progress over time
        for race_name in merged_df['Race_Name'].unique():
            race_data = merged_df[merged_df['Race_Name'] == race_name]
            race_profit = 0
            race_bets = 0
            race_wins = 0
            
            for _, row in race_data.iterrows():
                # Place bet
                bet_cost = self.bet_amount
                race_bets += 1
                
                # Check if bet was successful (top N finish)
                if row['Actual_Position'] <= top_n_success:
                    # Win: (Quote * bet_amount) - bet_amount
                    profit = (row['Quote'] * self.bet_amount) - self.bet_amount
                    race_wins += 1
                    outcome = 'WIN'
                else:
                    # Loss: -bet_amount
                    profit = -self.bet_amount
                    outcome = 'LOSS'
                
                race_profit += profit
                
                # Log individual bet
                self.simulation_log.append({
                    'Race_Name': race_name,
                    'Driver': row['Driver'],
                    'Quote': row['Quote'],
                    'Predicted_Probability': row['Predicted_Probability'],
                    'EV': row['EV'],
                    'Actual_Position': row['Actual_Position'],
                    'Bet_Amount': self.bet_amount,
                    'Outcome': outcome,
                    'Profit_Loss': profit,
                    'Success_Threshold': top_n_success
                })
            
            cumulative_profit += race_profit
            race_profits[race_name] = {
                'race_profit': race_profit,
                'cumulative_profit': cumulative_profit,
                'total_capital': self.starting_capital + cumulative_profit,
                'bets_placed': race_bets,
                'bets_won': race_wins,
                'win_rate': race_wins / race_bets if race_bets > 0 else 0
            }
            
            print(f"🏁 {race_name}: {race_bets} bets, {race_wins} wins, €{race_profit:.2f} profit")
        
        self.race_profits = race_profits
        print(f"\n💰 Total Profit/Loss: €{cumulative_profit:.2f}")
        print(f"💼 Final Capital: €{self.starting_capital + cumulative_profit:.2f}")
        
        return cumulative_profit
    
    def save_simulation_log(self, output_path="data/processed/bet_simulation_log.csv"):
        """
        Save detailed simulation log to CSV
        """
        if not self.simulation_log:
            print("❌ No simulation data to save")
            return
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        log_df = pd.DataFrame(self.simulation_log)
        log_df.to_csv(output_path, index=False)
        print(f"💾 Simulation log saved to {output_path}")
        
        # Also save race summary
        if hasattr(self, 'race_profits'):
            summary_data = []
            for race_name, data in self.race_profits.items():
                summary_data.append({
                    'Race_Name': race_name,
                    'Race_Profit': data['race_profit'],
                    'Cumulative_Profit': data['cumulative_profit'],
                    'Total_Capital': data['total_capital'],
                    'Bets_Placed': data['bets_placed'],
                    'Bets_Won': data['bets_won'],
                    'Win_Rate': data['win_rate']
                })
            
            summary_df = pd.DataFrame(summary_data)
            summary_path = output_path.replace('.csv', '_summary.csv')
            summary_df.to_csv(summary_path, index=False)
            print(f"📊 Race summary saved to {summary_path}")
    
    def plot_profit_over_time(self, output_path="data/processed/profit_over_time.png"):
        """
        Create and save profit graph over time
        """
        if not hasattr(self, 'race_profits'):
            print("❌ No simulation data to plot")
            return
        
        # Prepare data for plotting
        races = list(self.race_profits.keys())
        total_capitals = [self.race_profits[race]['total_capital'] for race in races]
        cumulative_profits = [self.race_profits[race]['cumulative_profit'] for race in races]
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # Plot 1: Total Capital over time
        ax1.plot(races, total_capitals, marker='o', linewidth=2, markersize=6, color='#2E86AB')
        ax1.axhline(y=self.starting_capital, color='red', linestyle='--', alpha=0.7, label=f'Starting Capital (€{self.starting_capital})')
        ax1.set_title('F1 Betting Simulation - Total Capital Over Time', fontsize=16, fontweight='bold')
        ax1.set_ylabel('Total Capital (€)', fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Rotate x-axis labels for better readability
        ax1.tick_params(axis='x', rotation=45)
        
        # Add value annotations
        for i, (race, capital) in enumerate(zip(races, total_capitals)):
            if i % 2 == 0:  # Show every other value to avoid crowding
                ax1.annotate(f'€{capital:.0f}', (i, capital), textcoords="offset points", 
                           xytext=(0,10), ha='center', fontsize=9)
        
        # Plot 2: Cumulative Profit/Loss
        colors = ['green' if profit >= 0 else 'red' for profit in cumulative_profits]
        bars = ax2.bar(races, cumulative_profits, color=colors, alpha=0.7)
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.8)
        ax2.set_title('Cumulative Profit/Loss per Race', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Cumulative Profit/Loss (€)', fontsize=12)
        ax2.set_xlabel('Race', fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, profit in zip(bars, cumulative_profits):
            height = bar.get_height()
            ax2.annotate(f'€{profit:.0f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3 if height >= 0 else -15),
                        textcoords="offset points", ha='center', va='bottom' if height >= 0 else 'top',
                        fontsize=9)
        
        plt.tight_layout()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"📈 Profit graph saved to {output_path}")
        plt.show()
    
    def generate_performance_report(self):
        """
        Generate a comprehensive performance report
        """
        if not self.simulation_log:
            print("❌ No simulation data available")
            return
        
        log_df = pd.DataFrame(self.simulation_log)
        
        print("\n" + "="*60)
        print("📊 F1 BETTING SIMULATION PERFORMANCE REPORT")
        print("="*60)
        
        # Overall Statistics
        total_bets = len(log_df)
        total_wins = len(log_df[log_df['Outcome'] == 'WIN'])
        win_rate = total_wins / total_bets * 100
        total_profit = log_df['Profit_Loss'].sum()
        
        print(f"\n🎯 OVERALL PERFORMANCE:")
        print(f"   Total Bets Placed: {total_bets}")
        print(f"   Winning Bets: {total_wins}")
        print(f"   Win Rate: {win_rate:.1f}%")
        print(f"   Total Profit/Loss: €{total_profit:.2f}")
        print(f"   ROI: {(total_profit / (total_bets * self.bet_amount)) * 100:.1f}%")
        
        # Best and Worst Races
        race_summary = log_df.groupby('Race_Name')['Profit_Loss'].sum().sort_values(ascending=False)
        print(f"\n🏆 BEST RACE: {race_summary.index[0]} (+€{race_summary.iloc[0]:.2f})")
        print(f"💸 WORST RACE: {race_summary.index[-1]} (€{race_summary.iloc[-1]:.2f})")
        
        # Driver Performance
        driver_stats = log_df.groupby('Driver').agg({
            'Profit_Loss': 'sum',
            'Outcome': lambda x: (x == 'WIN').sum(),
            'Driver': 'count'
        }).rename(columns={'Driver': 'Total_Bets'})
        driver_stats['Win_Rate'] = driver_stats['Outcome'] / driver_stats['Total_Bets'] * 100
        driver_stats = driver_stats.sort_values('Profit_Loss', ascending=False)
        
        print(f"\n🏎️ TOP 5 MOST PROFITABLE DRIVERS:")
        for i, (driver, stats) in enumerate(driver_stats.head().iterrows()):
            print(f"   {i+1}. {driver}: €{stats['Profit_Loss']:.2f} ({stats['Win_Rate']:.1f}% win rate)")
        
        return {
            'total_bets': total_bets,
            'win_rate': win_rate,
            'total_profit': total_profit,
            'roi': (total_profit / (total_bets * self.bet_amount)) * 100,
            'best_race': race_summary.index[0],
            'worst_race': race_summary.index[-1]
        }

def run_bet_simulation(betting_csv, results_csv, output_dir="data/processed"):
    """
    Main function to run the complete betting simulation
    """
    print("🎰 Starting F1 Betting Simulation...\n")
    
    # Initialize simulator
    simulator = F1BetSimulator(starting_capital=1000, bet_amount=10)
    
    # Load data
    if not simulator.load_betting_recommendations(betting_csv):
        return
    
    if not simulator.load_race_results(results_csv):
        return
    
    # Run simulation
    total_profit = simulator.simulate_bets(top_n_success=3)
    
    # Save results
    log_path = os.path.join(output_dir, "bet_simulation_log.csv")
    simulator.save_simulation_log(log_path)
    
    # Create profit graph
    graph_path = os.path.join(output_dir, "profit_over_time.png")
    simulator.plot_profit_over_time(graph_path)
    
    # Generate report
    performance = simulator.generate_performance_report()
    
    return simulator, performance

if __name__ == "__main__":
    # Example usage
    betting_recommendations_file = "data/live/betting_recommendations.csv"
    race_results_file = "data/batch/actual_results_2023.csv"
    
    # Check if files exist
    if not os.path.exists(betting_recommendations_file):
        print(f"❌ Betting recommendations file not found: {betting_recommendations_file}")
        print("Creating sample betting recommendations...")
        
        # Create sample data
        sample_betting = pd.DataFrame({
            'Driver': ['Max Verstappen', 'Lewis Hamilton', 'Charles Leclerc', 'Lando Norris'] * 5,
            'Quote': [1.5, 3.2, 4.1, 6.5] * 5,
            'Predicted_Probability': [0.65, 0.28, 0.22, 0.15] * 5,
            'EV': [2.5, 1.8, 0.9, 0.3] * 5,
            'Race_Name': ['Bahrain GP', 'Saudi Arabia GP', 'Australia GP', 'Japan GP', 'China GP'] * 4
        })
        
        os.makedirs(os.path.dirname(betting_recommendations_file), exist_ok=True)
        sample_betting.to_csv(betting_recommendations_file, index=False)
        print(f"✅ Sample betting recommendations created at {betting_recommendations_file}")
    
    if not os.path.exists(race_results_file):
        print(f"❌ Race results file not found: {race_results_file}")
        print("Creating sample race results...")
        
        # Create sample results
        sample_results = pd.DataFrame({
            'Driver': ['Max Verstappen', 'Lewis Hamilton', 'Charles Leclerc', 'Lando Norris'] * 5,
            'Actual_Position': [1, 2, 3, 4] * 5,
            'Race_Name': ['Bahrain GP', 'Saudi Arabia GP', 'Australia GP', 'Japan GP', 'China GP'] * 4
        })
        
        os.makedirs(os.path.dirname(race_results_file), exist_ok=True)
        sample_results.to_csv(race_results_file, index=False)
        print(f"✅ Sample race results created at {race_results_file}")
    
    # Run simulation
    simulator, performance = run_bet_simulation(betting_recommendations_file, race_results_file)
    
    print("\n🏁 Simulation completed successfully!")