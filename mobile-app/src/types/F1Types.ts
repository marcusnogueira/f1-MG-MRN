export interface RaceInfo {
  id: string;
  raceName: string;
  location: string;
  country: string;
  raceDate: string;
  raceTime?: string;
  circuit: string;
  round: number;
  season: number;
  isRaceWeekend: boolean;
  daysUntil: number;
  hoursUntil: number;
}

export interface Driver {
  id: string;
  code: string; // e.g., 'VER', 'HAM'
  firstName: string;
  lastName: string;
  fullName: string;
  team: string;
  teamColor: string;
  nationality: string;
  number: number;
  profileImage?: string;
}

export interface DriverPrediction {
  driver: Driver;
  predictedPosition: number;
  confidence: number;
  probability: number;
  features: {
    qualifyingPosition?: number;
    trackAffinity: number;
    teamStrength: number;
    momentum: number;
    recentForm: number[];
  };
}

export interface PositionProbability {
  driver: string;
  position: number;
  probability: number;
}

export interface BettingRecommendation {
  id: string;
  type: 'win' | 'podium' | 'top10' | 'head_to_head';
  driver: string;
  description: string;
  odds: number;
  impliedProbability: number;
  modelProbability: number;
  valueRating: number;
  expectedValue: number;
  confidence: 'low' | 'medium' | 'high';
  stake?: number;
  potentialReturn?: number;
}

export interface OddsData {
  driver: string;
  bookmaker: string;
  winOdds: number;
  podiumOdds?: number;
  top10Odds?: number;
  lastUpdated: string;
}

export interface ModelPerformance {
  accuracy: number;
  precision: number;
  recall: number;
  f1Score: number;
  roi: number;
  totalPredictions: number;
  correctPredictions: number;
  profitLoss: number;
  winRate: number;
  averageOdds: number;
  lastEvaluated: string;
  performanceByRace: RacePerformance[];
}

export interface RacePerformance {
  raceId: string;
  raceName: string;
  date: string;
  accuracy: number;
  roi: number;
  predictions: number;
  correct: number;
  profit: number;
}

export interface FeatureImportance {
  feature: string;
  importance: number;
  description: string;
}

export interface TrackCharacteristics {
  trackId: string;
  name: string;
  length: number;
  corners: number;
  drsZones: number;
  difficulty: 'low' | 'medium' | 'high';
  overtakingDifficulty: 'easy' | 'medium' | 'hard';
  weatherSensitivity: number;
  tyreDegradation: 'low' | 'medium' | 'high';
}

export interface WeatherData {
  temperature: number;
  humidity: number;
  windSpeed: number;
  windDirection: string;
  precipitation: number;
  conditions: 'sunny' | 'cloudy' | 'rainy' | 'stormy';
  forecast: WeatherForecast[];
}

export interface WeatherForecast {
  time: string;
  temperature: number;
  precipitation: number;
  conditions: string;
}

export interface SessionData {
  sessionType: 'practice1' | 'practice2' | 'practice3' | 'qualifying' | 'sprint' | 'race';
  startTime: string;
  endTime: string;
  status: 'upcoming' | 'live' | 'completed';
  results?: SessionResult[];
}

export interface SessionResult {
  position: number;
  driver: string;
  time?: string;
  gap?: string;
  laps?: number;
  status: 'finished' | 'dnf' | 'dns' | 'dsq';
}

export interface LiveTiming {
  currentLap: number;
  totalLaps: number;
  timeRemaining: string;
  raceStatus: 'not_started' | 'formation_lap' | 'racing' | 'safety_car' | 'virtual_safety_car' | 'red_flag' | 'finished';
  positions: LivePosition[];
  fastestLap?: {
    driver: string;
    time: string;
    lap: number;
  };
}

export interface LivePosition {
  position: number;
  driver: string;
  gap: string;
  interval: string;
  lastLapTime: string;
  bestLapTime: string;
  sector1: string;
  sector2: string;
  sector3: string;
  pitStops: number;
  tyre: 'soft' | 'medium' | 'hard' | 'intermediate' | 'wet';
  tyreAge: number;
}

export interface BettingStrategy {
  id: string;
  name: string;
  description: string;
  riskLevel: 'conservative' | 'moderate' | 'aggressive';
  minOdds: number;
  maxOdds: number;
  minConfidence: number;
  bankrollPercentage: number;
  active: boolean;
}

export interface UserSettings {
  notifications: {
    raceReminders: boolean;
    predictionUpdates: boolean;
    bettingAlerts: boolean;
    valueBetalerts: boolean;
  };
  betting: {
    defaultStake: number;
    maxStake: number;
    currency: string;
    autoCalculateStakes: boolean;
    strategies: BettingStrategy[];
  };
  display: {
    theme: 'light' | 'dark' | 'auto';
    language: string;
    timeZone: string;
    units: 'metric' | 'imperial';
  };
  privacy: {
    analytics: boolean;
    crashReporting: boolean;
    dataSharing: boolean;
  };
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  timestamp: string;
}

export interface ApiError {
  code: string;
  message: string;
  details?: any;
}