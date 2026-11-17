import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  SafeAreaView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  Animated,
  Image,
} from 'react-native';
import { WSSPInput } from '../../components/common/WSSPInput';
import { useAuth } from '../../store/AuthContext';
import { Colors, Typography, Spacing, BorderRadius } from '../../constants/theme';
import { Ionicons } from '@expo/vector-icons';
import { LoginSuccessAnimation } from '../../components/common/LoginSuccessAnimation';

interface CitizenLoginScreenProps {
  navigation: any;
  route?: any;
}

export const CitizenLoginScreen: React.FC<CitizenLoginScreenProps> = ({ navigation, route }) => {
  const { loginCitizen, commitSession, isLoading } = useAuth();

  const [mobileNumber, setMobileNumber] = useState(route?.params?.prefillMobile || '');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [successSession, setSuccessSession] = useState<{ token: string; user: any } | null>(null);

  const shakeAnim = useRef(new Animated.Value(0)).current;

  const triggerShake = () => {
    Animated.sequence([
      Animated.timing(shakeAnim, { toValue: 10, duration: 60, useNativeDriver: true }),
      Animated.timing(shakeAnim, { toValue: -10, duration: 60, useNativeDriver: true }),
      Animated.timing(shakeAnim, { toValue: 8, duration: 60, useNativeDriver: true }),
      Animated.timing(shakeAnim, { toValue: -8, duration: 60, useNativeDriver: true }),
      Animated.timing(shakeAnim, { toValue: 0, duration: 60, useNativeDriver: true }),
    ]).start();
  };

  const handleLogin = async () => {
    setError(null);

    const mobile = mobileNumber.trim();
    if (!mobile || !password.trim()) {
      setError('Please enter both your mobile number and password.');
      triggerShake();
      return;
    }

    const result = await loginCitizen(mobile, password);

    if (result.success && result.token && result.user) {
      setSuccessSession({ token: result.token, user: result.user });
    } else {
      const msg = result.error || 'Authentication failed. Please check your mobile number and password.';
      setError(msg);
      triggerShake();
    }
  };

  const handleForgotPassword = () => {
    Alert.alert(
      'Password Recovery',
      'If you have forgotten your password, please contact WSSP Peshawar helpline:\n\n📞  1334\n\nA WSSP representative will help you recover your account.',
      [{ text: 'OK', style: 'default' }],
    );
  };

  if (successSession) {
    return (
      <LoginSuccessAnimation
        onAnimationComplete={() => {
          commitSession(successSession.token, successSession.user);
        }}
        title="Welcome Back!"
        subtitle="Logging you into your WSSP account…"
      />
    );
  }

  return (
    <SafeAreaView style={styles.safe}>
      <KeyboardAvoidingView
        style={styles.flex}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        <ScrollView
          contentContainerStyle={styles.scroll}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          {/* Header / Back Button */}
          <View style={styles.headerRow}>
            <TouchableOpacity
              style={styles.backBtn}
              onPress={() => navigation.goBack()}
              hitSlop={{ top: 10, left: 10, bottom: 10, right: 10 }}
            >
              <Ionicons name="arrow-back" size={22} color={Colors.textInverse} />
            </TouchableOpacity>
          </View>

          {/* Brand Section */}
          <View style={styles.brandSection}>
            <Image
              source={require('../../assets/imgs/wssp_logo.png')}
              style={styles.logo}
              resizeMode="contain"
            />
            <Text style={styles.appName}>WSSP Citizen Portal</Text>
            <Text style={styles.appSubtitle}>Water & Sanitation Services Peshawar</Text>
          </View>

          {/* Card */}
          <Animated.View style={[styles.card, { transform: [{ translateX: shakeAnim }] }]}>
            <Text style={styles.cardTitle}>Sign In</Text>
            <Text style={styles.cardSubtitle}>Enter your registered mobile number</Text>

            {/* Error Banner */}
            {error ? (
              <View style={styles.errorBanner}>
                <Ionicons name="alert-circle" size={16} color={Colors.error} />
                <Text style={styles.errorText}>{error}</Text>
              </View>
            ) : null}

            {/* Mobile Number */}
            <WSSPInput
              label="Mobile Number"
              value={mobileNumber}
              onChangeText={(t) => { setMobileNumber(t); setError(null); }}
              placeholder="e.g. 03001234567"
              keyboardType="phone-pad"
              autoCapitalize="none"
              leftIcon="call-outline"
              helperText="The number you used to register"
            />

            {/* Password — uses WSSPInput's built-in isPassword show/hide */}
            <WSSPInput
              label="Password"
              value={password}
              onChangeText={(t) => { setPassword(t); setError(null); }}
              placeholder="Your password"
              isPassword
              autoCapitalize="none"
              leftIcon="lock-closed-outline"
            />

            {/* Forgot Password */}
            <TouchableOpacity style={styles.forgotRow} onPress={handleForgotPassword}>
              <Text style={styles.forgotText}>Forgot password? Call 1334</Text>
            </TouchableOpacity>

            {/* Sign In Button */}
            <TouchableOpacity
              style={[styles.signInBtn, isLoading && styles.signInBtnDisabled]}
              onPress={handleLogin}
              disabled={isLoading}
              activeOpacity={0.85}
            >
              {isLoading ? (
                <ActivityIndicator size="small" color={Colors.textInverse} />
              ) : (
                <>
                  <Ionicons name="log-in-outline" size={20} color={Colors.textInverse} style={styles.btnIcon} />
                  <Text style={styles.signInBtnText}>Sign In</Text>
                </>
              )}
            </TouchableOpacity>

            {/* Register Link */}
            <View style={styles.registerRow}>
              <Text style={styles.registerPrompt}>New to WSSP Citizen Portal? </Text>
              <TouchableOpacity onPress={() => navigation.navigate('CitizenRegister')}>
                <Text style={styles.registerLink}>Create Account</Text>
              </TouchableOpacity>
            </View>
          </Animated.View>

          {/* Footer */}
          <View style={styles.footer}>
            <Text style={styles.footerText}>
              For complaints &amp; queries, call WSSP helpline{' '}
              <Text style={styles.footerHighlight}>1334</Text>
            </Text>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: Colors.primaryDark,
  },
  flex: {
    flex: 1,
  },
  scroll: {
    flexGrow: 1,
    paddingHorizontal: Spacing.lg,
    paddingBottom: Spacing.xl,
  },
  headerRow: {
    paddingTop: Spacing.md,
    marginBottom: Spacing.sm,
  },
  backBtn: {
    width: 38,
    height: 38,
    borderRadius: 19,
    backgroundColor: 'rgba(255,255,255,0.12)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  brandSection: {
    alignItems: 'center',
    paddingVertical: Spacing.lg,
  },
  logo: {
    width: 80,
    height: 80,
    marginBottom: Spacing.sm,
  },
  appName: {
    fontSize: Typography.fontSize.xl,
    fontWeight: '800',
    color: Colors.textInverse,
    letterSpacing: 0.5,
  },
  appSubtitle: {
    fontSize: Typography.fontSize.xs,
    color: 'rgba(255,255,255,0.65)',
    marginTop: 2,
    textAlign: 'center',
  },
  card: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.xl,
    padding: Spacing.lg,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.18,
    shadowRadius: 20,
    elevation: 10,
    marginBottom: Spacing.lg,
  },
  cardTitle: {
    fontSize: Typography.fontSize.xxl,
    fontWeight: '800',
    color: Colors.textPrimary,
    marginBottom: 4,
  },
  cardSubtitle: {
    fontSize: Typography.fontSize.sm,
    color: Colors.textSecondary,
    marginBottom: Spacing.md,
  },
  errorBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FEF2F2',
    borderRadius: BorderRadius.md,
    padding: Spacing.sm,
    marginBottom: Spacing.md,
    borderLeftWidth: 3,
    borderLeftColor: Colors.error,
    gap: 8,
  },
  errorText: {
    flex: 1,
    fontSize: Typography.fontSize.sm,
    color: Colors.error,
    lineHeight: 18,
  },
  forgotRow: {
    alignSelf: 'flex-end',
    marginBottom: Spacing.md,
    marginTop: -Spacing.xs,
  },
  forgotText: {
    fontSize: Typography.fontSize.sm,
    color: Colors.primary,
    fontWeight: '600',
  },
  signInBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: Colors.primary,
    borderRadius: BorderRadius.lg,
    paddingVertical: 14,
    marginBottom: Spacing.md,
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 5,
  },
  signInBtnDisabled: {
    backgroundColor: Colors.textMuted,
    shadowOpacity: 0,
    elevation: 0,
  },
  btnIcon: {
    marginRight: 8,
  },
  signInBtnText: {
    fontSize: Typography.fontSize.md,
    fontWeight: '700',
    color: Colors.textInverse,
    letterSpacing: 0.5,
  },
  registerRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: Spacing.xs,
  },
  registerPrompt: {
    fontSize: Typography.fontSize.sm,
    color: Colors.textSecondary,
  },
  registerLink: {
    fontSize: Typography.fontSize.sm,
    color: Colors.primary,
    fontWeight: '700',
  },
  footer: {
    alignItems: 'center',
    paddingTop: Spacing.sm,
  },
  footerText: {
    fontSize: Typography.fontSize.xs,
    color: 'rgba(255,255,255,0.5)',
    textAlign: 'center',
  },
  footerHighlight: {
    color: Colors.secondary,
    fontWeight: '700',
  },
});
