import React, { useState, useEffect } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Alert,
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  Switch,
  Text,
  TextInput,
  List,
  Divider,
  RadioButton,
  Chip,
  Surface,
} from 'react-native-paper';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { theme } from '../theme/theme';
import { UserSettings } from '../types/F1Types';

const SettingsScreen: React.FC = () => {
  const [settings, setSettings] = useState<UserSettings>({
    notifications: {
      raceReminders: true,
      predictionUpdates: true,
      bettingAlerts: false,
      newsUpdates: false,
    },
    display: {
      theme: 'auto',
      currency: 'USD',
      timeFormat: '24h',
      language: 'en',
    },
    betting: {
      defaultStake: 10,
      maxStake: 100,
      autoCalculateStakes: true,
      showValueBetsOnly: false,
      riskTolerance: 'medium',
    },
    data: {
      autoRefresh: true,
      refreshInterval: 300,
      cacheEnabled: true,
      offlineMode: false,
    },
    privacy: {
      analytics: true,
      crashReporting: true,
      dataSharing: false,
    },
  });

  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const savedSettings = await AsyncStorage.getItem('userSettings');
      if (savedSettings) {
        setSettings(JSON.parse(savedSettings));
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  };

  const saveSettings = async (newSettings: UserSettings) => {
    try {
      setLoading(true);
      await AsyncStorage.setItem('userSettings', JSON.stringify(newSettings));
      setSettings(newSettings);
    } catch (error) {
      console.error('Failed to save settings:', error);
      Alert.alert('Error', 'Failed to save settings. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const updateNotificationSetting = (key: keyof UserSettings['notifications'], value: boolean) => {
    const newSettings = {
      ...settings,
      notifications: {
        ...settings.notifications,
        [key]: value,
      },
    };
    saveSettings(newSettings);
  };

  const updateDisplaySetting = (key: keyof UserSettings['display'], value: string) => {
    const newSettings = {
      ...settings,
      display: {
        ...settings.display,
        [key]: value,
      },
    };
    saveSettings(newSettings);
  };

  const updateBettingSetting = (key: keyof UserSettings['betting'], value: any) => {
    const newSettings = {
      ...settings,
      betting: {
        ...settings.betting,
        [key]: value,
      },
    };
    saveSettings(newSettings);
  };

  const updateDataSetting = (key: keyof UserSettings['data'], value: any) => {
    const newSettings = {
      ...settings,
      data: {
        ...settings.data,
        [key]: value,
      },
    };
    saveSettings(newSettings);
  };

  const updatePrivacySetting = (key: keyof UserSettings['privacy'], value: boolean) => {
    const newSettings = {
      ...settings,
      privacy: {
        ...settings.privacy,
        [key]: value,
      },
    };
    saveSettings(newSettings);
  };

  const resetSettings = () => {
    Alert.alert(
      'Reset Settings',
      'Are you sure you want to reset all settings to default values?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Reset',
          style: 'destructive',
          onPress: async () => {
            try {
              await AsyncStorage.removeItem('userSettings');
              await loadSettings();
              Alert.alert('Success', 'Settings have been reset to default values.');
            } catch (error) {
              Alert.alert('Error', 'Failed to reset settings.');
            }
          },
        },
      ]
    );
  };

  const clearCache = () => {
    Alert.alert(
      'Clear Cache',
      'This will clear all cached data and may affect offline functionality.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Clear',
          style: 'destructive',
          onPress: async () => {
            try {
              // Clear all cache except settings
              const keys = await AsyncStorage.getAllKeys();
              const cacheKeys = keys.filter(key => key !== 'userSettings');
              await AsyncStorage.multiRemove(cacheKeys);
              Alert.alert('Success', 'Cache has been cleared.');
            } catch (error) {
              Alert.alert('Error', 'Failed to clear cache.');
            }
          },
        },
      ]
    );
  };

  const renderNotificationSettings = () => {
    return (
      <Card style={styles.settingsCard} elevation={2}>
        <Card.Content>
          <Title style={styles.sectionTitle}>Notifications</Title>
          
          <View style={styles.settingItem}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Race Reminders</Text>
              <Text style={styles.settingDescription}>
                Get notified before races start
              </Text>
            </View>
            <Switch
              value={settings.notifications.raceReminders}
              onValueChange={(value) => updateNotificationSetting('raceReminders', value)}
              color={theme.colors.primary}
            />
          </View>
          
          <View style={styles.settingItem}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Prediction Updates</Text>
              <Text style={styles.settingDescription}>
                Notifications when new predictions are available
              </Text>
            </View>
            <Switch
              value={settings.notifications.predictionUpdates}
              onValueChange={(value) => updateNotificationSetting('predictionUpdates', value)}
              color={theme.colors.primary}
            />
          </View>
          
          <View style={styles.settingItem}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Betting Alerts</Text>
              <Text style={styles.settingDescription}>
                Alerts for high-value betting opportunities
              </Text>
            </View>
            <Switch
              value={settings.notifications.bettingAlerts}
              onValueChange={(value) => updateNotificationSetting('bettingAlerts', value)}
              color={theme.colors.primary}
            />
          </View>
          
          <View style={styles.settingItem}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>News Updates</Text>
              <Text style={styles.settingDescription}>
                F1 news and breaking updates
              </Text>
            </View>
            <Switch
              value={settings.notifications.newsUpdates}
              onValueChange={(value) => updateNotificationSetting('newsUpdates', value)}
              color={theme.colors.primary}
            />
          </View>
        </Card.Content>
      </Card>
    );
  };

  const renderDisplaySettings = () => {
    return (
      <Card style={styles.settingsCard} elevation={2}>
        <Card.Content>
          <Title style={styles.sectionTitle}>Display</Title>
          
          <View style={styles.settingItem}>
            <Text style={styles.settingLabel}>Theme</Text>
            <View style={styles.radioGroup}>
              {['light', 'dark', 'auto'].map((theme) => (
                <View key={theme} style={styles.radioItem}>
                  <RadioButton
                    value={theme}
                    status={settings.display.theme === theme ? 'checked' : 'unchecked'}
                    onPress={() => updateDisplaySetting('theme', theme)}
                    color={theme.colors?.primary}
                  />
                  <Text style={styles.radioLabel}>
                    {theme.charAt(0).toUpperCase() + theme.slice(1)}
                  </Text>
                </View>
              ))}
            </View>
          </View>
          
          <Divider style={styles.divider} />
          
          <View style={styles.settingItem}>
            <Text style={styles.settingLabel}>Currency</Text>
            <View style={styles.chipGroup}>
              {['USD', 'EUR', 'GBP', 'JPY'].map((currency) => (
                <Chip
                  key={currency}
                  mode={settings.display.currency === currency ? 'flat' : 'outlined'}
                  selected={settings.display.currency === currency}
                  onPress={() => updateDisplaySetting('currency', currency)}
                  style={styles.chip}
                >
                  {currency}
                </Chip>
              ))}
            </View>
          </View>
          
          <Divider style={styles.divider} />
          
          <View style={styles.settingItem}>
            <Text style={styles.settingLabel}>Time Format</Text>
            <View style={styles.radioGroup}>
              {[{ value: '12h', label: '12 Hour' }, { value: '24h', label: '24 Hour' }].map((format) => (
                <View key={format.value} style={styles.radioItem}>
                  <RadioButton
                    value={format.value}
                    status={settings.display.timeFormat === format.value ? 'checked' : 'unchecked'}
                    onPress={() => updateDisplaySetting('timeFormat', format.value)}
                    color={theme.colors.primary}
                  />
                  <Text style={styles.radioLabel}>{format.label}</Text>
                </View>
              ))}
            </View>
          </View>
        </Card.Content>
      </Card>
    );
  };

  const renderBettingSettings = () => {
    return (
      <Card style={styles.settingsCard} elevation={2}>
        <Card.Content>
          <Title style={styles.sectionTitle}>Betting</Title>
          
          <View style={styles.settingItem}>
            <Text style={styles.settingLabel}>Default Stake</Text>
            <TextInput
              value={settings.betting.defaultStake.toString()}
              onChangeText={(value) => {
                const numValue = parseFloat(value) || 0;
                updateBettingSetting('defaultStake', numValue);
              }}
              keyboardType="numeric"
              mode="outlined"
              style={styles.textInput}
              left={<TextInput.Affix text="$" />}
            />
          </View>
          
          <View style={styles.settingItem}>
            <Text style={styles.settingLabel}>Maximum Stake</Text>
            <TextInput
              value={settings.betting.maxStake.toString()}
              onChangeText={(value) => {
                const numValue = parseFloat(value) || 0;
                updateBettingSetting('maxStake', numValue);
              }}
              keyboardType="numeric"
              mode="outlined"
              style={styles.textInput}
              left={<TextInput.Affix text="$" />}
            />
          </View>
          
          <View style={styles.settingItem}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Auto-Calculate Stakes</Text>
              <Text style={styles.settingDescription}>
                Use Kelly Criterion for optimal stake sizing
              </Text>
            </View>
            <Switch
              value={settings.betting.autoCalculateStakes}
              onValueChange={(value) => updateBettingSetting('autoCalculateStakes', value)}
              color={theme.colors.primary}
            />
          </View>
          
          <View style={styles.settingItem}>
            <Text style={styles.settingLabel}>Risk Tolerance</Text>
            <View style={styles.chipGroup}>
              {['low', 'medium', 'high'].map((risk) => (
                <Chip
                  key={risk}
                  mode={settings.betting.riskTolerance === risk ? 'flat' : 'outlined'}
                  selected={settings.betting.riskTolerance === risk}
                  onPress={() => updateBettingSetting('riskTolerance', risk)}
                  style={styles.chip}
                >
                  {risk.charAt(0).toUpperCase() + risk.slice(1)}
                </Chip>
              ))}
            </View>
          </View>
        </Card.Content>
      </Card>
    );
  };

  const renderDataSettings = () => {
    return (
      <Card style={styles.settingsCard} elevation={2}>
        <Card.Content>
          <Title style={styles.sectionTitle}>Data & Sync</Title>
          
          <View style={styles.settingItem}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Auto Refresh</Text>
              <Text style={styles.settingDescription}>
                Automatically refresh data when app is opened
              </Text>
            </View>
            <Switch
              value={settings.data.autoRefresh}
              onValueChange={(value) => updateDataSetting('autoRefresh', value)}
              color={theme.colors.primary}
            />
          </View>
          
          <View style={styles.settingItem}>
            <Text style={styles.settingLabel}>Refresh Interval (seconds)</Text>
            <TextInput
              value={settings.data.refreshInterval.toString()}
              onChangeText={(value) => {
                const numValue = parseInt(value) || 300;
                updateDataSetting('refreshInterval', numValue);
              }}
              keyboardType="numeric"
              mode="outlined"
              style={styles.textInput}
            />
          </View>
          
          <View style={styles.settingItem}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Cache Enabled</Text>
              <Text style={styles.settingDescription}>
                Store data locally for faster loading
              </Text>
            </View>
            <Switch
              value={settings.data.cacheEnabled}
              onValueChange={(value) => updateDataSetting('cacheEnabled', value)}
              color={theme.colors.primary}
            />
          </View>
          
          <View style={styles.settingItem}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Offline Mode</Text>
              <Text style={styles.settingDescription}>
                Use cached data when network is unavailable
              </Text>
            </View>
            <Switch
              value={settings.data.offlineMode}
              onValueChange={(value) => updateDataSetting('offlineMode', value)}
              color={theme.colors.primary}
            />
          </View>
          
          <Divider style={styles.divider} />
          
          <Button
            mode="outlined"
            onPress={clearCache}
            style={styles.actionButton}
            icon="delete"
          >
            Clear Cache
          </Button>
        </Card.Content>
      </Card>
    );
  };

  const renderPrivacySettings = () => {
    return (
      <Card style={styles.settingsCard} elevation={2}>
        <Card.Content>
          <Title style={styles.sectionTitle}>Privacy</Title>
          
          <View style={styles.settingItem}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Analytics</Text>
              <Text style={styles.settingDescription}>
                Help improve the app by sharing usage analytics
              </Text>
            </View>
            <Switch
              value={settings.privacy.analytics}
              onValueChange={(value) => updatePrivacySetting('analytics', value)}
              color={theme.colors.primary}
            />
          </View>
          
          <View style={styles.settingItem}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Crash Reporting</Text>
              <Text style={styles.settingDescription}>
                Automatically send crash reports to help fix bugs
              </Text>
            </View>
            <Switch
              value={settings.privacy.crashReporting}
              onValueChange={(value) => updatePrivacySetting('crashReporting', value)}
              color={theme.colors.primary}
            />
          </View>
          
          <View style={styles.settingItem}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Data Sharing</Text>
              <Text style={styles.settingDescription}>
                Share anonymized data with third-party services
              </Text>
            </View>
            <Switch
              value={settings.privacy.dataSharing}
              onValueChange={(value) => updatePrivacySetting('dataSharing', value)}
              color={theme.colors.primary}
            />
          </View>
        </Card.Content>
      </Card>
    );
  };

  const renderAboutSection = () => {
    return (
      <Card style={styles.settingsCard} elevation={2}>
        <Card.Content>
          <Title style={styles.sectionTitle}>About</Title>
          
          <List.Item
            title="Version"
            description="1.0.0"
            left={(props) => <List.Icon {...props} icon="information" />}
          />
          
          <List.Item
            title="Privacy Policy"
            description="View our privacy policy"
            left={(props) => <List.Icon {...props} icon="shield-account" />}
            right={(props) => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => Alert.alert('Privacy Policy', 'This would open the privacy policy.')}
          />
          
          <List.Item
            title="Terms of Service"
            description="View terms and conditions"
            left={(props) => <List.Icon {...props} icon="file-document" />}
            right={(props) => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => Alert.alert('Terms of Service', 'This would open the terms of service.')}
          />
          
          <List.Item
            title="Support"
            description="Get help and support"
            left={(props) => <List.Icon {...props} icon="help-circle" />}
            right={(props) => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => Alert.alert('Support', 'This would open the support page.')}
          />
          
          <Divider style={styles.divider} />
          
          <Button
            mode="outlined"
            onPress={resetSettings}
            style={styles.actionButton}
            icon="restore"
            buttonColor={theme.colors.errorContainer}
            textColor={theme.colors.error}
          >
            Reset All Settings
          </Button>
        </Card.Content>
      </Card>
    );
  };

  return (
    <ScrollView style={styles.container}>
      {renderNotificationSettings()}
      {renderDisplaySettings()}
      {renderBettingSettings()}
      {renderDataSettings()}
      {renderPrivacySettings()}
      {renderAboutSection()}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  settingsCard: {
    margin: 16,
    borderRadius: 12,
  },
  sectionTitle: {
    fontSize: 18,
    marginBottom: 16,
    color: theme.colors.onSurface,
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  settingInfo: {
    flex: 1,
    marginRight: 16,
  },
  settingLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: theme.colors.onSurface,
    marginBottom: 4,
  },
  settingDescription: {
    fontSize: 12,
    color: theme.colors.onSurfaceVariant,
  },
  radioGroup: {
    flexDirection: 'row',
    marginTop: 8,
  },
  radioItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 24,
  },
  radioLabel: {
    fontSize: 14,
    color: theme.colors.onSurface,
    marginLeft: 8,
  },
  chipGroup: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 8,
  },
  chip: {
    marginRight: 8,
    marginBottom: 8,
  },
  textInput: {
    width: 120,
  },
  divider: {
    marginVertical: 16,
  },
  actionButton: {
    marginTop: 8,
  },
});

export default SettingsScreen;