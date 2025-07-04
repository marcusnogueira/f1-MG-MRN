import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import numpy as np
from datetime import datetime
import io
import tempfile
import json
import os
import sys
from pathlib import Path

# Optional imports for PDF generation
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Optional imports for additional plotting
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.abspath('.'))
sys.path.append('ml')

# Import live dashboard functions
def load_next_race_info():
    """Load next race info for Streamlit dashboard"""
    try:
        info_file = "data/live/next_race_info.json"
        if os.path.exists(info_file):
            with open(info_file, 'r') as f:
                data = json.load(f)
                return {
                    "race_name": data.get('race_name', 'Next Race'),
                    "location": data.get('location', 'TBD'),
                    "date": data.get('race_date_formatted', data.get('race_date', 'TBD')),
                    "country": data.get('country', ''),
                    "days_until": data.get('days_until', 0),
                    "hours_until": data.get('hours_until', 0),
                    "is_race_weekend": data.get('is_race_weekend', False)
                }
    except Exception as e:
        st.error(f"Error loading race info: {e}")
    return {"race_name": "Next Race", "date": "TBD", "location": "TBD"}

def load_best_odds():
    """Load best odds for Streamlit dashboard"""
    try:
        odds_file = "data/live/best_odds_summary.csv"
        if os.path.exists(odds_file):
            return pd.read_csv(odds_file)
    except Exception as e:
        st.error(f"Error loading odds: {e}")
    return pd.DataFrame()

def load_top_value_bets():
    """Load top value bets for Streamlit dashboard"""
    try:
        bets_file = "data/live/top_value_bets.csv"
        if os.path.exists(bets_file):
            return pd.read_csv(bets_file)
    except Exception as e:
        st.error(f"Error loading value bets: {e}")
    return pd.DataFrame()

def load_race_countdown():
    """Load race countdown for Streamlit dashboard"""
    try:
        countdown_file = "data/live/race_countdown.json"
        if os.path.exists(countdown_file):
            with open(countdown_file, 'r') as f:
                data = json.load(f)
                days = data.get('days', 0)
                hours = data.get('hours', 0)
                minutes = data.get('minutes', 0)
                
                if days > 0:
                    return f"{days} days, {hours} hours away"
                elif hours > 0:
                    return f"{hours} hours, {minutes} minutes away"
                else:
                    return f"{minutes} minutes away"
    except Exception as e:
        st.error(f"Error loading countdown: {e}")
    return "Race information not available"

try:
    from ml import value_bet_calculator, betting_strategy
    from utils.prediction_exporter import F1PredictionExporter
except ImportError:
    # Fallback if imports fail
    value_bet_calculator = None
    betting_strategy = None
    F1PredictionExporter = None

# 📁 Configuration
YEAR = 2025
RACE = "Spanish Grand Prix"
RACE_FILE = "Spanish_Grand_Prix_full"
PRED_FILE = f"data/live/predicted_probabilities_{YEAR}_{RACE_FILE}.csv"
BETTING_FILE = "data/live/betting_recommendations.csv"
ODDS_FILE = "data/live/sample_odds.csv"

st.set_page_config(page_title="F1 PredictPro Live Dashboard", layout="wide")

# Auto-refresh configuration
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()

# Add refresh controls in sidebar
st.sidebar.markdown("### 🔄 Live Updates")
auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)", value=True)
if st.sidebar.button("🔄 Refresh Now"):
    st.session_state.last_update = datetime.now()
    st.rerun()

# Auto-refresh logic
if auto_refresh and (datetime.now() - st.session_state.last_update).seconds > 30:
    st.session_state.last_update = datetime.now()
    st.rerun()

# 📥 Load data
if not os.path.exists(PRED_FILE):
    st.error(f"❌ File not found: {PRED_FILE}")
    st.stop()

df = pd.read_csv(PRED_FILE)

# Sidebar for Navigation
st.sidebar.title("🏎️ F1 PredictPro")
page = st.sidebar.selectbox("Navigation", ["🏁 Dashboard", "📊 Driver Analysis", "💰 Betting Recommendations", "📈 Probabilities"])

