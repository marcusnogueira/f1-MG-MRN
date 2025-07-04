import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { F1ApiService } from '../services/F1ApiService';
import { RaceInfo, DriverPrediction, BettingRecommendation, ModelPerformance } from '../types/F1Types';

interface F1DataState {
  // Race Information
  nextRace: RaceInfo | null;
  raceCountdown: string;
  
  // Predictions
  driverPredictions: DriverPrediction[];
  positionProbabilities: { [driver: string]: number[] };
  
  // Betting
  bettingRecommendations: BettingRecommendation[];
  valueBets: BettingRecommendation[];
  bestOdds: any[];
  
  // Analytics
  modelPerformance: ModelPerformance | null;
  featureImportance: { [feature: string]: number };
  
  // UI State
  loading: boolean;
  error: string | null;
  lastUpdated: Date | null;
}

type F1DataAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_NEXT_RACE'; payload: RaceInfo }
  | { type: 'SET_RACE_COUNTDOWN'; payload: string }
  | { type: 'SET_DRIVER_PREDICTIONS'; payload: DriverPrediction[] }
  | { type: 'SET_POSITION_PROBABILITIES'; payload: { [driver: string]: number[] } }
  | { type: 'SET_BETTING_RECOMMENDATIONS'; payload: BettingRecommendation[] }
  | { type: 'SET_VALUE_BETS'; payload: BettingRecommendation[] }
  | { type: 'SET_BEST_ODDS'; payload: any[] }
  | { type: 'SET_MODEL_PERFORMANCE'; payload: ModelPerformance }
  | { type: 'SET_FEATURE_IMPORTANCE'; payload: { [feature: string]: number } }
  | { type: 'SET_LAST_UPDATED'; payload: Date };

const initialState: F1DataState = {
  nextRace: null,
  raceCountdown: '',
  driverPredictions: [],
  positionProbabilities: {},
  bettingRecommendations: [],
  valueBets: [],
  bestOdds: [],
  modelPerformance: null,
  featureImportance: {},
  loading: false,
  error: null,
  lastUpdated: null,
};

function f1DataReducer(state: F1DataState, action: F1DataAction): F1DataState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: false };
    case 'SET_NEXT_RACE':
      return { ...state, nextRace: action.payload };
    case 'SET_RACE_COUNTDOWN':
      return { ...state, raceCountdown: action.payload };
    case 'SET_DRIVER_PREDICTIONS':
      return { ...state, driverPredictions: action.payload };
    case 'SET_POSITION_PROBABILITIES':
      return { ...state, positionProbabilities: action.payload };
    case 'SET_BETTING_RECOMMENDATIONS':
      return { ...state, bettingRecommendations: action.payload };
    case 'SET_VALUE_BETS':
      return { ...state, valueBets: action.payload };
    case 'SET_BEST_ODDS':
      return { ...state, bestOdds: action.payload };
    case 'SET_MODEL_PERFORMANCE':
      return { ...state, modelPerformance: action.payload };
    case 'SET_FEATURE_IMPORTANCE':
      return { ...state, featureImportance: action.payload };
    case 'SET_LAST_UPDATED':
      return { ...state, lastUpdated: action.payload };
    default:
      return state;
  }
}

interface F1DataContextType {
  state: F1DataState;
  actions: {
    refreshData: () => Promise<void>;
    loadNextRace: () => Promise<void>;
    loadPredictions: () => Promise<void>;
    loadBettingData: () => Promise<void>;
    loadAnalytics: () => Promise<void>;
    updateCountdown: () => void;
  };
}

const F1DataContext = createContext<F1DataContextType | undefined>(undefined);

