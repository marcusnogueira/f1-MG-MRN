#!/usr/bin/env python3
"""
F1 Predict Pro API Server
Provides REST API endpoints for the mobile application
"""

import os
import sys
import json
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ml.train_model import load_model, make_predictions
    from utils.feature_engineering import calculate_track_affinity, calculate_team_strength, calculate_momentum
except ImportError as e:
    print(f"Warning: Could not import ML modules: {e}")
    print("Running in mock mode")

app = Flask(__name__)
CORS(app)  # Enable CORS for mobile app

# Configuration
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
LIVE_DATA_DIR = os.path.join(DATA_DIR, 'live')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')

# Mock data for development
MOCK_DRIVERS = [
    {'id': 1, 'name': 'Max Verstappen', 'team': 'Red Bull Racing', 'number': 1},
    {'id': 2, 'name': 'Sergio Perez', 'team': 'Red Bull Racing', 'number': 11},
    {'id': 3, 'name': 'Lewis Hamilton', 'team': 'Mercedes', 'number': 44},
    {'id': 4, 'name': 'George Russell', 'team': 'Mercedes', 'number': 63},
    {'id': 5, 'name': 'Charles Leclerc', 'team': 'Ferrari', 'number': 16},
    {'id': 6, 'name': 'Carlos Sainz', 'team': 'Ferrari', 'number': 55},
    {'id': 7, 'name': 'Lando Norris', 'team': 'McLaren', 'number': 4},
    {'id': 8, 'name': 'Oscar Piastri', 'team': 'McLaren', 'number': 81},
    {'id': 9, 'name': 'Fernando Alonso', 'team': 'Aston Martin', 'number': 14},
    {'id': 10, 'name': 'Lance Stroll', 'team': 'Aston Martin', 'number': 18},
]

def load_live_data(filename):
    """Load data from live directory with fallback to mock data"""
    filepath = os.path.join(LIVE_DATA_DIR, filename)
    try:
        if filename.endswith('.json'):
            with open(filepath, 'r') as f:
                return json.load(f)
        elif filename.endswith('.csv'):
            return pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"Warning: {filename} not found, using mock data")
        return None
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None

def generate_mock_predictions():
    """Generate mock prediction data"""
    predictions = []
    for i, driver in enumerate(MOCK_DRIVERS):
        # Simulate realistic probabilities with some randomness
        base_prob = max(0.01, 0.25 - (i * 0.02) + np.random.normal(0, 0.05))
        
        prediction = {
            'driverId': driver['id'],
            'driver': driver['name'],
            'team': driver['team'],
            'winProbability': max(0.001, min(0.8, base_prob)),
            'podiumProbability': max(0.01, min(0.9, base_prob * 3)),
            'top5Probability': max(0.05, min(0.95, base_prob * 4)),
            'top10Probability': max(0.1, min(0.99, base_prob * 5)),
            'expectedPosition': i + 1 + np.random.normal(0, 2),
            'confidence': 'high' if i < 3 else 'medium' if i < 7 else 'low',
            'factors': {
                'trackAffinity': np.random.uniform(0.3, 0.9),
                'teamStrength': np.random.uniform(0.4, 0.95),
                'momentum': np.random.uniform(0.2, 0.8),
                'recentForm': np.random.uniform(0.3, 0.85)
            }
        }
        predictions.append(prediction)
    
    return sorted(predictions, key=lambda x: x['winProbability'], reverse=True)

def generate_mock_betting_recommendations():
    """Generate mock betting recommendations"""
    recommendations = []
    for i, driver in enumerate(MOCK_DRIVERS[:8]):  # Top 8 drivers
        odds = 2.0 + (i * 1.5) + np.random.uniform(-0.5, 0.5)
        model_prob = max(0.01, 0.3 - (i * 0.03))
        implied_prob = 1 / odds
        
        recommendation = {
            'id': f'bet_{driver["id"]}_{i}',
            'driver': driver['name'],
            'type': 'win' if i < 3 else 'podium' if i < 6 else 'top10',
            'description': f'{driver["name"]} to {"win" if i < 3 else "finish on podium" if i < 6 else "finish in top 10"}',
            'odds': odds,
            'impliedProbability': implied_prob,
            'modelProbability': model_prob,
            'valueRating': model_prob / implied_prob if implied_prob > 0 else 0,
            'expectedValue': (model_prob * (odds - 1)) - (1 - model_prob),
            'confidence': 'high' if i < 2 else 'medium' if i < 5 else 'low',
            'bookmaker': ['Bet365', 'William Hill', 'Paddy Power', 'Betfair'][i % 4]
        }
        recommendations.append(recommendation)
    
    return sorted(recommendations, key=lambda x: x['valueRating'], reverse=True)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/race/next', methods=['GET'])
