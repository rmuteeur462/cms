import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { View, StyleSheet, Platform } from 'react-native';
import { HomeScreen } from '../screens/main/HomeScreen';
import { ComplaintsScreen } from '../screens/main/ComplaintsScreen';
import { ReportsScreen } from '../screens/main/ReportsScreen';
import { ProfileScreen } from '../screens/main/ProfileScreen';
import { AppHeader } from '../components/common/AppHeader';
import { Colors, Typography, BorderRadius } from '../constants/theme';
import { Ionicons } from '@expo/vector-icons';

const Tab = createBottomTabNavigator();

export const MainTabsNavigator: React.FC = () => {
  return (
    <View style={styles.container}>
      <AppHeader />
      <Tab.Navigator
        screenOptions={({ route }) => ({
          headerShown: false,
          tabBarActiveTintColor: Colors.primary,
          tabBarInactiveTintColor: Colors.textMuted,
          tabBarStyle: styles.tabBar,
          tabBarLabelStyle: styles.tabBarLabel,
          tabBarIcon: ({ focused, color, size }) => {
            let iconName: keyof typeof Ionicons.glyphMap = 'home';

            if (route.name === 'Home') {
              iconName = focused ? 'home' : 'home-outline';
            } else if (route.name === 'Complaints') {
              iconName = focused ? 'file-tray-full' : 'file-tray-outline';
            } else if (route.name === 'Reports') {
              iconName = focused ? 'stats-chart' : 'stats-chart-outline';
            } else if (route.name === 'Profile') {
              iconName = focused ? 'person' : 'person-outline';
            }

            return (
              <View style={[styles.iconContainer, focused && styles.iconFocused]}>
                <Ionicons name={iconName} size={22} color={color} />
              </View>
            );
          },
        })}
      >
        <Tab.Screen name="Home" component={HomeScreen} options={{ tabBarLabel: 'Home' }} />
        <Tab.Screen name="Complaints" component={ComplaintsScreen} options={{ tabBarLabel: 'Complaints' }} />
        <Tab.Screen name="Reports" component={ReportsScreen} options={{ tabBarLabel: 'Reports' }} />
        <Tab.Screen name="Profile" component={ProfileScreen} options={{ tabBarLabel: 'Profile' }} />
      </Tab.Navigator>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  tabBar: {
    backgroundColor: Colors.surface,
    borderTopWidth: 1,
    borderTopColor: Colors.border,
    height: Platform.OS === 'ios' ? 86 : 64,
    paddingTop: 6,
    paddingBottom: Platform.OS === 'ios' ? 24 : 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 8,
  },
  tabBarLabel: {
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 0.2,
    marginTop: 2,
  },
  iconContainer: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  iconFocused: {
    transform: [{ scale: 1.08 }],
  },
});
