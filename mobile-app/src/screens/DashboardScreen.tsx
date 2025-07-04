import React, { useEffect } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  RefreshControl,
  Dimensions,
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  Chip,
  Surface,
  Text,
  ActivityIndicator,
} from 'react-native-paper';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { useF1Data } from '../context/F1DataContext';
import { theme, getPositionColor } from '../theme/theme';
import { format } from 'date-fns';

const { width } = Dimensions.get('window');

const DashboardScreen: React.FC = () => {
  const { state, actions } = useF1Data();
  const {
    nextRace,
    raceCountdown,
    driverPredictions,
    valueBets,
    modelPerformance,
    loading,
    error,
    lastUpdated,
  } = state;

  useEffect(() => {
    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      actions.refreshData();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const onRefresh = () => {
    actions.refreshData();
  };

  const renderRaceCountdown = () => {
    if (!nextRace) return null;

    return (
      <Card style={styles.raceCard} elevation={4}>
        <LinearGradient
          colors={[theme.colors.primary, theme.colors.secondary]}
          style={styles.raceGradient}
        >
          <Card.Content>
            <View style={styles.raceHeader}>
              <Ionicons name="flag" size={24} color={theme.colors.onPrimary} />
              <Title style={[styles.raceTitle, { color: theme.colors.onPrimary }]}>
                {nextRace.raceName}
              </Title>
            </View>
            
            <View style={styles.raceInfo}>
              <View style={styles.raceDetail}>
                <Ionicons name="location" size={16} color={theme.colors.onPrimary} />
                <Text style={[styles.raceText, { color: theme.colors.onPrimary }]}>
                  {nextRace.location}, {nextRace.country}
                </Text>
              </View>
              
              <View style={styles.raceDetail}>
                <Ionicons name="calendar" size={16} color={theme.colors.onPrimary} />
                <Text style={[styles.raceText, { color: theme.colors.onPrimary }]}>
                  {format(new Date(nextRace.raceDate), 'MMM dd, yyyy - HH:mm')}
                </Text>
              </View>
            </View>

            <Surface style={styles.countdownSurface}>
              <View style={styles.countdownContainer}>
                <Ionicons name="time" size={20} color={theme.colors.primary} />
                <Text style={styles.countdownText}>{raceCountdown}</Text>
              </View>
            </Surface>
          </Card.Content>
        </LinearGradient>
      </Card>
    );
  };

  const renderTopPredictions = () => {
    const topDrivers = driverPredictions.slice(0, 5);
    
    return (
      <Card style={styles.card} elevation={2}>
        <Card.Content>
          <View style={styles.sectionHeader}>
            <Ionicons name="trophy" size={20} color={theme.colors.primary} />
            <Title style={styles.sectionTitle}>Top 5 Predictions</Title>
          </View>
          
          {topDrivers.map((prediction, index) => (
            <View key={prediction.driver.code} style={styles.predictionRow}>
              <View style={styles.positionContainer}>
                <Surface 
                  style={[
                    styles.positionBadge,
                    { backgroundColor: getPositionColor(prediction.predictedPosition) }
                  ]}
                >
                  <Text style={styles.positionText}>{prediction.predictedPosition}</Text>
                </Surface>
              </View>
              
              <View style={styles.driverInfo}>
                <Text style={styles.driverName}>{prediction.driver.fullName}</Text>
                <Text style={styles.teamName}>{prediction.driver.team}</Text>
              </View>
              
              <View style={styles.confidenceContainer}>
                <Chip 
                  mode="outlined" 
                  compact
                  style={[
                    styles.confidenceChip,
                    { borderColor: theme.colors.primary }
                  ]}
                >
                  {Math.round(prediction.confidence * 100)}%
                </Chip>
              </View>
            </View>
          ))}
        </Card.Content>
      </Card>
    );
  };

  const renderValueBets = () => {
    const topValueBets = valueBets.slice(0, 3);
    
    if (topValueBets.length === 0) {
      return (
        <Card style={styles.card} elevation={2}>
          <Card.Content>
            <View style={styles.sectionHeader}>
              <Ionicons name="trending-up" size={20} color={theme.colors.tertiary} />
              <Title style={styles.sectionTitle}>Value Bets</Title>
            </View>
            <Paragraph>No value bets available at the moment.</Paragraph>
          </Card.Content>
        </Card>
      );
    }

    return (
      <Card style={styles.card} elevation={2}>
        <Card.Content>
          <View style={styles.sectionHeader}>
            <Ionicons name="trending-up" size={20} color={theme.colors.tertiary} />
            <Title style={styles.sectionTitle}>Top Value Bets</Title>
          </View>
          
          {topValueBets.map((bet, index) => (
            <Surface key={bet.id} style={styles.valueBetSurface}>
              <View style={styles.valueBetHeader}>
                <Text style={styles.valueBetDriver}>{bet.driver}</Text>
                <Chip 
                  mode="flat"
                  style={[
                    styles.valueRatingChip,
                    { backgroundColor: theme.colors.tertiary }
                  ]}
                >
                  {Math.round(bet.valueRating * 100)}% Value
                </Chip>
              </View>
              
              <Text style={styles.valueBetDescription}>{bet.description}</Text>
              
              <View style={styles.valueBetStats}>
                <View style={styles.valueBetStat}>
                  <Text style={styles.valueBetStatLabel}>Odds</Text>
                  <Text style={styles.valueBetStatValue}>{bet.odds.toFixed(2)}</Text>
                </View>
                <View style={styles.valueBetStat}>
                  <Text style={styles.valueBetStatLabel}>Expected Value</Text>
                  <Text style={styles.valueBetStatValue}>+{(bet.expectedValue * 100).toFixed(1)}%</Text>
                </View>
              </View>
            </Surface>
          ))}
        </Card.Content>
      </Card>
    );
  };

  const renderModelPerformance = () => {
    if (!modelPerformance) return null;

    return (
      <Card style={styles.card} elevation={2}>
        <Card.Content>
          <View style={styles.sectionHeader}>
            <Ionicons name="analytics" size={20} color={theme.colors.secondary} />
            <Title style={styles.sectionTitle}>Model Performance</Title>
          </View>
          
          <View style={styles.performanceGrid}>
            <View style={styles.performanceItem}>
              <Text style={styles.performanceValue}>
                {Math.round(modelPerformance.accuracy * 100)}%
              </Text>
              <Text style={styles.performanceLabel}>Accuracy</Text>
            </View>
            
            <View style={styles.performanceItem}>
              <Text style={[styles.performanceValue, { color: theme.colors.success }]}>
                +{Math.round(modelPerformance.roi * 100)}%
              </Text>
              <Text style={styles.performanceLabel}>ROI</Text>
            </View>
            
            <View style={styles.performanceItem}>
              <Text style={styles.performanceValue}>
                {modelPerformance.correctPredictions}/{modelPerformance.totalPredictions}
              </Text>
              <Text style={styles.performanceLabel}>Predictions</Text>
            </View>
            
            <View style={styles.performanceItem}>
              <Text style={[styles.performanceValue, { color: theme.colors.success }]}>
                ${modelPerformance.profitLoss.toFixed(0)}
              </Text>
              <Text style={styles.performanceLabel}>Profit</Text>
            </View>
          </View>
        </Card.Content>
      </Card>
    );
  };

  const renderQuickActions = () => {
    return (
      <Card style={styles.card} elevation={2}>
        <Card.Content>
          <Title style={styles.sectionTitle}>Quick Actions</Title>
          
          <View style={styles.actionButtons}>
            <Button 
              mode="contained" 
              icon="refresh"
              style={styles.actionButton}
              onPress={onRefresh}
              loading={loading}
            >
              Refresh Data
            </Button>
            
            <Button 
              mode="outlined" 
              icon="chart-line"
              style={styles.actionButton}
            >
              View Analytics
            </Button>
          </View>
        </Card.Content>
      </Card>
    );
  };

  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Ionicons name="warning" size={48} color={theme.colors.error} />
        <Text style={styles.errorText}>Failed to load data</Text>
        <Button mode="contained" onPress={onRefresh}>
          Retry
        </Button>
      </View>
    );
  }

  return (
    <ScrollView 
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={loading} onRefresh={onRefresh} />
      }
    >
      {renderRaceCountdown()}
      {renderTopPredictions()}
      {renderValueBets()}
      {renderModelPerformance()}
      {renderQuickActions()}
      
      {lastUpdated && (
        <View style={styles.lastUpdated}>
          <Text style={styles.lastUpdatedText}>
            Last updated: {format(lastUpdated, 'HH:mm:ss')}
          </Text>
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  raceCard: {
    margin: 16,
    marginBottom: 8,
    borderRadius: 16,
    overflow: 'hidden',
  },
  raceGradient: {
    borderRadius: 16,
  },
  raceHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  raceTitle: {
    marginLeft: 8,
    fontSize: 20,
    fontWeight: 'bold',
  },
  raceInfo: {
    marginBottom: 16,
  },
  raceDetail: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  raceText: {
    marginLeft: 6,
    fontSize: 14,
  },
  countdownSurface: {
    borderRadius: 12,
    padding: 12,
    backgroundColor: theme.colors.surface,
  },
  countdownContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  countdownText: {
    marginLeft: 8,
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.primary,
  },
  card: {
    margin: 16,
    marginTop: 8,
    borderRadius: 12,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionTitle: {
    marginLeft: 8,
    fontSize: 18,
  },
  predictionRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.outlineVariant,
  },
  positionContainer: {
    width: 40,
  },
  positionBadge: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  positionText: {
    color: theme.colors.onPrimary,
    fontWeight: 'bold',
    fontSize: 14,
  },
  driverInfo: {
    flex: 1,
    marginLeft: 12,
  },
  driverName: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.onSurface,
  },
  teamName: {
    fontSize: 12,
    color: theme.colors.onSurfaceVariant,
  },
  confidenceContainer: {
    alignItems: 'flex-end',
  },
  confidenceChip: {
    height: 28,
  },
  valueBetSurface: {
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
    backgroundColor: theme.colors.surfaceVariant,
  },
  valueBetHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  valueBetDriver: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.onSurface,
  },
  valueRatingChip: {
    height: 24,
  },
  valueBetDescription: {
    fontSize: 14,
    color: theme.colors.onSurfaceVariant,
    marginBottom: 8,
  },
  valueBetStats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  valueBetStat: {
    alignItems: 'center',
  },
  valueBetStatLabel: {
    fontSize: 12,
    color: theme.colors.onSurfaceVariant,
  },
  valueBetStatValue: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.onSurface,
  },
  performanceGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  performanceItem: {
    width: '48%',
    alignItems: 'center',
    marginBottom: 16,
  },
  performanceValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.primary,
  },
  performanceLabel: {
    fontSize: 12,
    color: theme.colors.onSurfaceVariant,
    marginTop: 4,
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  actionButton: {
    flex: 1,
    marginHorizontal: 4,
  },
  lastUpdated: {
    alignItems: 'center',
    padding: 16,
  },
  lastUpdatedText: {
    fontSize: 12,
    color: theme.colors.onSurfaceVariant,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  errorText: {
    fontSize: 18,
    color: theme.colors.error,
    marginVertical: 16,
    textAlign: 'center',
  },
});

export default DashboardScreen;