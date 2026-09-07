import React from 'react';
import { View, ActivityIndicator, Text, StyleSheet } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useAuth } from '../store/AuthContext';
import { LoginScreen } from '../screens/auth/LoginScreen';
import { HomeScreen } from '../screens/main/HomeScreen';
import { Colors, Typography, Spacing } from '../constants/theme';
import { Ionicons } from '@expo/vector-icons';

const Stack = createNativeStackNavigator();

export const RootNavigator: React.FC = () => {
  const { user, token, isLoading } = useAuth();

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <View style={styles.loadingBox}>
          <Ionicons name="water" size={48} color={Colors.accent} />
          <ActivityIndicator size="large" color={Colors.accent} style={{ marginVertical: Spacing.md }} />
          <Text style={styles.loadingTitle}>WSSP CMS</Text>
          <Text style={styles.loadingSubtitle}>Verifying Security Credentials...</Text>
        </View>
      </View>
    );
  }

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {token && user ? (
          <Stack.Screen name="Home" component={HomeScreen} />
        ) : (
          <Stack.Screen name="Login" component={LoginScreen} />
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
