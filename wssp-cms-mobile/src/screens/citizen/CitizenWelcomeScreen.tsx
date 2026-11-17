import React, { useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  TouchableOpacity,
  Image,
  Animated,
  Dimensions,
  StatusBar,
  Platform,
} from 'react-native';
import { Colors, Typography, Spacing, BorderRadius } from '../../constants/theme';
import { Ionicons } from '@expo/vector-icons';

const { width, height } = Dimensions.get('window');

interface CitizenWelcomeScreenProps {
  navigation: any;
}

export const CitizenWelcomeScreen: React.FC<CitizenWelcomeScreenProps> = ({ navigation }) => {
  // Entrance animations
  const logoAnim = useRef(new Animated.Value(0)).current;
  const titleAnim = useRef(new Animated.Value(0)).current;
  const ctaAnim = useRef(new Animated.Value(0)).current;
  const footerAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.stagger(120, [
      Animated.spring(logoAnim, { toValue: 1, tension: 60, friction: 8, useNativeDriver: true }),
      Animated.timing(titleAnim, { toValue: 1, duration: 420, useNativeDriver: true }),
      Animated.timing(ctaAnim, { toValue: 1, duration: 360, useNativeDriver: true }),
      Animated.timing(footerAnim, { toValue: 1, duration: 320, useNativeDriver: true }),
    ]).start();
  }, []);

  const translateFromBelow = (anim: Animated.Value) => ({
    opacity: anim,
    transform: [{ translateY: anim.interpolate({ inputRange: [0, 1], outputRange: [24, 0] }) }],
  });

  return (
    <SafeAreaView style={styles.safe}>
      <StatusBar barStyle="dark-content" />

      {/* Decorative soft glowing circles */}
      <View style={styles.bgCircle1} />
      <View style={styles.bgCircle2} />
      <View style={styles.bgCircle3} />

      <View style={styles.container}>

        {/* ─── Top: Brand Section ─── */}
        <View style={styles.topSection}>
          <Animated.View
            style={[
              styles.logoWrapper,
              {
                opacity: logoAnim,
                transform: [
                  { scale: logoAnim.interpolate({ inputRange: [0, 1], outputRange: [0.6, 1] }) },
                ],
              },
            ]}
          >
            <Image
              source={require('../../assets/imgs/wssp_logo.png')}
              style={styles.logo}
              resizeMode="contain"
            />
          </Animated.View>

          <Animated.Text style={[styles.orgName, translateFromBelow(titleAnim)]}>
            WSSP Peshawar
          </Animated.Text>
          <Animated.Text style={[styles.portalLabel, translateFromBelow(titleAnim)]}>
            CITIZEN COMPLAINT PORTAL
          </Animated.Text>
        </View>

        {/* ─── Bottom: Call to Action ─── */}
        <Animated.View style={[styles.ctaSection, translateFromBelow(ctaAnim)]}>

          {/* Register Button */}
          <TouchableOpacity
            style={styles.registerBtn}
            onPress={() => navigation.navigate('CitizenRegister')}
            activeOpacity={0.88}
          >
            <Ionicons name="person-add-outline" size={20} color={Colors.textInverse} style={styles.btnIcon} />
            <Text style={styles.registerBtnText}>Register Account</Text>
          </TouchableOpacity>

          {/* Sign In Button */}
          <TouchableOpacity
            style={styles.signInBtn}
            onPress={() => navigation.navigate('CitizenLogin')}
            activeOpacity={0.88}
          >
            <Ionicons name="log-in-outline" size={20} color={Colors.primary} style={styles.btnIcon} />
            <Text style={styles.signInBtnText}>Sign In</Text>
          </TouchableOpacity>
        </Animated.View>

        {/* ─── Staff Link Footer ─── */}
        <Animated.View style={[styles.staffFooter, { opacity: footerAnim }]}>
          <View style={styles.dividerRow}>
            <View style={styles.divider} />
            <Text style={styles.dividerText}>Are you WSSP staff?</Text>
            <View style={styles.divider} />
          </View>
          <TouchableOpacity
            onPress={() => navigation.navigate('Login')}
            hitSlop={{ top: 12, bottom: 12, left: 20, right: 20 }}
          >
            <Text style={styles.staffLink}>
              Staff Login  <Ionicons name="arrow-forward" size={13} color="#0080DF" />
            </Text>
          </TouchableOpacity>
        </Animated.View>

      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: '#EBF4FC', // Light blue background
  },
  container: {
    flex: 1,
    paddingHorizontal: Spacing.lg,
    paddingBottom: Platform.OS === 'android' ? Spacing.xl : Spacing.lg,
    justifyContent: 'space-between',
  },

  // ── Background decorative circles ──
  bgCircle1: {
    position: 'absolute',
    top: -height * 0.15,
    right: -width * 0.3,
    width: width * 0.8,
    height: width * 0.8,
    borderRadius: width * 0.4,
    backgroundColor: 'rgba(0, 128, 223, 0.08)',
  },
  bgCircle2: {
    position: 'absolute',
    bottom: height * 0.2,
    left: -width * 0.25,
    width: width * 0.6,
    height: width * 0.6,
    borderRadius: width * 0.3,
    backgroundColor: 'rgba(56, 189, 248, 0.1)',
  },
  bgCircle3: {
    position: 'absolute',
    bottom: -height * 0.05,
    right: -width * 0.1,
    width: width * 0.5,
    height: width * 0.5,
    borderRadius: width * 0.25,
    backgroundColor: 'rgba(0, 128, 223, 0.06)',
  },

  // ── Top section ──
  topSection: {
    alignItems: 'center',
    paddingTop: Spacing.xl * 1.8,
  },
  logoWrapper: {
    width: 124,
    height: 124,
    borderRadius: 62,
    backgroundColor: '#FFFFFF',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: Spacing.lg,
    shadowColor: '#0080DF',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.15,
    shadowRadius: 16,
    elevation: 8,
    borderWidth: 2,
    borderColor: 'rgba(0, 128, 223, 0.15)',
  },
  logo: {
    width: 95,
    height: 95,
  },
  orgName: {
    fontSize: Typography.fontSize.xxl * 1.1,
    fontWeight: '900',
    color: '#0A3663', // Deep corporate navy on light blue
    letterSpacing: 0.8,
    textAlign: 'center',
  },
  portalLabel: {
    fontSize: Typography.fontSize.sm,
    fontWeight: '700',
    color: '#0080DF', // WSSP vibrant blue
    letterSpacing: 2,
    textTransform: 'uppercase',
    marginTop: 6,
    textAlign: 'center',
  },

  // ── CTA section ──
  ctaSection: {
    gap: Spacing.md,
    marginTop: 'auto',
    marginBottom: Spacing.xl,
  },
  registerBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: Colors.primary,
    borderRadius: BorderRadius.lg,
    paddingVertical: 16,
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.25,
    shadowRadius: 12,
    elevation: 6,
  },
  btnIcon: {
    marginRight: 8,
  },
  registerBtnText: {
    fontSize: Typography.fontSize.md,
    fontWeight: '700',
    color: Colors.textInverse,
    letterSpacing: 0.5,
  },
  signInBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: BorderRadius.lg,
    paddingVertical: 16,
    borderWidth: 1.5,
    borderColor: '#C7E2FA',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  signInBtnText: {
    fontSize: Typography.fontSize.md,
    fontWeight: '700',
    color: Colors.primary,
    letterSpacing: 0.5,
  },

  // ── Staff footer ──
  staffFooter: {
    alignItems: 'center',
    paddingBottom: Spacing.sm,
    gap: Spacing.xs,
  },
  dividerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    width: '70%',
    marginBottom: Spacing.xs,
  },
  divider: {
    flex: 1,
    height: 1,
    backgroundColor: '#CBDDEE',
  },
  dividerText: {
    fontSize: 12,
    color: '#64748B',
    textAlign: 'center',
  },
  staffLink: {
    fontSize: Typography.fontSize.sm,
    color: '#0080DF',
    fontWeight: '700',
    letterSpacing: 0.3,
  },
});
