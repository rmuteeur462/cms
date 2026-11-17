import React from 'react';
import { View, ActivityIndicator, Text, StyleSheet } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useAuth } from '../store/AuthContext';
import { LoginScreen } from '../screens/auth/LoginScreen';
import { CitizenWelcomeScreen } from '../screens/citizen/CitizenWelcomeScreen';
import { CitizenLoginScreen } from '../screens/citizen/CitizenLoginScreen';
import { CitizenRegisterScreen } from '../screens/citizen/CitizenRegisterScreen';
import { MainTabsNavigator } from './MainTabsNavigator';
import { CitizenTabsNavigator } from './CitizenTabsNavigator';
import { Colors, Typography, Spacing } from '../constants/theme';
import { Ionicons } from '@expo/vector-icons';

import { LoginSuccessAnimation } from '../components/common/LoginSuccessAnimation';

const Stack = createNativeStackNavigator();

export const RootNavigator: React.FC = () => {
  const { user, token, isInitialLoading } = useAuth();

  if (isInitialLoading) {
    return (
      <LoginSuccessAnimation
        isSplash
        title="WSSP CMS"
        subtitle="Initializing Secure Session..."
      />
    );
  }

  const isCitizen = user?.account_type === 'citizen' || (!user?.is_staff && !user?.is_superuser);

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {token && user ? (
          isCitizen ? (
            <Stack.Screen name="CitizenMain" component={CitizenTabsNavigator} />
          ) : (
            <Stack.Screen name="Main" component={MainTabsNavigator} />
          )
        ) : (
          <>
            <Stack.Screen name="CitizenWelcome" component={CitizenWelcomeScreen} />
            <Stack.Screen name="CitizenLogin" component={CitizenLoginScreen} />
            <Stack.Screen name="CitizenRegister" component={CitizenRegisterScreen} />
            <Stack.Screen name="Login" component={LoginScreen} />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
};

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    backgroundColor: Colors.primaryDark,
    alignItems: 'center',
    justifyContent: 'center',
    padding: Spacing.xl,
  },
  loadingBox: {
    alignItems: 'center',
  },
  loadingTitle: {
    fontSize: Typography.fontSize.xxl,
    fontWeight: '900',
    color: Colors.textInverse,
    letterSpacing: 1,
  },
  loadingSubtitle: {
    fontSize: Typography.fontSize.sm,
    color: 'rgba(255, 255, 255, 0.7)',
    marginTop: 4,
  },
});
