import React, { useState } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  RefreshControl,
  Alert,
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  Chip,
  Surface,
  Text,
  TextInput,
  Switch,
  Divider,
  DataTable,
} from 'react-native-paper';
import { Ionicons } from '@expo/vector-icons';
import { useF1Data } from '../context/F1DataContext';
import { theme } from '../theme/theme';
import { BettingRecommendation } from '../types/F1Types';

type BetType = 'all' | 'win' | 'podium' | 'top10' | 'head_to_head';
type ConfidenceLevel = 'all' | 'high' | 'medium' | 'low';

const BettingScreen: React.FC = () => {
  const { state, actions } = useF1Data();
  const {
    bettingRecommendations,
    valueBets,
    bestOdds,
    loading,
    error,
  } = state;

  const [selectedBetType, setSelectedBetType] = useState<BetType>('all');
  const [selectedConfidence, setSelectedConfidence] = useState<ConfidenceLevel>('all');
  const [showValueBetsOnly, setShowValueBetsOnly] = useState(false);
  const [defaultStake, setDefaultStake] = useState('10');
  const [autoCalculateStakes, setAutoCalculateStakes] = useState(true);
  const [selectedBets, setSelectedBets] = useState<Set<string>>(new Set());

  const onRefresh = () => {
    actions.loadBettingData();
  };

  const filteredRecommendations = bettingRecommendations.filter(bet => {
    if (showValueBetsOnly && bet.valueRating < 0.7) return false;
    if (selectedBetType !== 'all' && bet.type !== selectedBetType) return false;
    if (selectedConfidence !== 'all' && bet.confidence !== selectedConfidence) return false;
    return true;
  });

  const toggleBetSelection = (betId: string) => {
    const newSelection = new Set(selectedBets);
    if (newSelection.has(betId)) {
      newSelection.delete(betId);
    } else {
      newSelection.add(betId);
    }
    setSelectedBets(newSelection);
  };

  const calculateOptimalStake = (bet: BettingRecommendation): number => {
    if (!autoCalculateStakes) return parseFloat(defaultStake) || 10;
    
    // Kelly Criterion for optimal stake sizing
    const p = bet.modelProbability;
    const b = bet.odds - 1;
    const q = 1 - p;
    
    const kellyFraction = (b * p - q) / b;
    const bankroll = 1000; // Assume $1000 bankroll
    
    return Math.max(5, Math.min(50, kellyFraction * bankroll));
  };

  const renderFilters = () => {
    return (
      <Card style={styles.filtersCard} elevation={1}>
        <Card.Content>
          <Title style={styles.filtersTitle}>Filters</Title>
          
          <View style={styles.filterRow}>
            <Text style={styles.filterLabel}>Bet Type:</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              <View style={styles.chipContainer}>
                {(['all', 'win', 'podium', 'top10', 'head_to_head'] as BetType[]).map(type => (
                  <Chip
                    key={type}
                    mode={selectedBetType === type ? 'flat' : 'outlined'}
                    selected={selectedBetType === type}
                    onPress={() => setSelectedBetType(type)}
                    style={styles.filterChip}
                  >
                    {type.replace('_', ' ').toUpperCase()}
                  </Chip>
                ))}
              </View>
            </ScrollView>
          </View>
          
          <View style={styles.filterRow}>
            <Text style={styles.filterLabel}>Confidence:</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              <View style={styles.chipContainer}>
                {(['all', 'high', 'medium', 'low'] as ConfidenceLevel[]).map(level => (
                  <Chip
                    key={level}
                    mode={selectedConfidence === level ? 'flat' : 'outlined'}
                    selected={selectedConfidence === level}
                    onPress={() => setSelectedConfidence(level)}
                    style={styles.filterChip}
                  >
                    {level.toUpperCase()}
                  </Chip>
                ))}
              </View>
            </ScrollView>
          </View>
          
          <View style={styles.switchRow}>
            <Text style={styles.switchLabel}>Show Value Bets Only</Text>
            <Switch
              value={showValueBetsOnly}
              onValueChange={setShowValueBetsOnly}
              color={theme.colors.primary}
            />
          </View>
        </Card.Content>
      </Card>
    );
  };

  const renderBettingSettings = () => {
    return (
      <Card style={styles.settingsCard} elevation={1}>
        <Card.Content>
          <Title style={styles.settingsTitle}>Betting Settings</Title>
          
          <View style={styles.settingRow}>
            <Text style={styles.settingLabel}>Default Stake ($)</Text>
            <TextInput
              value={defaultStake}
              onChangeText={setDefaultStake}
              keyboardType="numeric"
              style={styles.stakeInput}
              mode="outlined"
              dense
            />
          </View>
          
          <View style={styles.switchRow}>
            <Text style={styles.switchLabel}>Auto-Calculate Stakes (Kelly Criterion)</Text>
            <Switch
              value={autoCalculateStakes}
              onValueChange={setAutoCalculateStakes}
              color={theme.colors.primary}
            />
          </View>
        </Card.Content>
      </Card>
    );
  };

  const renderBettingRecommendation = (bet: BettingRecommendation) => {
    const isSelected = selectedBets.has(bet.id);
    const optimalStake = calculateOptimalStake(bet);
    const potentialReturn = optimalStake * bet.odds;
    const potentialProfit = potentialReturn - optimalStake;
    
    const getConfidenceColor = (confidence: string) => {
      switch (confidence) {
        case 'high': return theme.colors.success;
        case 'medium': return theme.colors.warning;
        case 'low': return theme.colors.error;
        default: return theme.colors.outline;
      }
    };

    return (
      <Card 
        key={bet.id} 
        style={[
          styles.betCard,
          isSelected && styles.selectedBetCard
        ]} 
        elevation={isSelected ? 4 : 2}
        onPress={() => toggleBetSelection(bet.id)}
      >
        <Card.Content>
          <View style={styles.betHeader}>
            <View style={styles.betInfo}>
              <Text style={styles.betDriver}>{bet.driver}</Text>
              <Text style={styles.betDescription}>{bet.description}</Text>
            </View>
            
            <View style={styles.betBadges}>
              <Chip 
                mode="flat"
                style={[
                  styles.confidenceChip,
                  { backgroundColor: getConfidenceColor(bet.confidence) }
                ]}
                textStyle={{ color: theme.colors.onPrimary }}
              >
                {bet.confidence.toUpperCase()}
              </Chip>
              
              {bet.valueRating > 0.7 && (
                <Chip 
                  mode="flat"
                  style={[
                    styles.valueChip,
                    { backgroundColor: theme.colors.tertiary }
                  ]}
                  textStyle={{ color: theme.colors.onTertiary }}
                >
                  VALUE
                </Chip>
              )}
            </View>
          </View>
          
          <Divider style={styles.betDivider} />
          
          <View style={styles.betStats}>
            <View style={styles.betStat}>
              <Text style={styles.betStatLabel}>Odds</Text>
              <Text style={styles.betStatValue}>{bet.odds.toFixed(2)}</Text>
            </View>
            
            <View style={styles.betStat}>
              <Text style={styles.betStatLabel}>Implied Prob.</Text>
              <Text style={styles.betStatValue}>{(bet.impliedProbability * 100).toFixed(1)}%</Text>
            </View>
            
            <View style={styles.betStat}>
              <Text style={styles.betStatLabel}>Model Prob.</Text>
              <Text style={styles.betStatValue}>{(bet.modelProbability * 100).toFixed(1)}%</Text>
            </View>
            
            <View style={styles.betStat}>
              <Text style={styles.betStatLabel}>Value Rating</Text>
              <Text style={[
                styles.betStatValue,
                { color: bet.valueRating > 0.7 ? theme.colors.success : theme.colors.onSurface }
              ]}>
                {(bet.valueRating * 100).toFixed(0)}%
              </Text>
            </View>
          </View>
          
          {isSelected && (
            <View style={styles.betCalculation}>
              <Divider style={styles.betDivider} />
              <Text style={styles.calculationTitle}>Stake Calculation</Text>
              
              <View style={styles.calculationRow}>
                <Text style={styles.calculationLabel}>Recommended Stake:</Text>
                <Text style={styles.calculationValue}>${optimalStake.toFixed(2)}</Text>
              </View>
              
              <View style={styles.calculationRow}>
                <Text style={styles.calculationLabel}>Potential Return:</Text>
                <Text style={styles.calculationValue}>${potentialReturn.toFixed(2)}</Text>
              </View>
              
              <View style={styles.calculationRow}>
                <Text style={styles.calculationLabel}>Potential Profit:</Text>
                <Text style={[
                  styles.calculationValue,
                  { color: theme.colors.success }
                ]}>
                  +${potentialProfit.toFixed(2)}
                </Text>
              </View>
              
              <View style={styles.calculationRow}>
                <Text style={styles.calculationLabel}>Expected Value:</Text>
                <Text style={[
                  styles.calculationValue,
                  { color: bet.expectedValue > 0 ? theme.colors.success : theme.colors.error }
                ]}>
                  {bet.expectedValue > 0 ? '+' : ''}{(bet.expectedValue * 100).toFixed(1)}%
                </Text>
              </View>
            </View>
          )}
        </Card.Content>
      </Card>
    );
  };

  const renderBestOdds = () => {
    if (bestOdds.length === 0) return null;

    return (
      <Card style={styles.oddsCard} elevation={2}>
        <Card.Content>
          <Title style={styles.oddsTitle}>Best Available Odds</Title>
          
          <DataTable>
            <DataTable.Header>
              <DataTable.Title>Driver</DataTable.Title>
              <DataTable.Title numeric>Win</DataTable.Title>
              <DataTable.Title numeric>Podium</DataTable.Title>
              <DataTable.Title>Bookmaker</DataTable.Title>
            </DataTable.Header>
            
            {bestOdds.slice(0, 10).map((odds, index) => (
              <DataTable.Row key={index}>
                <DataTable.Cell>{odds.driver}</DataTable.Cell>
                <DataTable.Cell numeric>{odds.winOdds.toFixed(2)}</DataTable.Cell>
                <DataTable.Cell numeric>
                  {odds.podiumOdds ? odds.podiumOdds.toFixed(2) : '-'}
                </DataTable.Cell>
                <DataTable.Cell>{odds.bookmaker}</DataTable.Cell>
              </DataTable.Row>
            ))}
          </DataTable>
        </Card.Content>
      </Card>
    );
  };

  const renderSelectedBetsSummary = () => {
    if (selectedBets.size === 0) return null;

    const selectedRecommendations = filteredRecommendations.filter(bet => 
      selectedBets.has(bet.id)
    );
    
    const totalStake = selectedRecommendations.reduce((sum, bet) => 
      sum + calculateOptimalStake(bet), 0
    );
    
    const totalPotentialReturn = selectedRecommendations.reduce((sum, bet) => 
      sum + (calculateOptimalStake(bet) * bet.odds), 0
    );
    
    const totalPotentialProfit = totalPotentialReturn - totalStake;

    return (
      <Card style={styles.summaryCard} elevation={3}>
        <Card.Content>
          <Title style={styles.summaryTitle}>Selected Bets Summary</Title>
          
          <View style={styles.summaryStats}>
            <View style={styles.summaryStat}>
              <Text style={styles.summaryStatValue}>{selectedBets.size}</Text>
              <Text style={styles.summaryStatLabel}>Bets Selected</Text>
            </View>
            
            <View style={styles.summaryStat}>
              <Text style={styles.summaryStatValue}>${totalStake.toFixed(2)}</Text>
              <Text style={styles.summaryStatLabel}>Total Stake</Text>
            </View>
            
            <View style={styles.summaryStat}>
              <Text style={[styles.summaryStatValue, { color: theme.colors.success }]}>
                +${totalPotentialProfit.toFixed(2)}
              </Text>
              <Text style={styles.summaryStatLabel}>Potential Profit</Text>
            </View>
          </View>
          
          <View style={styles.summaryActions}>
            <Button 
              mode="outlined" 
              onPress={() => setSelectedBets(new Set())}
              style={styles.summaryButton}
            >
              Clear All
            </Button>
            
            <Button 
              mode="contained" 
              onPress={() => {
                Alert.alert(
                  'Export Bets',
                  'This feature would export your selected bets to your preferred betting platform.',
                  [{ text: 'OK' }]
                );
              }}
              style={styles.summaryButton}
            >
              Export Bets
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
        <Text style={styles.errorText}>Failed to load betting data</Text>
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
      {renderFilters()}
      {renderBettingSettings()}
      {renderSelectedBetsSummary()}
      
      <View style={styles.recommendationsContainer}>
        <Title style={styles.recommendationsTitle}>
          Betting Recommendations ({filteredRecommendations.length})
        </Title>
        
        {filteredRecommendations.length === 0 ? (
          <Card style={styles.emptyCard} elevation={1}>
            <Card.Content>
              <Text style={styles.emptyText}>
                No betting recommendations match your current filters.
              </Text>
            </Card.Content>
          </Card>
        ) : (
          filteredRecommendations.map(bet => renderBettingRecommendation(bet))
        )}
      </View>
      
      {renderBestOdds()}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  filtersCard: {
    margin: 16,
    marginBottom: 8,
    borderRadius: 12,
  },
  filtersTitle: {
    fontSize: 16,
    marginBottom: 12,
  },
  filterRow: {
    marginBottom: 12,
  },
  filterLabel: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 8,
    color: theme.colors.onSurface,
  },
  chipContainer: {
    flexDirection: 'row',
  },
  filterChip: {
    marginRight: 8,
  },
  switchRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 8,
  },
  switchLabel: {
    fontSize: 14,
    color: theme.colors.onSurface,
  },
  settingsCard: {
    margin: 16,
    marginTop: 8,
    borderRadius: 12,
  },
  settingsTitle: {
    fontSize: 16,
    marginBottom: 12,
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  settingLabel: {
    fontSize: 14,
    color: theme.colors.onSurface,
    flex: 1,
  },
  stakeInput: {
    width: 100,
  },
  summaryCard: {
    margin: 16,
    marginTop: 8,
    borderRadius: 12,
    backgroundColor: theme.colors.primaryContainer,
  },
  summaryTitle: {
    fontSize: 16,
    marginBottom: 16,
    color: theme.colors.onPrimaryContainer,
  },
  summaryStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 16,
  },
  summaryStat: {
    alignItems: 'center',
  },
  summaryStatValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.colors.onPrimaryContainer,
  },
  summaryStatLabel: {
    fontSize: 12,
    color: theme.colors.onPrimaryContainer,
    marginTop: 4,
  },
  summaryActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  summaryButton: {
    flex: 1,
    marginHorizontal: 4,
  },
  recommendationsContainer: {
    paddingHorizontal: 16,
  },
  recommendationsTitle: {
    fontSize: 18,
    marginBottom: 12,
    color: theme.colors.onSurface,
  },
  betCard: {
    marginBottom: 12,
    borderRadius: 12,
  },
  selectedBetCard: {
    borderWidth: 2,
    borderColor: theme.colors.primary,
  },
  betHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  betInfo: {
    flex: 1,
  },
  betDriver: {
    fontSize: 18,
    fontWeight: '600',
    color: theme.colors.onSurface,
    marginBottom: 4,
  },
  betDescription: {
    fontSize: 14,
    color: theme.colors.onSurfaceVariant,
  },
  betBadges: {
    alignItems: 'flex-end',
  },
  confidenceChip: {
    marginBottom: 4,
    height: 24,
  },
  valueChip: {
    height: 24,
  },
  betDivider: {
    marginVertical: 12,
  },
  betStats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  betStat: {
    alignItems: 'center',
    flex: 1,
  },
  betStatLabel: {
    fontSize: 12,
    color: theme.colors.onSurfaceVariant,
    marginBottom: 4,
  },
  betStatValue: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.onSurface,
  },
  betCalculation: {
    marginTop: 8,
  },
  calculationTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.onSurface,
    marginBottom: 8,
  },
  calculationRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  calculationLabel: {
    fontSize: 12,
    color: theme.colors.onSurfaceVariant,
  },
  calculationValue: {
    fontSize: 12,
    fontWeight: '600',
    color: theme.colors.onSurface,
  },
  oddsCard: {
    margin: 16,
    borderRadius: 12,
  },
  oddsTitle: {
    fontSize: 16,
    marginBottom: 12,
  },
  emptyCard: {
    marginBottom: 16,
    borderRadius: 12,
  },
  emptyText: {
    textAlign: 'center',
    color: theme.colors.onSurfaceVariant,
    fontSize: 14,
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

export default BettingScreen;