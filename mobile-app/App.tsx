import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Provider as PaperProvider } from 'react-native-paper';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';

// Screens
import DashboardScreen from './src/screens/DashboardScreen';
import PredictionsScreen from './src/screens/PredictionsScreen';
import BettingScreen from './src/screens/BettingScreen';
import AnalyticsScreen from './src/screens/AnalyticsScreen';
import SettingsScreen from './src/screens/SettingsScreen';

// Theme
import { theme } from './src/theme/theme';

// Context
import { F1DataProvider } from './src/context/F1DataContext';

const Tab = createBottomTabNavigator();

function TabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: keyof typeof Ionicons.glyphMap;

          if (route.name === 'Dashboard') {
            iconName = focused ? 'speedometer' : 'speedometer-outline';
          } else if (route.name === 'Predictions') {
            iconName = focused ? 'analytics' : 'analytics-outline';
          } else if (route.name === 'Betting') {
            iconName = focused ? 'cash' : 'cash-outline';
          } else if (route.name === 'Analytics') {
            iconName = focused ? 'bar-chart' : 'bar-chart-outline';
          } else if (route.name === 'Settings') {
            iconName = focused ? 'settings' : 'settings-outline';
          } else {
            iconName = 'help-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: theme.colors.primary,
        tabBarInactiveTintColor: theme.colors.onSurfaceVariant,
        tabBarStyle: {
          backgroundColor: theme.colors.surface,
          borderTopColor: theme.colors.outline,
          paddingBottom: 5,
          height: 60,
        },
        headerStyle: {
          backgroundColor: theme.colors.primary,
        },
        headerTintColor: theme.colors.onPrimary,
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      })}
    >
      <Tab.Screen 
        name="Dashboard" 
        component={DashboardScreen}
        options={{ title: '🏎️ F1 Predict Pro' }}
      />
      <Tab.Screen 
        name="Predictions" 
        component={PredictionsScreen}
        options={{ title: 'Race Predictions' }}
      />
      <Tab.Screen 
        name="Betting" 
        component={BettingScreen}
        options={{ title: 'Betting Analysis' }}
      />
      <Tab.Screen 
        name="Analytics" 
        component={AnalyticsScreen}
        options={{ title: 'Performance Analytics' }}
      />
      <Tab.Screen 
        name="Settings" 
        component={SettingsScreen}
        options={{ title: 'Settings' }}
      />
    </Tab.Navigator>
  );
}

export default function App() {
  return (
    <SafeAreaProvider>
      <PaperProvider theme={theme}>
        <F1DataProvider>
          <NavigationContainer>
            <StatusBar style="light" backgroundColor={theme.colors.primary} />
            <TabNavigator />
          </NavigationContainer>
        </F1DataProvider>
      </PaperProvider>
    </SafeAreaProvider>
  );
}