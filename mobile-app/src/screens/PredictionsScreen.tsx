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
import { LineChart, BarChart } from 'react-native-chart-kit';
import { Ionicons } from '@expo/vector-icons';
import { useF1Data } from '../context/F1DataContext';
import { theme, getTeamColor, getPositionColor } from '../theme/theme';
import { DriverPrediction } from '../types/F1Types';

const { width } = Dimensions.get('window');
const chartWidth = width - 32;

type ViewMode = 'grid' | 'list' | 'chart';

const PredictionsScreen: React.FC = () => {
  const { state, actions } = useF1Data();
  const {
    driverPredictions,
    positionProbabilities,
    nextRace,
    loading,
    error,
  } = state;

  const [viewMode, setViewMode] = useState<ViewMode>('list');
  const [selectedDriver, setSelectedDriver] = useState<string | null>(null);

  const onRefresh = () => {
    actions.loadPredictions();
  };

  const renderViewModeSelector = () => {
    return (
      <View style={styles.viewModeContainer}>
        <SegmentedButtons
          value={viewMode}
          onValueChange={(value) => setViewMode(value as ViewMode)}
          buttons={[
            {
              value: 'list',
              label: 'List',
              icon: 'list',
            },
            {
              value: 'grid',
              label: 'Grid',
              icon: 'grid',
            },
            {
              value: 'chart',
              label: 'Chart',
              icon: 'bar-chart',
            },
          ]}
        />
      </View>
    );
  };

  const renderDriverCard = (prediction: DriverPrediction, index: number) => {
    const isSelected = selectedDriver === prediction.driver.code;
    
    return (
      <Card 
        key={prediction.driver.code} 
        style={[
          styles.driverCard,
          isSelected && styles.selectedDriverCard
        ]} 
        elevation={isSelected ? 4 : 2}
        onPress={() => setSelectedDriver(isSelected ? null : prediction.driver.code)}
      >
        <Card.Content>
          <View style={styles.driverHeader}>
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
              <View style={styles.teamContainer}>
                <View 
                  style={[
                    styles.teamColorDot,
                    { backgroundColor: getTeamColor(prediction.driver.team) }
                  ]} 
                />
                <Text style={styles.teamName}>{prediction.driver.team}</Text>
              </View>
            </View>
            
            <View style={styles.confidenceContainer}>
              <Text style={styles.confidenceValue}>
                {Math.round(prediction.confidence * 100)}%
              </Text>
              <Text style={styles.confidenceLabel}>Confidence</Text>
            </View>
          </View>
          
          <View style={styles.progressContainer}>
            <Text style={styles.progressLabel}>Prediction Strength</Text>
            <ProgressBar 
              progress={prediction.confidence} 
              color={theme.colors.primary}
              style={styles.progressBar}
            />
          </View>
          
          {isSelected && renderDriverDetails(prediction)}
        </Card.Content>
      </Card>
    );
  };

  const renderDriverDetails = (prediction: DriverPrediction) => {
    return (
      <View style={styles.driverDetails}>
        <Title style={styles.detailsTitle}>Prediction Factors</Title>
        
        <View style={styles.factorsGrid}>
          <View style={styles.factorItem}>
            <Text style={styles.factorLabel}>Track Affinity</Text>
            <View style={styles.factorBar}>
              <ProgressBar 
                progress={prediction.features.trackAffinity} 
                color={theme.colors.secondary}
              />
              <Text style={styles.factorValue}>
                {Math.round(prediction.features.trackAffinity * 100)}%
              </Text>
            </View>
          </View>
          
          <View style={styles.factorItem}>
            <Text style={styles.factorLabel}>Team Strength</Text>
            <View style={styles.factorBar}>
              <ProgressBar 
                progress={prediction.features.teamStrength} 
                color={theme.colors.tertiary}
              />
              <Text style={styles.factorValue}>
                {Math.round(prediction.features.teamStrength * 100)}%
              </Text>
            </View>
          </View>
          
          <View style={styles.factorItem}>
            <Text style={styles.factorLabel}>Current Momentum</Text>
            <View style={styles.factorBar}>
              <ProgressBar 
                progress={prediction.features.momentum} 
                color={theme.colors.success}
              />
              <Text style={styles.factorValue}>
                {Math.round(prediction.features.momentum * 100)}%
              </Text>
            </View>
          </View>
        </View>
        
        {prediction.features.recentForm && (
          <View style={styles.recentForm}>
            <Text style={styles.factorLabel}>Recent Form (Last 5 Races)</Text>
            <View style={styles.formPositions}>
              {prediction.features.recentForm.map((position, index) => (
                <Surface 
                  key={index}
                  style={[
                    styles.formPosition,
                    { backgroundColor: getPositionColor(position) }
                  ]}
                >
                  <Text style={styles.formPositionText}>{position}</Text>
                </Surface>
              ))}
            </View>
          </View>
        )}
      </View>
    );
  };

  const renderGridView = () => {
    return (
      <View style={styles.gridContainer}>
        {driverPredictions.map((prediction, index) => (
          <View key={prediction.driver.code} style={styles.gridItem}>
            <Surface style={styles.gridCard} elevation={2}>
              <View style={styles.gridPosition}>
                <Text style={styles.gridPositionText}>{prediction.predictedPosition}</Text>
              </View>
              <Text style={styles.gridDriverCode}>{prediction.driver.code}</Text>
              <Text style={styles.gridConfidence}>
                {Math.round(prediction.confidence * 100)}%
              </Text>
              <View 
                style={[
                  styles.gridTeamBar,
                  { backgroundColor: getTeamColor(prediction.driver.team) }
                ]} 
              />
            </Surface>
          </View>
        ))}
      </View>
    );
  };

  const renderChartView = () => {
    if (driverPredictions.length === 0) return null;

    const chartData = {
      labels: driverPredictions.slice(0, 10).map(p => p.driver.code),
      datasets: [{
        data: driverPredictions.slice(0, 10).map(p => p.confidence * 100),
        color: (opacity = 1) => `rgba(225, 6, 0, ${opacity})`,
        strokeWidth: 2,
      }]
    };

    const chartConfig = {
      backgroundColor: theme.colors.surface,
      backgroundGradientFrom: theme.colors.surface,
      backgroundGradientTo: theme.colors.surface,
      decimalPlaces: 0,
      color: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
      labelColor: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
      style: {
        borderRadius: 16,
      },
      propsForDots: {
        r: "6",
        strokeWidth: "2",
        stroke: theme.colors.primary,
      },
    };

    return (
      <Card style={styles.chartCard} elevation={2}>
        <Card.Content>
          <Title style={styles.chartTitle}>Prediction Confidence</Title>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            <LineChart
              data={chartData}
              width={Math.max(chartWidth, driverPredictions.length * 40)}
              height={220}
              chartConfig={chartConfig}
              bezier
              style={styles.chart}
            />
          </ScrollView>
        </Card.Content>
      </Card>
    );
  };

  const renderProbabilityMatrix = () => {
    if (Object.keys(positionProbabilities).length === 0) return null;

    const drivers = Object.keys(positionProbabilities).slice(0, 8);
    const positions = [1, 2, 3, 4, 5];

    return (
      <Card style={styles.card} elevation={2}>
        <Card.Content>
          <Title style={styles.sectionTitle}>Position Probabilities</Title>
          <Paragraph style={styles.sectionSubtitle}>
            Probability of each driver finishing in top 5 positions
          </Paragraph>
          
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            <View style={styles.probabilityMatrix}>
              <View style={styles.matrixHeader}>
                <View style={styles.matrixCorner} />
                {positions.map(pos => (
                  <View key={pos} style={styles.matrixHeaderCell}>
                    <Text style={styles.matrixHeaderText}>P{pos}</Text>
                  </View>
                ))}
              </View>
              
              {drivers.map(driver => (
                <View key={driver} style={styles.matrixRow}>
                  <View style={styles.matrixDriverCell}>
                    <Text style={styles.matrixDriverText}>{driver}</Text>
                  </View>
                  {positions.map(pos => {
                    const probability = positionProbabilities[driver]?.[pos - 1] || 0;
                    return (
                      <View key={pos} style={styles.matrixCell}>
                        <Surface 
                          style={[
                            styles.probabilityCell,
                            { 
                              backgroundColor: `rgba(225, 6, 0, ${probability})`,
                              opacity: Math.max(0.1, probability)
                            }
                          ]}
                        >
                          <Text style={styles.probabilityText}>
                            {Math.round(probability * 100)}%
                          </Text>
                        </Surface>
                      </View>
                    );
                  })}
                </View>
              ))}
            </View>
          </ScrollView>
        </Card.Content>
      </Card>
    );
  };

  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Ionicons name="warning" size={48} color={theme.colors.error} />
        <Text style={styles.errorText}>Failed to load predictions</Text>
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
      {nextRace && (
        <Card style={styles.raceInfoCard} elevation={1}>
          <Card.Content>
            <Text style={styles.raceInfoText}>
              Predictions for {nextRace.raceName}
            </Text>
          </Card.Content>
        </Card>
      )}
      
      {renderViewModeSelector()}
      
      {viewMode === 'list' && (
        <View style={styles.listContainer}>
          {driverPredictions.map((prediction, index) => 
            renderDriverCard(prediction, index)
          )}
        </View>
      )}
      
      {viewMode === 'grid' && renderGridView()}
      
      {viewMode === 'chart' && renderChartView()}
      
      {renderProbabilityMatrix()}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  raceInfoCard: {
    margin: 16,
    marginBottom: 8,
  },
  raceInfoText: {
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
    color: theme.colors.primary,
  },
  viewModeContainer: {
    margin: 16,
    marginTop: 8,
  },
  listContainer: {
    paddingHorizontal: 16,
  },
  driverCard: {
    marginBottom: 12,
    borderRadius: 12,
  },
  selectedDriverCard: {
    borderWidth: 2,
    borderColor: theme.colors.primary,
  },
  driverHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  positionContainer: {
    width: 50,
  },
  positionBadge: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  positionText: {
    color: theme.colors.onPrimary,
    fontWeight: 'bold',
    fontSize: 16,
  },
  driverInfo: {
    flex: 1,
    marginLeft: 12,
  },
  driverName: {
    fontSize: 18,
    fontWeight: '600',
    color: theme.colors.onSurface,
    marginBottom: 4,
  },
  teamContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  teamColorDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 6,
  },
  teamName: {
    fontSize: 14,
    color: theme.colors.onSurfaceVariant,
  },
  confidenceContainer: {
    alignItems: 'center',
  },
  confidenceValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.colors.primary,
  },
  confidenceLabel: {
    fontSize: 12,
    color: theme.colors.onSurfaceVariant,
  },
  progressContainer: {
    marginBottom: 8,
  },
  progressLabel: {
    fontSize: 12,
    color: theme.colors.onSurfaceVariant,
    marginBottom: 4,
  },
  progressBar: {
    height: 6,
    borderRadius: 3,
  },
  driverDetails: {
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: theme.colors.outlineVariant,
  },
  detailsTitle: {
    fontSize: 16,
    marginBottom: 12,
  },
  factorsGrid: {
    marginBottom: 16,
  },
  factorItem: {
    marginBottom: 12,
  },
  factorLabel: {
    fontSize: 14,
    color: theme.colors.onSurfaceVariant,
    marginBottom: 4,
  },
  factorBar: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  factorValue: {
    fontSize: 12,
    color: theme.colors.onSurface,
    marginLeft: 8,
    minWidth: 35,
  },
  recentForm: {
    marginTop: 8,
  },
  formPositions: {
    flexDirection: 'row',
    marginTop: 8,
  },
  formPosition: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8,
  },
  formPositionText: {
    color: theme.colors.onPrimary,
    fontWeight: 'bold',
    fontSize: 12,
  },
  gridContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 8,
  },
  gridItem: {
    width: '25%',
    padding: 4,
  },
  gridCard: {
    padding: 8,
    borderRadius: 8,
    alignItems: 'center',
  },
  gridPosition: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: theme.colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 4,
  },
  gridPositionText: {
    color: theme.colors.onPrimary,
    fontWeight: 'bold',
    fontSize: 12,
  },
  gridDriverCode: {
    fontSize: 12,
    fontWeight: '600',
    marginBottom: 2,
  },
  gridConfidence: {
    fontSize: 10,
    color: theme.colors.onSurfaceVariant,
    marginBottom: 4,
  },
  gridTeamBar: {
    width: '100%',
    height: 3,
    borderRadius: 1.5,
  },
  chartCard: {
    margin: 16,
    borderRadius: 12,
  },
  chartTitle: {
    fontSize: 18,
    marginBottom: 8,
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  card: {
    margin: 16,
    borderRadius: 12,
  },
  sectionTitle: {
    fontSize: 18,
    marginBottom: 4,
  },
  sectionSubtitle: {
    fontSize: 14,
    color: theme.colors.onSurfaceVariant,
    marginBottom: 16,
  },
  probabilityMatrix: {
    minWidth: 400,
  },
  matrixHeader: {
    flexDirection: 'row',
    marginBottom: 4,
  },
  matrixCorner: {
    width: 60,
    height: 30,
  },
  matrixHeaderCell: {
    width: 60,
    height: 30,
    justifyContent: 'center',
    alignItems: 'center',
  },
  matrixHeaderText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: theme.colors.primary,
  },
  matrixRow: {
    flexDirection: 'row',
    marginBottom: 4,
  },
  matrixDriverCell: {
    width: 60,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  matrixDriverText: {
    fontSize: 12,
    fontWeight: '600',
  },
  matrixCell: {
    width: 60,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  probabilityCell: {
    width: 50,
    height: 30,
    borderRadius: 4,
    justifyContent: 'center',
    alignItems: 'center',
  },
  probabilityText: {
    fontSize: 10,
    fontWeight: 'bold',
    color: theme.colors.onPrimary,
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

export default PredictionsScreen;