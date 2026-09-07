import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { AuthProvider } from './src/store/AuthContext';
import { RootNavigator } from './src/navigation/RootNavigator';
import { MobileWebFrame } from './src/components/common/MobileWebFrame';

export default function App() {
  return (
    <SafeAreaProvider>
      <StatusBar style="light" />
      <AuthProvider>
        <MobileWebFrame>
          <RootNavigator />
        </MobileWebFrame>
      </AuthProvider>
    </SafeAreaProvider>
  );
}
