import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { View, StyleSheet, Platform } from 'react-native';
import { CitizenHomeScreen } from '../screens/citizen/CitizenHomeScreen';
import { CitizenComplaintsScreen } from '../screens/citizen/CitizenComplaintsScreen';
import { CitizenCreateComplaintScreen } from '../screens/citizen/CitizenCreateComplaintScreen';
import { CitizenTrackingScreen } from '../screens/citizen/CitizenTrackingScreen';
import { CitizenProfileScreen } from '../screens/citizen/CitizenProfileScreen';
import { AppHeader } from '../components/common/AppHeader';
import { Colors } from '../constants/theme';
import { Ionicons } from '@expo/vector-icons';

const Tab = createBottomTabNavigator();

export const CitizenTabsNavigator: React.FC = () => {
  return (
    <View style={styles.container}>
      <Tab.Navigator
        screenOptions={({ route }) => ({
          headerShown: true,
          header: () => <AppHeader />,
          tabBarActiveTintColor: '#1E40AF',
          tabBarInactiveTintColor: Colors.textMuted,
          tabBarStyle: styles.tabBar,
          tabBarLabelStyle: styles.tabBarLabel,
          tabBarIcon: ({ focused, color, size }) => {
            if (route.name === 'NewComplaint') {
              return (
                <View style={[styles.centerPlusButton, focused && styles.centerPlusButtonFocused]}>
                  <Ionicons name="add" size={26} color="#FFFFFF" />
                </View>
              );
            }

            let iconName: keyof typeof Ionicons.glyphMap = 'home';

            if (route.name === 'Home') {
              iconName = focused ? 'home' : 'home-outline';
            } else if (route.name === 'Complaints') {
              iconName = focused ? 'file-tray-full' : 'file-tray-outline';
            } else if (route.name === 'Tracking') {
              iconName = focused ? 'navigate' : 'navigate-outline';
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
        <Tab.Screen
          name="Home"
          component={CitizenHomeScreen}
          options={{ tabBarLabel: 'Home' }}
        />
        <Tab.Screen
          name="Complaints"
          component={CitizenComplaintsScreen}
          options={{ tabBarLabel: 'My Complaints' }}
        />
        <Tab.Screen
          name="NewComplaint"
          component={CitizenCreateComplaintScreen}
          options={{
            tabBarLabel: () => null,
          }}
        />
        <Tab.Screen
          name="Tracking"
          component={CitizenTrackingScreen}
          options={{ tabBarLabel: 'Track' }}
        />
        <Tab.Screen
          name="Profile"
          component={CitizenProfileScreen}
          options={{ tabBarLabel: 'Profile' }}
        />
      </Tab.Navigator>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  tabBar: {
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E2E8F0',
    height: Platform.OS === 'ios' ? 88 : 72,
    paddingTop: 6,
    paddingBottom: Platform.OS === 'ios' ? 24 : 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -2 },
    shadowOpacity: 0.06,
    shadowRadius: 8,
    elevation: 10,
  },
  tabBarLabel: {
    fontSize: 11,
    fontWeight: '600',
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
  centerPlusButton: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#1E40AF',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: -16,
    shadowColor: '#1E40AF',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.35,
    shadowRadius: 6,
    elevation: 6,
    borderWidth: 3,
    borderColor: '#FFFFFF',
  },
  centerPlusButtonFocused: {
    backgroundColor: '#2563EB',
    transform: [{ scale: 1.06 }],
  },
});

