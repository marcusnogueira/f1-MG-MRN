import React, { useState } from 'react';
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
  SegmentedButtons,
  ProgressBar,
} from 'react-native-paper';
import { LineChart, BarChart, PieChart } from 'react-native-chart-kit';
import { Ionicons } from '@expo/vector-icons';
import { useF1Data } from '../context/F1DataContext';
import { theme } from '../theme/theme';
import { ModelPerformance, FeatureImportance } from '../types/F1Types';

type AnalyticsTab = 'performance' | 'features' | 'track' | 'trends';

const { width: screenWidth } = Dimensions.get('window');
const chartWidth = screenWidth - 32;

const AnalyticsScreen: React.FC = () => {
  const { state, actions } = useF1Data();
  const {
    modelPerformance,
    featureImportance,
    trackCharacteristics,
    loading,
    error,
  } = state;

  const [selectedTab, setSelectedTab] = useState<AnalyticsTab>('performance');
  const [selectedMetric, setSelectedMetric] = useState<string>('accuracy');
  const [timeRange, setTimeRange] = useState<string>('season');

  const onRefresh = () => {
    actions.loadAnalytics();
  };

  const chartConfig = {
    backgroundColor: theme.colors.surface,
    backgroundGradientFrom: theme.colors.surface,
    backgroundGradientTo: theme.colors.surface,
    decimalPlaces: 2,
    color: (opacity = 1) => `rgba(${theme.colors.primary}, ${opacity})`,
    labelColor: (opacity = 1) => theme.colors.onSurface,
    style: {
      borderRadius: 16,
    },
    propsForDots: {
      r: '6',
      strokeWidth: '2',
      stroke: theme.colors.primary,
    },
  };

  const renderTabButtons = () => {
    const buttons = [
      { value: 'performance', label: 'Performance' },
      { value: 'features', label: 'Features' },
      { value: 'track', label: 'Track' },
      { value: 'trends', label: 'Trends' },
    ];

    return (
      <Card style={styles.tabCard} elevation={1}>
        <Card.Content>
          <SegmentedButtons
            value={selectedTab}
            onValueChange={(value) => setSelectedTab(value as AnalyticsTab)}
            buttons={buttons}
            style={styles.segmentedButtons}
          />
        </Card.Content>
      </Card>
    );
  };

  const renderModelPerformance = () => {
    if (!modelPerformance) return null;

    const performanceData = {
      labels: ['Accuracy', 'Precision', 'Recall', 'F1-Score'],
      datasets: [
        {
          data: [
            modelPerformance.accuracy,
            modelPerformance.precision,
            modelPerformance.recall,
            modelPerformance.f1Score,
          ],
        },
      ],
    };

    const historicalData = {
      labels: ['Race 1', 'Race 2', 'Race 3', 'Race 4', 'Race 5', 'Race 6'],
      datasets: [
        {
          data: [0.72, 0.75, 0.78, 0.76, 0.81, 0.83],
          color: (opacity = 1) => `rgba(${theme.colors.primary}, ${opacity})`,
          strokeWidth: 2,
        },
      ],
    };

    return (
      <View>
        <Card style={styles.performanceCard} elevation={2}>
          <Card.Content>
            <Title style={styles.cardTitle}>Current Model Performance</Title>
            
            <View style={styles.metricsGrid}>
              <View style={styles.metricItem}>
                <Text style={styles.metricValue}>
                  {(modelPerformance.accuracy * 100).toFixed(1)}%
                </Text>
                <Text style={styles.metricLabel}>Accuracy</Text>
                <ProgressBar 
                  progress={modelPerformance.accuracy} 
                  color={theme.colors.primary}
                  style={styles.progressBar}
                />
              </View>
              
              <View style={styles.metricItem}>
                <Text style={styles.metricValue}>
                  {(modelPerformance.precision * 100).toFixed(1)}%
                </Text>
                <Text style={styles.metricLabel}>Precision</Text>
                <ProgressBar 
                  progress={modelPerformance.precision} 
                  color={theme.colors.secondary}
                  style={styles.progressBar}
                />
              </View>
              
              <View style={styles.metricItem}>
                <Text style={styles.metricValue}>
                  {(modelPerformance.recall * 100).toFixed(1)}%
                </Text>
                <Text style={styles.metricLabel}>Recall</Text>
                <ProgressBar 
                  progress={modelPerformance.recall} 
                  color={theme.colors.tertiary}
                  style={styles.progressBar}
                />
              </View>
              
              <View style={styles.metricItem}>
                <Text style={styles.metricValue}>
                  {(modelPerformance.f1Score * 100).toFixed(1)}%
                </Text>
                <Text style={styles.metricLabel}>F1-Score</Text>
                <ProgressBar 
                  progress={modelPerformance.f1Score} 
                  color={theme.colors.success}
                  style={styles.progressBar}
                />
              </View>
            </View>
            
            <View style={styles.additionalMetrics}>
              <View style={styles.additionalMetric}>
                <Text style={styles.additionalMetricLabel}>Training Samples</Text>
                <Text style={styles.additionalMetricValue}>
                  {modelPerformance.trainingSamples.toLocaleString()}
                </Text>
              </View>
              
              <View style={styles.additionalMetric}>
                <Text style={styles.additionalMetricLabel}>Last Updated</Text>
                <Text style={styles.additionalMetricValue}>
                  {new Date(modelPerformance.lastUpdated).toLocaleDateString()}
                </Text>
              </View>
            </View>
          </Card.Content>
        </Card>

        <Card style={styles.chartCard} elevation={2}>
          <Card.Content>
            <Title style={styles.cardTitle}>Performance Comparison</Title>
            <BarChart
              data={performanceData}
              width={chartWidth - 32}
              height={220}
              chartConfig={chartConfig}
              style={styles.chart}
              showValuesOnTopOfBars
            />
          </Card.Content>
        </Card>

        <Card style={styles.chartCard} elevation={2}>
          <Card.Content>
            <Title style={styles.cardTitle}>Historical Accuracy Trend</Title>
            <LineChart
              data={historicalData}
              width={chartWidth - 32}
              height={220}
              chartConfig={chartConfig}
              style={styles.chart}
              bezier
            />
          </Card.Content>
        </Card>
      </View>
    );
  };

  const renderFeatureImportance = () => {
    if (!featureImportance || featureImportance.length === 0) return null;

    const chartData = {
      labels: featureImportance.slice(0, 6).map(f => f.feature.replace('_', ' ')),
      datasets: [
        {
          data: featureImportance.slice(0, 6).map(f => f.importance),
        },
      ],
    };

    const pieData = featureImportance.slice(0, 5).map((feature, index) => ({
      name: feature.feature.replace('_', ' '),
      importance: feature.importance,
      color: [
        theme.colors.primary,
        theme.colors.secondary,
        theme.colors.tertiary,
        theme.colors.success,
        theme.colors.warning,
      ][index],
      legendFontColor: theme.colors.onSurface,
      legendFontSize: 12,
    }));

    return (
      <View>
        <Card style={styles.featuresCard} elevation={2}>
          <Card.Content>
            <Title style={styles.cardTitle}>Feature Importance Rankings</Title>
            
            {featureImportance.map((feature, index) => (
              <View key={feature.feature} style={styles.featureItem}>
                <View style={styles.featureHeader}>
                  <Text style={styles.featureRank}>#{index + 1}</Text>
                  <Text style={styles.featureName}>
                    {feature.feature.replace('_', ' ').toUpperCase()}
                  </Text>
                  <Text style={styles.featureImportance}>
                    {(feature.importance * 100).toFixed(1)}%
                  </Text>
                </View>
                
                <ProgressBar 
                  progress={feature.importance} 
                  color={index < 3 ? theme.colors.primary : theme.colors.outline}
                  style={styles.featureProgressBar}
                />
                
                {feature.description && (
                  <Text style={styles.featureDescription}>
                    {feature.description}
                  </Text>
                )}
              </View>
            ))}
          </Card.Content>
        </Card>

        <Card style={styles.chartCard} elevation={2}>
          <Card.Content>
            <Title style={styles.cardTitle}>Top Features Distribution</Title>
            <PieChart
              data={pieData}
              width={chartWidth - 32}
              height={220}
              chartConfig={chartConfig}
              accessor="importance"
              backgroundColor="transparent"
              paddingLeft="15"
              style={styles.chart}
            />
          </Card.Content>
        </Card>

        <Card style={styles.chartCard} elevation={2}>
          <Card.Content>
            <Title style={styles.cardTitle}>Feature Importance Comparison</Title>
            <BarChart
              data={chartData}
              width={chartWidth - 32}
              height={220}
              chartConfig={chartConfig}
              style={styles.chart}
              showValuesOnTopOfBars
              fromZero
            />
          </Card.Content>
        </Card>
      </View>
    );
  };

  const renderTrackCharacteristics = () => {
    if (!trackCharacteristics) return null;

    const trackData = {
      labels: ['Speed', 'Overtaking', 'Tire Deg.', 'Weather', 'Elevation'],
      datasets: [
        {
          data: [
            trackCharacteristics.speedImportance,
            trackCharacteristics.overtakingDifficulty,
            trackCharacteristics.tireDegradation,
            trackCharacteristics.weatherImpact,
            trackCharacteristics.elevationChange,
          ],
        },
      ],
    };

    return (
      <View>
        <Card style={styles.trackCard} elevation={2}>
          <Card.Content>
            <Title style={styles.cardTitle}>Current Track: {trackCharacteristics.trackName}</Title>
            
            <View style={styles.trackInfo}>
              <View style={styles.trackInfoItem}>
                <Ionicons name="speedometer" size={24} color={theme.colors.primary} />
                <Text style={styles.trackInfoLabel}>Track Length</Text>
                <Text style={styles.trackInfoValue}>{trackCharacteristics.length} km</Text>
              </View>
              
              <View style={styles.trackInfoItem}>
                <Ionicons name="flag" size={24} color={theme.colors.secondary} />
                <Text style={styles.trackInfoLabel}>Lap Record</Text>
                <Text style={styles.trackInfoValue}>{trackCharacteristics.lapRecord}</Text>
              </View>
              
              <View style={styles.trackInfoItem}>
                <Ionicons name="car-sport" size={24} color={theme.colors.tertiary} />
                <Text style={styles.trackInfoLabel}>DRS Zones</Text>
                <Text style={styles.trackInfoValue}>{trackCharacteristics.drsZones}</Text>
              </View>
            </View>
            
            <View style={styles.trackCharacteristics}>
              <View style={styles.characteristic}>
                <Text style={styles.characteristicLabel}>Speed Importance</Text>
                <ProgressBar 
                  progress={trackCharacteristics.speedImportance} 
                  color={theme.colors.primary}
                  style={styles.characteristicBar}
                />
                <Text style={styles.characteristicValue}>
                  {(trackCharacteristics.speedImportance * 100).toFixed(0)}%
                </Text>
              </View>
              
              <View style={styles.characteristic}>
                <Text style={styles.characteristicLabel}>Overtaking Difficulty</Text>
                <ProgressBar 
                  progress={trackCharacteristics.overtakingDifficulty} 
                  color={theme.colors.warning}
                  style={styles.characteristicBar}
                />
                <Text style={styles.characteristicValue}>
                  {(trackCharacteristics.overtakingDifficulty * 100).toFixed(0)}%
                </Text>
              </View>
              
              <View style={styles.characteristic}>
                <Text style={styles.characteristicLabel}>Tire Degradation</Text>
                <ProgressBar 
                  progress={trackCharacteristics.tireDegradation} 
                  color={theme.colors.error}
                  style={styles.characteristicBar}
                />
                <Text style={styles.characteristicValue}>
                  {(trackCharacteristics.tireDegradation * 100).toFixed(0)}%
                </Text>
              </View>
              
              <View style={styles.characteristic}>
                <Text style={styles.characteristicLabel}>Weather Impact</Text>
                <ProgressBar 
                  progress={trackCharacteristics.weatherImpact} 
                  color={theme.colors.tertiary}
                  style={styles.characteristicBar}
                />
                <Text style={styles.characteristicValue}>
                  {(trackCharacteristics.weatherImpact * 100).toFixed(0)}%
                </Text>
              </View>
            </View>
          </Card.Content>
        </Card>

        <Card style={styles.chartCard} elevation={2}>
          <Card.Content>
            <Title style={styles.cardTitle}>Track Characteristics Radar</Title>
            <BarChart
              data={trackData}
              width={chartWidth - 32}
              height={220}
              chartConfig={chartConfig}
              style={styles.chart}
              showValuesOnTopOfBars
            />
          </Card.Content>
        </Card>
      </View>
    );
  };

  const renderTrends = () => {
    const trendData = {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      datasets: [
        {
          data: [0.72, 0.75, 0.78, 0.76, 0.81, 0.83],
          color: (opacity = 1) => theme.colors.primary,
          strokeWidth: 2,
        },
        {
          data: [0.68, 0.71, 0.74, 0.73, 0.77, 0.79],
          color: (opacity = 1) => theme.colors.secondary,
          strokeWidth: 2,
        },
      ],
    };

    return (
      <View>
        <Card style={styles.trendsCard} elevation={2}>
          <Card.Content>
            <Title style={styles.cardTitle}>Model Performance Trends</Title>
            
            <View style={styles.trendFilters}>
              <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                <View style={styles.chipContainer}>
                  {['week', 'month', 'season', 'year'].map(range => (
                    <Chip
                      key={range}
                      mode={timeRange === range ? 'flat' : 'outlined'}
                      selected={timeRange === range}
                      onPress={() => setTimeRange(range)}
                      style={styles.trendChip}
                    >
                      {range.toUpperCase()}
                    </Chip>
                  ))}
                </View>
              </ScrollView>
            </View>
            
            <LineChart
              data={trendData}
              width={chartWidth - 32}
              height={220}
              chartConfig={chartConfig}
              style={styles.chart}
              bezier
            />
            
            <View style={styles.trendLegend}>
              <View style={styles.legendItem}>
                <View style={[styles.legendColor, { backgroundColor: theme.colors.primary }]} />
                <Text style={styles.legendText}>Accuracy</Text>
              </View>
              <View style={styles.legendItem}>
                <View style={[styles.legendColor, { backgroundColor: theme.colors.secondary }]} />
                <Text style={styles.legendText}>Precision</Text>
              </View>
            </View>
          </Card.Content>
        </Card>

        <Card style={styles.insightsCard} elevation={2}>
          <Card.Content>
            <Title style={styles.cardTitle}>Key Insights</Title>
            
            <View style={styles.insight}>
              <Ionicons name="trending-up" size={20} color={theme.colors.success} />
              <Text style={styles.insightText}>
                Model accuracy has improved by 15% over the last 6 races
              </Text>
            </View>
            
            <View style={styles.insight}>
              <Ionicons name="analytics" size={20} color={theme.colors.primary} />
              <Text style={styles.insightText}>
                Track affinity is the most predictive feature this season
              </Text>
            </View>
            
            <View style={styles.insight}>
              <Ionicons name="warning" size={20} color={theme.colors.warning} />
              <Text style={styles.insightText}>
                Weather conditions significantly impact prediction accuracy
              </Text>
            </View>
          </Card.Content>
        </Card>
      </View>
    );
  };

  const renderContent = () => {
    switch (selectedTab) {
      case 'performance':
        return renderModelPerformance();
      case 'features':
        return renderFeatureImportance();
      case 'track':
        return renderTrackCharacteristics();
      case 'trends':
        return renderTrends();
      default:
        return null;
    }
  };

  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Ionicons name="warning" size={48} color={theme.colors.error} />
        <Text style={styles.errorText}>Failed to load analytics data</Text>
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
      {renderTabButtons()}
      {renderContent()}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  tabCard: {
    margin: 16,
    marginBottom: 8,
    borderRadius: 12,
  },
  segmentedButtons: {
    backgroundColor: theme.colors.surface,
  },
  performanceCard: {
    margin: 16,
    marginTop: 8,
    borderRadius: 12,
  },
  cardTitle: {
    fontSize: 18,
    marginBottom: 16,
    color: theme.colors.onSurface,
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  metricItem: {
    width: '48%',
    marginBottom: 16,
  },
  metricValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.primary,
    marginBottom: 4,
  },
  metricLabel: {
    fontSize: 12,
    color: theme.colors.onSurfaceVariant,
    marginBottom: 8,
  },
  progressBar: {
    height: 6,
    borderRadius: 3,
  },
  additionalMetrics: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: theme.colors.outline,
  },
  additionalMetric: {
    alignItems: 'center',
  },
  additionalMetricLabel: {
    fontSize: 12,
    color: theme.colors.onSurfaceVariant,
    marginBottom: 4,
  },
  additionalMetricValue: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.onSurface,
  },
  chartCard: {
    margin: 16,
    marginTop: 8,
    borderRadius: 12,
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  featuresCard: {
    margin: 16,
    marginTop: 8,
    borderRadius: 12,
  },
  featureItem: {
    marginBottom: 16,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.outline,
  },
  featureHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  featureRank: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.primary,
    width: 30,
  },
  featureName: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.onSurface,
    flex: 1,
    marginLeft: 8,
  },
  featureImportance: {
    fontSize: 14,
    fontWeight: 'bold',
    color: theme.colors.primary,
  },
  featureProgressBar: {
    height: 4,
    borderRadius: 2,
    marginBottom: 4,
  },
  featureDescription: {
    fontSize: 12,
    color: theme.colors.onSurfaceVariant,
    fontStyle: 'italic',
  },
  trackCard: {
    margin: 16,
    marginTop: 8,
    borderRadius: 12,
  },
  trackInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  trackInfoItem: {
    alignItems: 'center',
    flex: 1,
  },
  trackInfoLabel: {
    fontSize: 12,
    color: theme.colors.onSurfaceVariant,
    marginTop: 4,
    marginBottom: 2,
  },
  trackInfoValue: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.onSurface,
  },
  trackCharacteristics: {
    marginTop: 16,
  },
  characteristic: {
    marginBottom: 16,
  },
  characteristicLabel: {
    fontSize: 14,
    color: theme.colors.onSurface,
    marginBottom: 8,
  },
  characteristicBar: {
    height: 6,
    borderRadius: 3,
    marginBottom: 4,
  },
  characteristicValue: {
    fontSize: 12,
    color: theme.colors.onSurfaceVariant,
    textAlign: 'right',
  },
  trendsCard: {
    margin: 16,
    marginTop: 8,
    borderRadius: 12,
  },
  trendFilters: {
    marginBottom: 16,
  },
  chipContainer: {
    flexDirection: 'row',
  },
  trendChip: {
    marginRight: 8,
  },
  trendLegend: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: 16,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginHorizontal: 16,
  },
  legendColor: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 8,
  },
  legendText: {
    fontSize: 12,
    color: theme.colors.onSurface,
  },
  insightsCard: {
    margin: 16,
    marginTop: 8,
    borderRadius: 12,
  },
  insight: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  insightText: {
    fontSize: 14,
    color: theme.colors.onSurface,
    marginLeft: 12,
    flex: 1,
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

export default AnalyticsScreen;