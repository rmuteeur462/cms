import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  SafeAreaView,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { Colors, Spacing, BorderRadius, Typography } from '../../constants/theme';
import { WSSPInput } from '../../components/common/WSSPInput';
import { WSSPButton } from '../../components/common/WSSPButton';
import { useAuth } from '../../store/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import { Config } from '../../constants/config';

export const LoginScreen: React.FC = () => {
  const { login, isLoading } = useAuth();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async () => {
    setError(null);
    if (!username.trim() || !password.trim()) {
      setError('Please enter both your username and password.');
      return;
    }

    const result = await login(username.trim(), password);
    if (!result.success) {
      setError(result.error || 'Authentication failed.');
    }
  };

  const fillQuickCredentials = (user: string, pass: string) => {
    setUsername(user);
    setPassword(pass);
    setError(null);
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        style={styles.keyboardView}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
        >
          {/* Top Decorative Banner */}
          <View style={styles.headerBox}>
            <View style={styles.emblemCircle}>
              <Ionicons name="water" size={38} color={Colors.accent} />
            </View>
            <Text style={styles.govTitle}>GOVERNMENT OF KHYBER PAKHTUNKHWA</Text>
            <Text style={styles.appTitle}>WSSP CMS</Text>
            <Text style={styles.deptSubtitle}>Water & Sanitation Services Peshawar</Text>
            <View style={styles.badgeLine}>
              <Text style={styles.badgeLineText}>COMPLAINT MANAGEMENT SYSTEM</Text>
            </View>
          </View>

          {/* Login Card */}
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Officer Portal Login</Text>
            <Text style={styles.cardSubtitle}>
              Sign in with your authorized WSSP departmental credentials
            </Text>

            {error ? (
              <View style={styles.errorBox}>
                <Ionicons name="alert-circle" size={20} color={Colors.danger} style={{ marginRight: 8 }} />
                <Text style={styles.errorBoxText}>{error}</Text>
              </View>
            ) : null}

            <WSSPInput
              label="Username"
              placeholder="e.g. ccho_officer"
              value={username}
              onChangeText={(t) => {
                setUsername(t);
                if (error) setError(null);
              }}
              autoCapitalize="none"
              autoCorrect={false}
              leftIcon="person-outline"
            />

            <WSSPInput
              label="Password"
              placeholder="Enter your password"
              value={password}
              onChangeText={(t) => {
                setPassword(t);
                if (error) setError(null);
              }}
              isPassword
              leftIcon="lock-closed-outline"
            />

            <WSSPButton
              title="Sign In to CMS"
              onPress={handleLogin}
              loading={isLoading}
              style={styles.loginBtn}
            />

            {/* Quick Test Accounts for Developer/Reviewer Convenience */}
            <View style={styles.quickFillSection}>
              <Text style={styles.quickFillHeading}>QUICK TEST ACCOUNTS (PHASE 3 VERIFIED):</Text>
              <View style={styles.chipsRow}>
                <TouchableOpacity
                  style={styles.accountChip}
                  onPress={() => fillQuickCredentials('ccho_officer', 'wssp12345')}
                  activeOpacity={0.7}
                >
                  <Ionicons name="shield" size={14} color={Colors.primary} style={{ marginRight: 4 }} />
                  <Text style={styles.accountChipText}>Head Office (All Zones)</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={styles.accountChip}
                  onPress={() => fillQuickCredentials('zone_a_officer', 'wssp12345')}
                  activeOpacity={0.7}
                >
                  <Ionicons name="location" size={14} color={Colors.primary} style={{ marginRight: 4 }} />
                  <Text style={styles.accountChipText}>Zone A (Restricted)</Text>
                </TouchableOpacity>
              </View>
            </View>
          </View>

          {/* Footer Info */}
          <View style={styles.footer}>
            <Text style={styles.helplineText}>Toll-Free Helpline: 1334</Text>
            <Text style={styles.versionText}>{Config.APP_VERSION}</Text>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: Colors.primaryDark,
  },
  keyboardView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    backgroundColor: Colors.background,
  },
  headerBox: {
    backgroundColor: Colors.primaryDark,
    alignItems: 'center',
    paddingTop: Spacing.xl,
    paddingBottom: Spacing.xxl,
    paddingHorizontal: Spacing.lg,
  },
  emblemCircle: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: 'rgba(255, 255, 255, 0.15)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: Spacing.sm,
    borderWidth: 2,
    borderColor: Colors.accent,
  },
  govTitle: {
    fontSize: 10,
    fontWeight: '800',
    color: Colors.accent,
    letterSpacing: 1.5,
    marginBottom: 4,
  },
  appTitle: {
    fontSize: 32,
    fontWeight: '900',
    color: Colors.textInverse,
    letterSpacing: 1,
  },
  deptSubtitle: {
    fontSize: Typography.fontSize.sm,
    color: 'rgba(255, 255, 255, 0.85)',
    fontWeight: '500',
    marginTop: 2,
    textAlign: 'center',
  },
  badgeLine: {
    backgroundColor: 'rgba(244, 180, 26, 0.2)',
    paddingHorizontal: Spacing.md,
    paddingVertical: 4,
    borderRadius: BorderRadius.full,
    marginTop: Spacing.md,
    borderWidth: 1,
    borderColor: Colors.accent,
  },
  badgeLineText: {
    color: Colors.accent,
    fontSize: 11,
    fontWeight: '800',
    letterSpacing: 1,
  },
  card: {
    backgroundColor: Colors.surface,
    marginHorizontal: Spacing.md,
    marginTop: -Spacing.lg,
    borderRadius: BorderRadius.xl,
    padding: Spacing.lg,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.08,
    shadowRadius: 12,
    elevation: 4,
  },
  cardTitle: {
    fontSize: Typography.fontSize.xl,
    fontWeight: '800',
    color: Colors.textPrimary,
  },
  cardSubtitle: {
    fontSize: Typography.fontSize.sm,
    color: Colors.textSecondary,
    marginTop: 4,
    marginBottom: Spacing.lg,
  },
  errorBox: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.status.rejectedBg,
    padding: Spacing.md,
    borderRadius: BorderRadius.md,
    marginBottom: Spacing.md,
    borderLeftWidth: 4,
    borderLeftColor: Colors.danger,
  },
  errorBoxText: {
    color: Colors.danger,
    fontSize: Typography.fontSize.sm,
    fontWeight: '600',
    flex: 1,
  },
  loginBtn: {
    marginTop: Spacing.sm,
  },
  quickFillSection: {
    marginTop: Spacing.xl,
    paddingTop: Spacing.md,
    borderTopWidth: 1,
    borderTopColor: Colors.border,
  },
  quickFillHeading: {
    fontSize: 10,
    fontWeight: '800',
    color: Colors.textMuted,
    letterSpacing: 0.8,
    marginBottom: Spacing.sm,
  },
  chipsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: Spacing.sm,
  },
  accountChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F0FDF4',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: BorderRadius.full,
    borderWidth: 1,
    borderColor: '#BBF7D0',
  },
  accountChipText: {
    fontSize: 12,
    fontWeight: '700',
    color: Colors.primary,
  },
  footer: {
    alignItems: 'center',
    marginVertical: Spacing.xl,
  },
  helplineText: {
    fontSize: Typography.fontSize.sm,
    fontWeight: '700',
    color: Colors.primary,
  },
  versionText: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textMuted,
    marginTop: 4,
  },
});
