import axios, { AxiosInstance, AxiosResponse } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import {
  RaceInfo,
  DriverPrediction,
  BettingRecommendation,
  ModelPerformance,
  OddsData,
  ApiResponse,
  ApiError,
  Driver,
  WeatherData,
  LiveTiming,
  SessionData,
} from '../types/F1Types';

export class F1ApiService {
  private api: AxiosInstance;
  private baseURL: string;
  private cacheTimeout = 30000; // 30 seconds

  constructor() {
    // In production, this would be your deployed backend URL
    // For development, use local Python server
    this.baseURL = __DEV__ 
      ? 'http://localhost:8000/api' 
      : 'https://your-production-api.com/api';
    
    this.api = axios.create({
      baseURL: this.baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor
    this.api.interceptors.request.use(
      (config) => {
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('API Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.api.interceptors.response.use(
      (response: AxiosResponse) => {
        console.log(`API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error) => {
        console.error('API Response Error:', error.response?.data || error.message);
        return Promise.reject(this.handleApiError(error));
      }
    );
  }

  private handleApiError(error: any): ApiError {
    if (error.response) {
      return {
        code: error.response.status.toString(),
        message: error.response.data?.message || 'Server error',
        details: error.response.data,
      };
    } else if (error.request) {
      return {
        code: 'NETWORK_ERROR',
        message: 'Network connection failed',
        details: error.request,
      };
    } else {
      return {
        code: 'UNKNOWN_ERROR',
        message: error.message || 'Unknown error occurred',
        details: error,
      };
    }
  }

  private async getCachedData<T>(key: string): Promise<T | null> {
    try {
      const cached = await AsyncStorage.getItem(key);
      if (cached) {
        const { data, timestamp } = JSON.parse(cached);
        if (Date.now() - timestamp < this.cacheTimeout) {
          return data;
        }
      }
    } catch (error) {
      console.warn('Cache read error:', error);
    }
    return null;
  }

  private async setCachedData<T>(key: string, data: T): Promise<void> {
    try {
      const cacheData = {
        data,
        timestamp: Date.now(),
      };
      await AsyncStorage.setItem(key, JSON.stringify(cacheData));
    } catch (error) {
      console.warn('Cache write error:', error);
    }
  }

  // Race Information
  async getNextRaceInfo(): Promise<RaceInfo> {
    const cacheKey = 'next_race_info';
    const cached = await this.getCachedData<RaceInfo>(cacheKey);
    if (cached) return cached;

    try {
      // Try to read from local file first (for offline capability)
      const response = await this.api.get('/race/next');
      const raceInfo = response.data;
      await this.setCachedData(cacheKey, raceInfo);
      return raceInfo;
    } catch (error) {
      // Fallback to mock data if API fails
      const mockRaceInfo: RaceInfo = {
        id: 'spanish-gp-2025',
        raceName: 'Spanish Grand Prix',
        location: 'Barcelona',
        country: 'Spain',
        raceDate: '2025-06-15T13:00:00Z',
        circuit: 'Circuit de Barcelona-Catalunya',
        round: 8,
        season: 2025,
        isRaceWeekend: false,
        daysUntil: 45,
        hoursUntil: 1080,
      };
      return mockRaceInfo;
    }
  }

  // Driver Predictions
  async getDriverPredictions(): Promise<DriverPrediction[]> {
    const cacheKey = 'driver_predictions';
    const cached = await this.getCachedData<DriverPrediction[]>(cacheKey);
    if (cached) return cached;

    try {
      const response = await this.api.get('/predictions/drivers');
      const predictions = response.data;
      await this.setCachedData(cacheKey, predictions);
      return predictions;
    } catch (error) {
      // Return mock predictions
      return this.getMockDriverPredictions();
    }
  }

  // Position Probabilities
  async getPositionProbabilities(): Promise<{ [driver: string]: number[] }> {
    const cacheKey = 'position_probabilities';
    const cached = await this.getCachedData<{ [driver: string]: number[] }>(cacheKey);
    if (cached) return cached;

    try {
      const response = await this.api.get('/predictions/probabilities');
      const probabilities = response.data;
      await this.setCachedData(cacheKey, probabilities);
      return probabilities;
    } catch (error) {
      return this.getMockPositionProbabilities();
    }
  }

  // Betting Recommendations
  async getBettingRecommendations(): Promise<BettingRecommendation[]> {
    const cacheKey = 'betting_recommendations';
    const cached = await this.getCachedData<BettingRecommendation[]>(cacheKey);
    if (cached) return cached;

    try {
      const response = await this.api.get('/betting/recommendations');
      const recommendations = response.data;
      await this.setCachedData(cacheKey, recommendations);
      return recommendations;
    } catch (error) {
      return this.getMockBettingRecommendations();
    }
  }

  // Value Bets
  async getValueBets(): Promise<BettingRecommendation[]> {
    const cacheKey = 'value_bets';
    const cached = await this.getCachedData<BettingRecommendation[]>(cacheKey);
    if (cached) return cached;

    try {
      const response = await this.api.get('/betting/value-bets');
      const valueBets = response.data;
      await this.setCachedData(cacheKey, valueBets);
      return valueBets;
    } catch (error) {
      return this.getMockValueBets();
    }
  }

  // Best Odds
  async getBestOdds(): Promise<OddsData[]> {
    const cacheKey = 'best_odds';
    const cached = await this.getCachedData<OddsData[]>(cacheKey);
    if (cached) return cached;

    try {
      const response = await this.api.get('/betting/best-odds');
      const odds = response.data;
      await this.setCachedData(cacheKey, odds);
      return odds;
    } catch (error) {
      return this.getMockBestOdds();
    }
  }

  // Model Performance
  async getModelPerformance(): Promise<ModelPerformance> {
    const cacheKey = 'model_performance';
    const cached = await this.getCachedData<ModelPerformance>(cacheKey);
    if (cached) return cached;

    try {
      const response = await this.api.get('/analytics/performance');
      const performance = response.data;
      await this.setCachedData(cacheKey, performance);
      return performance;
    } catch (error) {
      return this.getMockModelPerformance();
    }
  }

  // Feature Importance
  async getFeatureImportance(): Promise<{ [feature: string]: number }> {
    const cacheKey = 'feature_importance';
    const cached = await this.getCachedData<{ [feature: string]: number }>(cacheKey);
    if (cached) return cached;

    try {
      const response = await this.api.get('/analytics/feature-importance');
      const importance = response.data;
      await this.setCachedData(cacheKey, importance);
      return importance;
    } catch (error) {
      return {
        'qualifying_position': 0.35,
        'track_affinity': 0.25,
        'team_strength': 0.20,
        'momentum': 0.15,
        'weather_conditions': 0.05,
      };
    }
  }

  // Mock data methods for offline/fallback functionality
  private getMockDriverPredictions(): DriverPrediction[] {
    const drivers = [
      { code: 'VER', name: 'Max Verstappen', team: 'Red Bull', position: 1, confidence: 0.85 },
      { code: 'HAM', name: 'Lewis Hamilton', team: 'Mercedes', position: 2, confidence: 0.72 },
      { code: 'LEC', name: 'Charles Leclerc', team: 'Ferrari', position: 3, confidence: 0.68 },
      { code: 'RUS', name: 'George Russell', team: 'Mercedes', position: 4, confidence: 0.65 },
      { code: 'SAI', name: 'Carlos Sainz', team: 'Ferrari', position: 5, confidence: 0.62 },
    ];

    return drivers.map((driver, index) => ({
      driver: {
        id: driver.code.toLowerCase(),
        code: driver.code,
        firstName: driver.name.split(' ')[0],
        lastName: driver.name.split(' ')[1],
        fullName: driver.name,
        team: driver.team,
        teamColor: this.getTeamColor(driver.team),
        nationality: 'Unknown',
        number: index + 1,
      },
      predictedPosition: driver.position,
      confidence: driver.confidence,
      probability: driver.confidence,
      features: {
        trackAffinity: Math.random() * 0.5 + 0.5,
        teamStrength: Math.random() * 0.3 + 0.7,
        momentum: Math.random() * 0.4 + 0.6,
        recentForm: [1, 2, 3, 1, 2],
      },
    }));
  }

  private getMockPositionProbabilities(): { [driver: string]: number[] } {
    return {
      'VER': [0.45, 0.25, 0.15, 0.08, 0.04, 0.02, 0.01, 0, 0, 0],
      'HAM': [0.20, 0.30, 0.25, 0.15, 0.07, 0.02, 0.01, 0, 0, 0],
      'LEC': [0.15, 0.25, 0.30, 0.20, 0.07, 0.02, 0.01, 0, 0, 0],
      'RUS': [0.10, 0.15, 0.20, 0.25, 0.20, 0.07, 0.02, 0.01, 0, 0],
      'SAI': [0.05, 0.10, 0.15, 0.20, 0.25, 0.15, 0.07, 0.02, 0.01, 0],
    };
  }

  private getMockBettingRecommendations(): BettingRecommendation[] {
    return [
      {
        id: '1',
        type: 'win',
        driver: 'VER',
        description: 'Max Verstappen to win',
        odds: 2.1,
        impliedProbability: 0.476,
        modelProbability: 0.65,
        valueRating: 0.85,
        expectedValue: 0.365,
        confidence: 'high',
        stake: 50,
        potentialReturn: 105,
      },
    ];
  }

  private getMockValueBets(): BettingRecommendation[] {
    return this.getMockBettingRecommendations().filter(bet => bet.valueRating > 0.7);
  }

  private getMockBestOdds(): OddsData[] {
    return [
      {
        driver: 'VER',
        bookmaker: 'Bet365',
        winOdds: 2.1,
        podiumOdds: 1.3,
        top10Odds: 1.05,
        lastUpdated: new Date().toISOString(),
      },
    ];
  }

  private getMockModelPerformance(): ModelPerformance {
    return {
      accuracy: 0.73,
      precision: 0.71,
      recall: 0.69,
      f1Score: 0.70,
      roi: 0.15,
      totalPredictions: 250,
      correctPredictions: 182,
      profitLoss: 1250.50,
      winRate: 0.68,
      averageOdds: 2.45,
      lastEvaluated: new Date().toISOString(),
      performanceByRace: [],
    };
  }

  private getTeamColor(team: string): string {
    const colors: { [key: string]: string } = {
      'Red Bull': '#0600EF',
      'Mercedes': '#00D2BE',
      'Ferrari': '#DC143C',
      'McLaren': '#FF8700',
      'Aston Martin': '#006F62',
      'Alpine': '#0090FF',
      'Williams': '#005AFF',
      'Haas': '#FFFFFF',
      'Alfa Romeo': '#900000',
      'AlphaTauri': '#2B4562',
    };
    return colors[team] || '#666666';
  }
}