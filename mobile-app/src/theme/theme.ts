import { MD3LightTheme as DefaultTheme } from 'react-native-paper';

// F1-inspired color palette
const colors = {
  // Primary F1 Red
  primary: '#E10600',
  onPrimary: '#FFFFFF',
  primaryContainer: '#FFDDDB',
  onPrimaryContainer: '#410002',
  
  // Secondary colors
  secondary: '#1976D2',
  onSecondary: '#FFFFFF',
  secondaryContainer: '#D1E4FF',
  onSecondaryContainer: '#001D36',
  
  // Tertiary (Gold for podium/wins)
  tertiary: '#FFD700',
  onTertiary: '#000000',
  tertiaryContainer: '#FFF8DC',
  onTertiaryContainer: '#1F1A00',
  
  // Error
  error: '#BA1A1A',
  onError: '#FFFFFF',
  errorContainer: '#FFDAD6',
  onErrorContainer: '#410002',
  
  // Background
  background: '#FFFBFF',
  onBackground: '#1C1B1F',
  
  // Surface
  surface: '#FFFBFF',
  onSurface: '#1C1B1F',
  surfaceVariant: '#F2F0F4',
  onSurfaceVariant: '#45464A',
  
  // Outline
  outline: '#767680',
  outlineVariant: '#C6C5D0',
  
  // Additional F1 colors
  success: '#4CAF50',
  warning: '#FF9800',
  info: '#2196F3',
  
  // Team colors (for driver cards)
  redBull: '#0600EF',
  mercedes: '#00D2BE',
  ferrari: '#DC143C',
  mclaren: '#FF8700',
  astonMartin: '#006F62',
  alpine: '#0090FF',
  williams: '#005AFF',
  haas: '#FFFFFF',
  alfaRomeo: '#900000',
  alphaTauri: '#2B4562',
};

export const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    ...colors,
  },
  fonts: {
    ...DefaultTheme.fonts,
    titleLarge: {
      ...DefaultTheme.fonts.titleLarge,
      fontWeight: '700' as const,
    },
    titleMedium: {
      ...DefaultTheme.fonts.titleMedium,
      fontWeight: '600' as const,
    },
  },
  roundness: 12,
};

export type AppTheme = typeof theme;

// Utility function to get team color
export const getTeamColor = (team: string): string => {
  const teamColors: { [key: string]: string } = {
    'Red Bull': colors.redBull,
    'Mercedes': colors.mercedes,
    'Ferrari': colors.ferrari,
    'McLaren': colors.mclaren,
    'Aston Martin': colors.astonMartin,
    'Alpine': colors.alpine,
    'Williams': colors.williams,
    'Haas': colors.haas,
    'Alfa Romeo': colors.alfaRomeo,
    'AlphaTauri': colors.alphaTauri,
  };
  
  return teamColors[team] || colors.outline;
};

// Position colors for race results
export const getPositionColor = (position: number): string => {
  if (position === 1) return colors.tertiary; // Gold
  if (position === 2) return '#C0C0C0'; // Silver
  if (position === 3) return '#CD7F32'; // Bronze
  if (position <= 10) return colors.success; // Points
  return colors.outline; // No points
};