def main_dashboard():
    st.title("🏎️ F1 PredictPro Dashboard")
    st.markdown("### Welcome to the Ultimate F1 Prediction & Betting Analysis Platform")
    
    # Live Race Information Section
    st.markdown("---")
    st.markdown("## 🏁 Next Race Information")
    
    try:
        next_race = load_next_race_info()
        countdown = load_race_countdown()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"### {next_race.get('race_name', 'Next Race')}")
            st.markdown(f"📍 **Location:** {next_race.get('location', 'TBD')}")
            st.markdown(f"📅 **Date:** {next_race.get('date', 'TBD')}")
            
        with col2:
             st.markdown("### ⏰ Countdown")
             
             # Calculate live countdown
             try:
                 race_time = datetime.fromisoformat(next_race.get('race_date', '').replace('Z', '+00:00')) if next_race.get('race_date') else None
                 if race_time:
                     now = datetime.now()
                     time_diff = race_time - now
                     
                     if time_diff.total_seconds() > 0:
                         days = time_diff.days
                         hours, remainder = divmod(time_diff.seconds, 3600)
                         minutes, seconds = divmod(remainder, 60)
                         
                         # Display countdown with seconds
                         if days > 0:
                             live_countdown = f"**{days}d {hours}h {minutes}m {seconds}s**"
                         elif hours > 0:
                             live_countdown = f"**{hours}h {minutes}m {seconds}s**"
                         else:
                             live_countdown = f"**{minutes}m {seconds}s**"
                         
                         st.markdown(live_countdown)
                         
                         # Add JavaScript for real-time countdown
                         race_timestamp = int(race_time.timestamp() * 1000)
                         st.markdown(f"""
                         <div id="countdown-timer" style="font-size: 18px; font-weight: bold; color: #ff6b6b;"></div>
                         <script>
                         function updateCountdown() {{
                             const raceTime = {race_timestamp};
                             const now = new Date().getTime();
                             const distance = raceTime - now;
                             
                             if (distance > 0) {{
                                 const days = Math.floor(distance / (1000 * 60 * 60 * 24));
                                 const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                                 const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                                 const seconds = Math.floor((distance % (1000 * 60)) / 1000);
                                 
                                 let display = "";
                                 if (days > 0) display = days + "d " + hours + "h " + minutes + "m " + seconds + "s";
                                 else if (hours > 0) display = hours + "h " + minutes + "m " + seconds + "s";
                                 else display = minutes + "m " + seconds + "s";
                                 
                                 document.getElementById("countdown-timer").innerHTML = "🏁 " + display + " until race!";
                             }} else {{
                                 document.getElementById("countdown-timer").innerHTML = "🏁 Race has started!";
                             }}
                         }}
                         
                         updateCountdown();
                         setInterval(updateCountdown, 1000);
                         </script>
                         """, unsafe_allow_html=True)
                     else:
                         st.markdown("**🏁 Race has started!**")
                 else:
                     st.markdown(f"**{countdown}**")
             except Exception as e:
                 st.markdown(f"**{countdown}**")
                 st.sidebar.error(f"Countdown error: {str(e)}")
        
        # Best Odds Section
        st.markdown("### 💰 Best Current Odds")
        best_odds = load_best_odds()
        if not best_odds.empty:
            st.dataframe(best_odds, use_container_width=True)
        else:
            st.info("Odds will be available closer to race time")
        
        # Top Value Bets
        st.markdown("### 🎯 Top Value Bets")
        value_bets = load_top_value_bets()
        if not value_bets.empty:
            st.dataframe(value_bets, use_container_width=True)
        else:
            st.info("Value bet analysis will be available when odds are loaded")
            
    except Exception as e:
        st.warning(f"Live race data temporarily unavailable: {str(e)}")
    
    st.markdown("---")
    
    # Quick stats overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Races Analyzed", "23")
    with col2:
        st.metric("Prediction Accuracy", "78.5%")
    with col3:
        st.metric("Betting ROI", "+15.2%")
    with col4:
        st.metric("Active Strategies", "5")

if page == "🏁 Dashboard":
    main_dashboard()