export function F1DataProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(f1DataReducer, initialState);
  const apiService = new F1ApiService();

  const actions = {
    refreshData: async () => {
      dispatch({ type: 'SET_LOADING', payload: true });
      try {
        await Promise.all([
          actions.loadNextRace(),
          actions.loadPredictions(),
          actions.loadBettingData(),
          actions.loadAnalytics(),
        ]);
        dispatch({ type: 'SET_LAST_UPDATED', payload: new Date() });
      } catch (error) {
        dispatch({ type: 'SET_ERROR', payload: error instanceof Error ? error.message : 'Unknown error' });
      } finally {
        dispatch({ type: 'SET_LOADING', payload: false });
      }
    },

    loadNextRace: async () => {
      try {
        const raceInfo = await apiService.getNextRaceInfo();
        dispatch({ type: 'SET_NEXT_RACE', payload: raceInfo });
        actions.updateCountdown();
      } catch (error) {
        console.error('Failed to load next race:', error);
      }
    },

    loadPredictions: async () => {
      try {
        const [predictions, probabilities] = await Promise.all([
          apiService.getDriverPredictions(),
          apiService.getPositionProbabilities(),
        ]);
        dispatch({ type: 'SET_DRIVER_PREDICTIONS', payload: predictions });
        dispatch({ type: 'SET_POSITION_PROBABILITIES', payload: probabilities });
      } catch (error) {
        console.error('Failed to load predictions:', error);
      }
    },

    loadBettingData: async () => {
      try {
        const [recommendations, valueBets, bestOdds] = await Promise.all([
          apiService.getBettingRecommendations(),
          apiService.getValueBets(),
          apiService.getBestOdds(),
        ]);
        dispatch({ type: 'SET_BETTING_RECOMMENDATIONS', payload: recommendations });
        dispatch({ type: 'SET_VALUE_BETS', payload: valueBets });
        dispatch({ type: 'SET_BEST_ODDS', payload: bestOdds });
      } catch (error) {
        console.error('Failed to load betting data:', error);
      }
    },

    loadAnalytics: async () => {
      try {
        const [performance, featureImportance] = await Promise.all([
          apiService.getModelPerformance(),
          apiService.getFeatureImportance(),
        ]);
        dispatch({ type: 'SET_MODEL_PERFORMANCE', payload: performance });
        dispatch({ type: 'SET_FEATURE_IMPORTANCE', payload: featureImportance });
      } catch (error) {
        console.error('Failed to load analytics:', error);
      }
    },

    updateCountdown: () => {
      if (state.nextRace?.raceDate) {
        const now = new Date();
        const raceDate = new Date(state.nextRace.raceDate);
        const timeDiff = raceDate.getTime() - now.getTime();
        
        if (timeDiff > 0) {
          const days = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
          const hours = Math.floor((timeDiff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
          const minutes = Math.floor((timeDiff % (1000 * 60 * 60)) / (1000 * 60));
          const seconds = Math.floor((timeDiff % (1000 * 60)) / 1000);
          
          let countdown = '';
          if (days > 0) {
            countdown = `${days}d ${hours}h ${minutes}m ${seconds}s`;
          } else if (hours > 0) {
            countdown = `${hours}h ${minutes}m ${seconds}s`;
          } else {
            countdown = `${minutes}m ${seconds}s`;
          }
          
          dispatch({ type: 'SET_RACE_COUNTDOWN', payload: countdown });
        } else {
          dispatch({ type: 'SET_RACE_COUNTDOWN', payload: 'Race has started!' });
        }
      }
    },
  };

  // Auto-refresh countdown every second
  useEffect(() => {
    const interval = setInterval(actions.updateCountdown, 1000);
    return () => clearInterval(interval);
  }, [state.nextRace]);

  // Initial data load
  useEffect(() => {
    actions.refreshData();
  }, []);

  return (
    <F1DataContext.Provider value={{ state, actions }}>
      {children}
    </F1DataContext.Provider>
  );
}

export function useF1Data() {
  const context = useContext(F1DataContext);
  if (context === undefined) {
    throw new Error('useF1Data must be used within a F1DataProvider');
  }
  return context;
}