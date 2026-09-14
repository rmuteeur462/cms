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
  Modal,
  TextInput,
  Image,
} from 'react-native';
import { Colors, Spacing, BorderRadius, Typography } from '../../constants/theme';
import { WSSPInput } from '../../components/common/WSSPInput';
import { useAuth } from '../../store/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import { Config, DEFAULT_DEV_MACHINE_IP } from '../../constants/config';

export const LoginScreen: React.FC = () => {
  const { login, isLoading } = useAuth();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  // Server settings modal state
  const [serverModalVisible, setServerModalVisible] = useState(false);
  const [serverInput, setServerInput] = useState(Config.BASE_URL);

  const handleLogin = async () => {
    setError(null);
    if (!username.trim() || !password.trim()) {
      setError('Please enter both your username and password.');
      return;
    }

    const result = await login(username.trim(), password);
    if (!result.success) {
      setError(result.error || 'Authentication failed. Please check credentials.');
    }
  };

  const handleSaveServer = async () => {
    if (serverInput.trim()) {
      await Config.setCustomBaseUrl(serverInput.trim());
    } else {
      await Config.setCustomBaseUrl(null);
    }
    setServerModalVisible(false);
    setError(null);
  };

  const handleResetServer = async () => {
    await Config.setCustomBaseUrl(null);
    const def = Config.BASE_URL;
    setServerInput(def);
    setServerModalVisible(false);
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
          showsVerticalScrollIndicator={false}
          bounces={false}
        >
          {/* Top Corporate Navy Header */}
          <View style={styles.headerBox}>
            <View style={styles.logoContainer}>
              <Image
                source={require('../../assets/imgs/wssp_logo.png')}
                style={styles.logoImage}
                resizeMode="contain"
              />
            </View>

            <Text style={styles.appTitle}>WSSP CMS</Text>
            <Text style={styles.deptSubtitle}>Water & Sanitation Services Peshawar</Text>

            <View style={styles.badgeLine}>
              <View style={styles.dotIndicator} />
              <Text style={styles.badgeLineText}>CITIZEN & OFFICER PORTAL</Text>
            </View>
          </View>

          {/* Full-Screen Seamless White Card Container */}
          <View style={styles.cardContainer}>
            {/* Top Portion: Form Content */}
            <View style={styles.formSection}>
              <View style={styles.cardHeader}>
                <Text style={styles.cardTitle}>Sign In</Text>
                <View style={styles.titleUnderline} />
              </View>
              <Text style={styles.cardSubtitle}>
                Enter your credentials to access the complaint portal
              </Text>

              {error ? (
                <View style={styles.errorBox}>
                  <Ionicons name="alert-circle" size={20} color="#DC2626" style={{ marginRight: 8, marginTop: 2 }} />
                  <View style={{ flex: 1 }}>
                    <Text style={styles.errorBoxText}>{error}</Text>
                    {error.includes('Cannot reach') && (
                      <TouchableOpacity
                        onPress={() => {
                          setServerInput(Config.BASE_URL);
                          setServerModalVisible(true);
                        }}
                        style={styles.errorActionBtn}
                      >
                        <Ionicons name="settings" size={13} color="#DC2626" style={{ marginRight: 4 }} />
                        <Text style={styles.errorActionText}>Configure Server IP</Text>
                      </TouchableOpacity>
                    )}
                  </View>
                </View>
              ) : null}

              <WSSPInput
                label="Username"
                placeholder="Enter your username"
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

              <TouchableOpacity
                style={[styles.loginBtn, isLoading && { opacity: 0.75 }]}
                onPress={handleLogin}
                disabled={isLoading}
                activeOpacity={0.85}
              >
                <Text style={styles.loginBtnText}>
                  {isLoading ? 'Signing In...' : 'Sign In'}
                </Text>
                <Ionicons name="arrow-forward" size={18} color="#FFFFFF" style={{ marginLeft: 8 }} />
              </TouchableOpacity>
            </View>

            {/* Anchored Footer Section */}
            <View style={styles.footerSection}>
              <View style={styles.helplineRow}>
                <View style={styles.helplineContent}>
                  <Ionicons name="call" size={14} color="#0080DF" style={{ marginRight: 6 }} />
                  <Text style={styles.bottomHelplineText}>
                    Landline Helpline: <Text style={styles.bottomHelplineNumber}>1334</Text>
                  </Text>
                </View>

                <TouchableOpacity
                  onPress={() => {
                    setServerInput(Config.BASE_URL);
                    setServerModalVisible(true);
                  }}
                  style={styles.gearBtn}
                  accessibilityLabel="Server settings"
                >
                  <Ionicons name="settings-outline" size={16} color="#64748B" />
                </TouchableOpacity>
              </View>

              <Text style={styles.copyrightText}>
                Water & Sanitation Services Peshawar • Govt. of KP
              </Text>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>

      {/* Discreet Server Settings Modal */}
      <Modal
        visible={serverModalVisible}
        transparent
        animationType="fade"
        onRequestClose={() => setServerModalVisible(false)}
      >
        <View style={styles.modalBackdrop}>
          <View style={styles.modalCard}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Server Configuration</Text>
              <TouchableOpacity onPress={() => setServerModalVisible(false)}>
                <Ionicons name="close" size={22} color="#6C757D" />
              </TouchableOpacity>
            </View>

            <Text style={styles.modalHint}>
              Enter the backend host URL (Default: {DEFAULT_DEV_MACHINE_IP}:8000):
            </Text>

            <TextInput
              style={styles.serverTextInput}
              value={serverInput}
              onChangeText={setServerInput}
              placeholder={`http://${DEFAULT_DEV_MACHINE_IP}:8000`}
              placeholderTextColor="#ADB5BD"
              autoCapitalize="none"
              autoCorrect={false}
            />

            <View style={styles.modalButtonsRow}>
              <TouchableOpacity
                style={styles.modalBtnReset}
                onPress={handleResetServer}
              >
                <Text style={styles.modalBtnResetText}>Auto-Detect</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.modalBtnSave}
                onPress={handleSaveServer}
              >
                <Text style={styles.modalBtnSaveText}>Save</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#0A3663', // Deep Corporate Navy Blue
  },
  keyboardView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    backgroundColor: '#0A3663', // Continuous Navy Blue background
  },

  // WSSP Blue Header Banner
  headerBox: {
    backgroundColor: '#0A3663',
    alignItems: 'center',
    paddingTop: Platform.OS === 'android' ? 24 : 16,
    paddingBottom: 24,
    paddingHorizontal: 20,
  },
  logoContainer: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#FFFFFF',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.25,
    shadowRadius: 8,
    elevation: 6,
    padding: 3,
  },
  logoImage: {
    width: '100%',
    height: '100%',
  },
  appTitle: {
    fontSize: 26,
    fontWeight: '900',
    color: '#FFFFFF',
    letterSpacing: 0.5,
  },
  deptSubtitle: {
    fontSize: 13,
    color: '#93C5FD',
    fontWeight: '600',
    marginTop: 2,
    textAlign: 'center',
    maxWidth: 280,
  },
  badgeLine: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 122, 0, 0.18)',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 20,
    marginTop: 10,
    borderWidth: 1,
    borderColor: '#FF7A00',
  },
  dotIndicator: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: '#FF7A00',
    marginRight: 6,
  },
  badgeLineText: {
    color: '#FFA940',
    fontSize: 10,
    fontWeight: '800',
    letterSpacing: 0.8,
  },

  // Full-Screen Card Container
  cardContainer: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 32,
    borderTopRightRadius: 32,
    paddingHorizontal: 24,
    paddingTop: 28,
    paddingBottom: 24,
    justifyContent: 'space-between',
    minHeight: 450,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -4 },
    shadowOpacity: 0.12,
    shadowRadius: 16,
    elevation: 8,
  },
  formSection: {
    width: '100%',
  },
  cardHeader: {
    marginBottom: 4,
  },
  cardTitle: {
    fontSize: 24,
    fontWeight: '800',
    color: '#0F172A',
  },
  titleUnderline: {
    width: 42,
    height: 4,
    backgroundColor: '#FF7A00',
    borderRadius: 2,
    marginTop: 4,
  },
  cardSubtitle: {
    fontSize: 13.5,
    color: '#64748B',
    marginTop: 6,
    marginBottom: 22,
    lineHeight: 19,
  },
  errorBox: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    backgroundColor: '#FEF2F2',
    padding: 12,
    borderRadius: 10,
    marginBottom: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#DC2626',
    borderWidth: 1,
    borderColor: '#FECACA',
  },
  errorBoxText: {
    color: '#991B1B',
    fontSize: 13,
    fontWeight: '500',
    lineHeight: 18,
  },
  errorActionBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 6,
    paddingVertical: 4,
    paddingHorizontal: 8,
    backgroundColor: '#FEE2E2',
    borderRadius: 4,
    alignSelf: 'flex-start',
  },
  errorActionText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#DC2626',
  },
  loginBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#0080DF',
    paddingVertical: 15,
    borderRadius: 14,
    marginTop: 12,
    shadowColor: '#0080DF',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.35,
    shadowRadius: 10,
    elevation: 5,
  },
  loginBtnText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '800',
    letterSpacing: 0.3,
  },

  // Anchored Footer Section
  footerSection: {
    marginTop: 28,
    alignItems: 'center',
    width: '100%',
  },
  helplineRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
    marginBottom: 12,
  },
  helplineContent: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F1F5F9',
    paddingHorizontal: 16,
    paddingVertical: 9,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  bottomHelplineText: {
    fontSize: 13,
    color: '#334155',
    fontWeight: '500',
  },
  bottomHelplineNumber: {
    color: '#0080DF',
    fontWeight: '800',
    letterSpacing: 0.5,
  },
  gearBtn: {
    padding: 8,
    borderRadius: 20,
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  copyrightText: {
    fontSize: 11.5,
    color: '#94A3B8',
    fontWeight: '600',
    textAlign: 'center',
  },

  // Server Modal
  modalBackdrop: {
    flex: 1,
    backgroundColor: 'rgba(10, 54, 99, 0.55)',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
  },
  modalCard: {
    width: '100%',
    maxWidth: 380,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.2,
    shadowRadius: 12,
    elevation: 8,
  },
  modalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  modalTitle: {
    fontSize: 17,
    fontWeight: '800',
    color: '#0A3663',
  },
  modalHint: {
    fontSize: 12.5,
    color: '#64748B',
    marginBottom: 12,
    lineHeight: 18,
  },
  serverTextInput: {
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#CBD5E1',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 14,
    color: '#0F172A',
    marginBottom: 16,
  },
  modalButtonsRow: {
    flexDirection: 'row',
    gap: 10,
  },
  modalBtnReset: {
    flex: 1,
    paddingVertical: 11,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#CBD5E1',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
  },
  modalBtnResetText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#475569',
  },
  modalBtnSave: {
    flex: 1,
    paddingVertical: 11,
    borderRadius: 8,
    backgroundColor: '#0080DF',
    alignItems: 'center',
  },
  modalBtnSaveText: {
    fontSize: 13,
    fontWeight: '700',
    color: '#FFFFFF',
  },
});