def get_next_race():
    """Get next race information"""
    # Try to load from live data first
    race_data = load_live_data('next_race_info.json')
    
    if not race_data:
        # Generate mock data
        next_sunday = datetime.now() + timedelta(days=(6 - datetime.now().weekday()))
        race_data = {
            'name': 'Monaco Grand Prix',
            'circuit': 'Circuit de Monaco',
            'country': 'Monaco',
            'date': next_sunday.isoformat(),
            'time': '15:00',
            'timezone': 'CEST',
            'round': 6,
            'season': 2024,
            'weather': {
                'temperature': 24,
                'humidity': 65,
                'windSpeed': 12,
                'chanceOfRain': 20,
                'conditions': 'Partly Cloudy'
            },
            'sessions': {
                'practice1': (next_sunday - timedelta(days=2, hours=3)).isoformat(),
                'practice2': (next_sunday - timedelta(days=2)).isoformat(),
                'practice3': (next_sunday - timedelta(days=1, hours=3)).isoformat(),
                'qualifying': (next_sunday - timedelta(days=1)).isoformat(),
                'race': next_sunday.isoformat()
            }
        }
    
    return jsonify({
        'success': True,
        'data': race_data
    })

@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    """Get driver predictions for next race"""
    try:
        # Try to load real predictions
        predictions_data = load_live_data('predictions.json')
        
        if not predictions_data:
            predictions_data = generate_mock_predictions()
        
        return jsonify({
            'success': True,
            'data': predictions_data,
            'lastUpdated': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/betting/recommendations', methods=['GET'])
def get_betting_recommendations():
    """Get betting recommendations"""
    try:
        betting_data = load_live_data('betting_recommendations.json')
        
        if not betting_data:
            betting_data = generate_mock_betting_recommendations()
        
        return jsonify({
            'success': True,
            'data': betting_data,
            'lastUpdated': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/betting/odds', methods=['GET'])
def get_best_odds():
    """Get best available odds"""
    try:
        odds_data = load_live_data('best_odds.csv')
        
        if odds_data is None:
            # Generate mock odds data
            odds_data = []
            for driver in MOCK_DRIVERS:
                odds_data.append({
                    'driver': driver['name'],
                    'winOdds': 2.0 + np.random.uniform(0, 10),
                    'podiumOdds': 1.5 + np.random.uniform(0, 3),
                    'bookmaker': ['Bet365', 'William Hill', 'Paddy Power'][np.random.randint(0, 3)],
                    'lastUpdated': datetime.now().isoformat()
                })
        else:
            odds_data = odds_data.to_dict('records')
        
        return jsonify({
            'success': True,
            'data': odds_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analytics/performance', methods=['GET'])
def get_model_performance():
    """Get model performance metrics"""
    try:
        performance_data = {
            'accuracy': 0.83,
            'precision': 0.81,
            'recall': 0.79,
            'f1Score': 0.80,
            'trainingSamples': 2847,
            'lastUpdated': datetime.now().isoformat(),
            'confusionMatrix': [[45, 3, 2], [4, 38, 8], [1, 7, 42]]
        }
        
        return jsonify({
            'success': True,
            'data': performance_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analytics/features', methods=['GET'])
def get_feature_importance():
    """Get feature importance data"""
    try:
        features_data = [
            {'feature': 'track_affinity', 'importance': 0.28, 'description': 'Driver performance at similar track types'},
            {'feature': 'team_strength', 'importance': 0.24, 'description': 'Current team performance and car competitiveness'},
            {'feature': 'momentum', 'importance': 0.18, 'description': 'Recent race results and trending performance'},
            {'feature': 'qualifying_position', 'importance': 0.15, 'description': 'Starting grid position'},
            {'feature': 'weather_conditions', 'importance': 0.08, 'description': 'Weather impact on driver performance'},
            {'feature': 'tire_strategy', 'importance': 0.07, 'description': 'Tire compound and strategy effectiveness'}
        ]
        
        return jsonify({
            'success': True,
            'data': features_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analytics/track', methods=['GET'])
def get_track_characteristics():
    """Get current track characteristics"""
    try:
        track_data = {
            'trackName': 'Circuit de Monaco',
            'length': 3.337,
            'lapRecord': '1:12.909',
            'drsZones': 1,
            'speedImportance': 0.3,
            'overtakingDifficulty': 0.9,
            'tireDegradation': 0.4,
            'weatherImpact': 0.7,
            'elevationChange': 0.6
        }
        
        return jsonify({
            'success': True,
            'data': track_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/countdown', methods=['GET'])
def get_race_countdown():
    """Get race countdown information"""
    try:
        countdown_data = load_live_data('race_countdown.json')
        
        if not countdown_data:
            next_sunday = datetime.now() + timedelta(days=(6 - datetime.now().weekday()))
            race_time = next_sunday.replace(hour=15, minute=0, second=0, microsecond=0)
            
            countdown_data = {
                'raceDateTime': race_time.isoformat(),
                'timeUntilRace': str(race_time - datetime.now()),
                'isLive': False,
                'status': 'upcoming'
            }
        
        return jsonify({
            'success': True,
            'data': countdown_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # Create directories if they don't exist
    os.makedirs(LIVE_DATA_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    
    print("Starting F1 Predict Pro API Server...")
    print(f"Data directory: {DATA_DIR}")
    print(f"Live data directory: {LIVE_DATA_DIR}")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True
    )