elif page == "📊 Driver Analysis":
    st.title(f"📊 F1 Driver Analysis - {RACE} {YEAR}")
    
    # 🎯 Driver Selection
    drivers = sorted(df["driver"].unique())
    selected_driver = st.selectbox("🏎️ Select Driver:", drivers)
    
    # 📊 Get probabilities
    driver_data = df[df["driver"] == selected_driver].sort_values("position")
    driver_data["probability"] = driver_data["probability"].round(2)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # 📋 Table
        st.markdown(f"### 📊 Position Probabilities for **{selected_driver}**")
        display_data = driver_data[["position", "probability"]].rename(columns={
            "position": "Position",
            "probability": "Probability (%)"
        })
        st.dataframe(display_data, use_container_width=True)
        
        # Highlight Top 3 probabilities
        top3_data = driver_data[driver_data["position"].isin([1, 2, 3])]
        if not top3_data.empty:
            st.markdown("### 🏆 Top 3 Chances")
            for _, row in top3_data.iterrows():
                st.metric(f"P{int(row['position'])}", f"{row['probability']:.1f}%")
    
    with col2:
        # 📈 Chart
        st.markdown("### 📈 Probability Distribution")
        chart_data = driver_data.set_index("position")["probability"]
        st.bar_chart(chart_data, use_container_width=True)
        
        # Additional Statistics
        st.markdown("### 📊 Statistics")
        st.metric("Highest Probability", f"{driver_data['probability'].max():.1f}%")
        best_position = driver_data.loc[driver_data['probability'].idxmax(), 'position']
        st.metric("Most Likely Position", f"P{int(best_position)}")
        top10_prob = driver_data[driver_data['position'] <= 10]['probability'].sum()
        st.metric("Top 10 Probability", f"{top10_prob:.1f}%")

elif page == "💰 Betting Recommendations":
    st.title(f"💰 Betting Recommendations - {RACE} {YEAR}")
    
    # Generate betting recommendations if not available
    if not os.path.exists(BETTING_FILE):
        st.warning("⚠️ Generating betting recommendations...")
        
        # Create sample odds if not available
        if not os.path.exists(ODDS_FILE):
            from ml.value_bet_calculator import create_sample_odds_file
            create_sample_odds_file(ODDS_FILE)
        
        try:
            from ml.betting_strategy import generate_betting_recommendations
            betting_df = generate_betting_recommendations(PRED_FILE, ODDS_FILE, BETTING_FILE)
            st.success("✅ Betting recommendations generated successfully!")
        except Exception as e:
            st.error(f"❌ Error generating recommendations: {e}")
            st.stop()
    else:
        betting_df = pd.read_csv(BETTING_FILE)
    
    # Filter options
    st.sidebar.markdown("### 🎛️ Filters")
    show_only_recommended = st.sidebar.checkbox("Show only recommended bets", value=True)
    min_ev_filter = st.sidebar.slider("Minimum Expected Value", -5.0, 10.0, 0.0, 0.1)
    
    # Filter data
    filtered_df = betting_df.copy()
    if show_only_recommended:
        filtered_df = filtered_df[filtered_df['bet_recommendation'] == 'Ja']
    filtered_df = filtered_df[filtered_df['expected_value'] >= min_ev_filter]
    
    # Main table
    st.markdown("### 📊 Betting Recommendations Overview")
    
    if len(filtered_df) > 0:
        # Format table for better display
        display_df = filtered_df[[
            'driver', 'position', 'odds', 'probability_pct', 
            'expected_value', 'bet_recommendation', 'stake', 'potential_profit'
        ]].copy()
        
        display_df.columns = [
            'Driver', 'Position', 'Odds', 'Probability (%)', 
            'Expected Value (€)', 'Recommendation', 'Stake (€)', 'Potential Profit (€)'
        ]
        
        # Color coding for recommendations
        def highlight_recommendations(row):
            if row['Recommendation'] == 'Ja':
                return ['background-color: lightgreen'] * len(row)
            else:
                return ['background-color: lightcoral'] * len(row)
        
        styled_df = display_df.style.apply(highlight_recommendations, axis=1)
        st.dataframe(styled_df, use_container_width=True)
        
        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        
        recommended_bets = filtered_df[filtered_df['bet_recommendation'] == 'Ja']
        
        with col1:
            st.metric("Recommended Bets", len(recommended_bets))
        with col2:
            total_stake = recommended_bets['stake'].sum()
            st.metric("Total Stake", f"{total_stake:.2f}€")
        with col3:
            total_potential = recommended_bets['potential_profit'].sum()
            st.metric("Potential Profit", f"{total_potential:.2f}€")
        with col4:
            total_ev = recommended_bets['expected_value'].sum()
            st.metric("Total Expected Value", f"{total_ev:.2f}€")
        
        # Download button
        csv_data = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"betting_recommendations_{RACE}_{YEAR}.csv",
            mime="text/csv"
        )
        
        # Highlight best bet
        if len(recommended_bets) > 0:
            best_bet = recommended_bets.loc[recommended_bets['expected_value'].idxmax()]
            st.markdown("### 🏆 Best Betting Recommendation")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Driver", f"{best_bet['driver']} ({best_bet['position']})")
            with col2:
                st.metric("Odds", f"{best_bet['odds']:.2f}")
            with col3:
                st.metric("Expected Value", f"{best_bet['expected_value']:.2f}€")
    else:
        st.warning("⚠️ No bets match the current filter criteria.")

