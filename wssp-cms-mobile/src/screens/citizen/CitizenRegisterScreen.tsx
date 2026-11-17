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
  ActivityIndicator,
  Alert,
} from 'react-native';
import { WSSPInput } from '../../components/common/WSSPInput';
import { useAuth } from '../../store/AuthContext';
import { Colors, Typography, Spacing, BorderRadius } from '../../constants/theme';
import { Ionicons } from '@expo/vector-icons';

interface CitizenRegisterScreenProps {
  navigation: any;
}

export const CitizenRegisterScreen: React.FC<CitizenRegisterScreenProps> = ({ navigation }) => {
  const { registerCitizen, isLoading } = useAuth();

  const [fullName, setFullName] = useState('');
  const [mobileNumber, setMobileNumber] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [email, setEmail] = useState('');
  const [address, setAddress] = useState('');

  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleRegister = async () => {
    setError(null);
    setSuccessMessage(null);

    // Form Validations
    if (!fullName.trim()) {
      setError('Please enter your full name.');
      return;
    }
    if (!mobileNumber.trim()) {
      setError('Please enter your 11-digit mobile number.');
      return;
    }
    if (!password) {
      setError('Please enter a password.');
      return;
    }
    if (password.length < 8) {
      setError('Password must be at least 8 characters long.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match. Please re-enter.');
      return;
    }

    const res = await registerCitizen({
      full_name: fullName.trim(),
      mobile_number: mobileNumber.trim(),
      password,
      confirm_password: confirmPassword,
      email: email.trim(),
      address: address.trim(),
    });

    if (res.success) {
      setSuccessMessage('Your account has been created successfully! You can now log in.');
      Alert.alert(
        'Registration Successful',
        'Your account has been created successfully. Please log in with your mobile number and password.',
        [
          {
            text: 'Proceed to Login',
            onPress: () => navigation.navigate('Login', { prefillMobile: mobileNumber.trim() }),
          },
        ]
      );
    } else {
      setError(res.error || 'Registration failed. Please check the information provided.');
    }
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
          showsVerticalScrollIndicator={false}
        >
          {/* Header Banner */}
          <View style={styles.headerBox}>
            <TouchableOpacity
              onPress={() => navigation.goBack()}
              style={styles.backButton}
              activeOpacity={0.7}
            >
              <Ionicons name="arrow-back" size={24} color={Colors.textInverse} />
            </TouchableOpacity>
            <View style={styles.badgeRow}>
              <View style={styles.govBadge}>
                <Ionicons name="shield-checkmark" size={14} color="#60A5FA" />
                <Text style={styles.govBadgeText}>CITIZEN PORTAL</Text>
              </View>
            </View>
            <Text style={styles.headerTitle}>Create Account</Text>
            <Text style={styles.headerSubtitle}>
              Register to report municipal issues, track resolutions, and rate WSSP services.
            </Text>
          </View>

          {/* Form Card */}
          <View style={styles.formCard}>
            {error && (
              <View style={styles.errorBanner}>
                <Ionicons name="alert-circle" size={20} color={Colors.error} />
                <Text style={styles.errorText}>{error}</Text>
              </View>
            )}

            {successMessage && (
              <View style={styles.successBanner}>
                <Ionicons name="checkmark-circle" size={20} color={Colors.success} />
                <Text style={styles.successText}>{successMessage}</Text>
              </View>
            )}

            <WSSPInput
              label="Full Name *"
              placeholder="e.g. Muhammad Ahmad"
              value={fullName}
              onChangeText={setFullName}
              leftIcon="person-outline"
              autoCapitalize="words"
            />

            <WSSPInput
              label="Mobile Number *"
              placeholder="03001234567"
              value={mobileNumber}
              onChangeText={setMobileNumber}
              leftIcon="call-outline"
              keyboardType="phone-pad"
              helperText="11-digit mobile number (used as your citizen login ID)"
            />

            <WSSPInput
              label="Password *"
              placeholder="At least 8 characters"
              value={password}
              onChangeText={setPassword}
              leftIcon="lock-closed-outline"
              secureTextEntry
            />

            <WSSPInput
              label="Confirm Password *"
              placeholder="Re-enter password"
              value={confirmPassword}
              onChangeText={setConfirmPassword}
              leftIcon="lock-closed-outline"
              secureTextEntry
            />

            <WSSPInput
              label="Email (Optional)"
              placeholder="citizen@example.com"
              value={email}
              onChangeText={setEmail}
              leftIcon="mail-outline"
              keyboardType="email-address"
              autoCapitalize="none"
            />

            <WSSPInput
              label="Address (Optional)"
              placeholder="House #, Street #, Mohallah / Sector"
              value={address}
              onChangeText={setAddress}
              leftIcon="location-outline"
              helperText="Default location for quicker complaint filing"
            />

            <TouchableOpacity
              style={[styles.submitButton, isLoading && styles.submitButtonDisabled]}
              onPress={handleRegister}
              disabled={isLoading}
              activeOpacity={0.85}
            >
              {isLoading ? (
                <ActivityIndicator color="#FFFFFF" size="small" />
              ) : (
                <>
                  <Text style={styles.submitButtonText}>Create Account</Text>
                  <Ionicons name="arrow-forward" size={18} color="#FFFFFF" style={{ marginLeft: 8 }} />
                </>
              )}
            </TouchableOpacity>

            <View style={styles.loginRow}>
              <Text style={styles.loginPrompt}>Already have an account? </Text>
              <TouchableOpacity onPress={() => navigation.navigate('Login')}>
                <Text style={styles.loginLink}>Sign In</Text>
              </TouchableOpacity>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#0F2744',
  },
  keyboardView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    backgroundColor: '#F3F4F6',
  },
  headerBox: {
    backgroundColor: '#0F2744',
    paddingTop: Platform.OS === 'ios' ? 16 : 24,
    paddingBottom: 28,
    paddingHorizontal: Spacing.xl,
    borderBottomLeftRadius: 24,
    borderBottomRightRadius: 24,
  },
  backButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.12)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: Spacing.md,
  },
  badgeRow: {
    flexDirection: 'row',
    marginBottom: 8,
  },
  govBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(30, 58, 138, 0.7)',
    borderColor: '#3B82F6',
    borderWidth: 1,
    borderRadius: 12,
    paddingHorizontal: 10,
    paddingVertical: 3,
    gap: 6,
  },
  govBadgeText: {
    color: '#93C5FD',
    fontSize: 10,
    fontWeight: '700',
    letterSpacing: 0.8,
  },
  headerTitle: {
    fontSize: Typography.fontSize.xxl,
    fontWeight: '800',
    color: Colors.textInverse,
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: Typography.fontSize.sm,
    color: 'rgba(255, 255, 255, 0.75)',
    lineHeight: 20,
  },
  formCard: {
    backgroundColor: '#FFFFFF',
    marginHorizontal: Spacing.md,
    marginTop: -16,
    marginBottom: Spacing.xxl,
    borderRadius: BorderRadius.lg,
    padding: Spacing.lg,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.08,
    shadowRadius: 10,
    elevation: 3,
  },
  errorBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FEF2F2',
    borderColor: '#FCA5A5',
    borderWidth: 1,
    borderRadius: BorderRadius.md,
    padding: Spacing.md,
    marginBottom: Spacing.md,
    gap: 8,
  },
  errorText: {
    flex: 1,
    color: Colors.error,
    fontSize: Typography.fontSize.sm,
    fontWeight: '500',
  },
  successBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F0FDF4',
    borderColor: '#86EFAC',
    borderWidth: 1,
    borderRadius: BorderRadius.md,
    padding: Spacing.md,
    marginBottom: Spacing.md,
    gap: 8,
  },
  successText: {
    flex: 1,
    color: Colors.success,
    fontSize: Typography.fontSize.sm,
    fontWeight: '600',
  },
  submitButton: {
    backgroundColor: '#1E40AF',
    borderRadius: BorderRadius.md,
    paddingVertical: 14,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: Spacing.md,
    shadowColor: '#1E40AF',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.25,
    shadowRadius: 6,
    elevation: 3,
  },
  submitButtonDisabled: {
    opacity: 0.6,
  },
  submitButtonText: {
    color: '#FFFFFF',
    fontSize: Typography.fontSize.md,
    fontWeight: '700',
  },
  loginRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: Spacing.lg,
  },
  loginPrompt: {
    color: Colors.textMuted,
    fontSize: Typography.fontSize.sm,
  },
  loginLink: {
    color: '#1E40AF',
    fontSize: Typography.fontSize.sm,
    fontWeight: '700',
  },
});