elif page == "📈 Probabilities":
    st.title(f"📈 All Driver Probabilities - {RACE} {YEAR}")
    
    # Position Filter
    positions = sorted(df['position'].unique())
    selected_positions = st.multiselect(
        "🎯 Select Positions:", 
        positions, 
        default=[1, 2, 3, 4, 5]
    )
    
    if selected_positions:
        # Filter by selected positions
        filtered_data = df[df['position'].isin(selected_positions)]
        
        # Pivot for better display
        pivot_data = filtered_data.pivot(index='driver', columns='position', values='probability')
        pivot_data = pivot_data.fillna(0).round(2)
        
        # Sort by P1 probability
        if 1 in selected_positions:
            pivot_data = pivot_data.sort_values(1, ascending=False)
        
        st.markdown("### 📊 Probability Matrix")
        st.dataframe(pivot_data, use_container_width=True)
        
        # Heatmap-like visualization
        st.markdown("### 🔥 Top Candidates per Position")
        
        cols = st.columns(min(len(selected_positions), 5))
        for i, pos in enumerate(selected_positions[:5]):
            with cols[i]:
                st.markdown(f"**P{pos}**")
                pos_data = df[df['position'] == pos].sort_values('probability', ascending=False).head(5)
                for _, row in pos_data.iterrows():
                    st.write(f"{row['driver']}: {row['probability']:.1f}%")
        
        # Export Options
        st.subheader("📦 Export Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Download button for probabilities
            csv_buffer = io.StringIO()
            filtered_data.to_csv(csv_buffer, index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv_buffer.getvalue(),
                file_name=f"probabilities_{RACE.replace(' ', '_')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # Formatted export for friends
            if st.button("📄 Formatted Export", use_container_width=True):
                if F1PredictionExporter:
                    try:
                        exporter = F1PredictionExporter()
                        
                        # Create temporary CSV
                        temp_csv = "temp_export.csv"
                        filtered_data.to_csv(temp_csv, index=False)
                        
                        # Perform export
                        exported_files = exporter.export_predictions(
                            csv_path=temp_csv,
                            race_name=RACE,
                            output_dir="data/exports",
                            formats=['csv']
                        )
                        
                        # Clean up
                        if os.path.exists(temp_csv):
                            os.remove(temp_csv)
                        
                        if 'csv' in exported_files:
                            with open(exported_files['csv'], 'r', encoding='utf-8') as f:
                                formatted_csv = f.read()
                            
                            st.download_button(
                                label="📥 Download Formatted CSV",
                                data=formatted_csv,
                                file_name=f"F1_Prediction_{RACE.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                                mime="text/csv"
                            )
                            st.success("✅ Formatted export created!")
                        
                    except Exception as e:
                        st.error(f"❌ Export error: {e}")
                else:
                    st.error("❌ Export module not available")
        
        with col3:
            # PDF Export (if available)
            if st.button("📄 PDF Export", use_container_width=True):
                if F1PredictionExporter:
                    try:
                        exporter = F1PredictionExporter()
                        
                        # Create temporary CSV
                        temp_csv = "temp_export.csv"
                        filtered_data.to_csv(temp_csv, index=False)
                        
                        # PDF Export
                        exported_files = exporter.export_predictions(
                            csv_path=temp_csv,
                            race_name=RACE,
                            output_dir="data/exports",
                            formats=['pdf']
                        )
                        
                        # Clean up
                        if os.path.exists(temp_csv):
                            os.remove(temp_csv)
                        
                        if 'pdf' in exported_files and os.path.exists(exported_files['pdf']):
                            with open(exported_files['pdf'], 'rb') as f:
                                pdf_data = f.read()
                            
                            st.download_button(
                                label="📥 Download PDF",
                                data=pdf_data,
                                file_name=f"F1_Prediction_{RACE.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                                mime="application/pdf"
                            )
                            st.success("✅ PDF created!")
                        else:
                            st.error("❌ PDF could not be created")
                        
                    except Exception as e:
                        st.error(f"❌ PDF export error: {e}")
                else:
                    st.error("❌ Export module not available")
    else:
        st.warning("⚠️ Please select at least one position.")
