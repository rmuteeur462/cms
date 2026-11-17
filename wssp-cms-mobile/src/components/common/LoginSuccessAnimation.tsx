import React, { useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Animated,
  Easing,
  Image,
  Dimensions,
} from 'react-native';

const { width } = Dimensions.get('window');

interface LoginSuccessAnimationProps {
  onAnimationComplete?: () => void;
  title?: string;
  subtitle?: string;
  isSplash?: boolean;
}

export const LoginSuccessAnimation: React.FC<LoginSuccessAnimationProps> = ({
  onAnimationComplete,
  title = 'WSSP CMS',
  subtitle = 'Complaint Management Portal',
  isSplash = false,
}) => {
  // Animation drivers
  const screenFade   = useRef(new Animated.Value(0)).current;
  const logoScale    = useRef(new Animated.Value(0.5)).current;
  const logoOpacity  = useRef(new Animated.Value(0)).current;
  const ripple1      = useRef(new Animated.Value(0)).current;
  const ripple2      = useRef(new Animated.Value(0)).current;
  const ripple3      = useRef(new Animated.Value(0)).current;
  const pulse        = useRef(new Animated.Value(1)).current;
  const contentFade  = useRef(new Animated.Value(0)).current;
  const contentSlide = useRef(new Animated.Value(20)).current;
  const progressBar  = useRef(new Animated.Value(0)).current;

  // Logo size — floats freely, no card wrapping it
  const logoW = Math.min(width * 0.60, 240);
  const logoH = Math.round(logoW * (717 / 892));

  // Ripple ring base — sized around the logo
  const ringBase = Math.max(logoW, logoH);

  useEffect(() => {
    // 1. Screen + logo entrance
    Animated.parallel([
      Animated.timing(screenFade, {
        toValue: 1, duration: 400,
        easing: Easing.out(Easing.cubic),
        useNativeDriver: true,
      }),
      Animated.timing(logoOpacity, {
        toValue: 1, duration: 450,
        useNativeDriver: true,
      }),
      Animated.spring(logoScale, {
        toValue: 1, friction: 6, tension: 50,
        useNativeDriver: true,
      }),
      // First ripple fires immediately
      Animated.timing(ripple1, {
        toValue: 1, duration: 1000,
        easing: Easing.out(Easing.ease),
        useNativeDriver: true,
      }),
    ]).start();

    // 2. Staggered ripples
    const t2 = setTimeout(() => {
      Animated.timing(ripple2, {
        toValue: 1, duration: 1000,
        easing: Easing.out(Easing.ease),
        useNativeDriver: true,
      }).start();
    }, 260);

    const t3 = setTimeout(() => {
      Animated.timing(ripple3, {
        toValue: 1, duration: 1000,
        easing: Easing.out(Easing.ease),
        useNativeDriver: true,
      }).start();
    }, 520);

    // 3. Gentle breathing pulse on logo
    const pulseLoop = Animated.loop(
      Animated.sequence([
        Animated.timing(pulse, {
          toValue: 1.04, duration: 900,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
        Animated.timing(pulse, {
          toValue: 1, duration: 900,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
      ])
    );
    pulseLoop.start();

    // 4. Bottom content slides in
    const tContent = setTimeout(() => {
      Animated.parallel([
        Animated.timing(contentFade, {
          toValue: 1, duration: 420,
          useNativeDriver: true,
        }),
        Animated.timing(contentSlide, {
          toValue: 0, duration: 420,
          easing: Easing.out(Easing.cubic),
          useNativeDriver: true,
        }),
        Animated.timing(progressBar, {
          toValue: 1, duration: 1100,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: false,
        }),
      ]).start();
    }, 380);

    // 5. Completion callback
    let tDone: ReturnType<typeof setTimeout> | null = null;
    if (onAnimationComplete) {
      tDone = setTimeout(() => onAnimationComplete(), 1900);
    }

    return () => {
      pulseLoop.stop();
      clearTimeout(t2); clearTimeout(t3);
      clearTimeout(tContent);
      if (tDone) clearTimeout(tDone);
    };
  }, [onAnimationComplete]);

  // Ripple interpolations
  const r1Scale   = ripple1.interpolate({ inputRange: [0, 1], outputRange: [0.9, 2.2] });
  const r1Opacity = ripple1.interpolate({ inputRange: [0, 0.4, 1], outputRange: [0.65, 0.3, 0] });
  const r2Scale   = ripple2.interpolate({ inputRange: [0, 1], outputRange: [0.9, 2.6] });
  const r2Opacity = ripple2.interpolate({ inputRange: [0, 0.4, 1], outputRange: [0.55, 0.25, 0] });
  const r3Scale   = ripple3.interpolate({ inputRange: [0, 1], outputRange: [0.9, 3.1] });
  const r3Opacity = ripple3.interpolate({ inputRange: [0, 0.4, 1], outputRange: [0.45, 0.2, 0] });

  const progressWidth = progressBar.interpolate({
    inputRange: [0, 1], outputRange: ['0%', '100%'],
  });

  return (
    <Animated.View style={[styles.container, { opacity: screenFade }]}>

      {/* ── Ambient background glow orbs ── */}
      <View style={styles.glowTop} />
      <View style={styles.glowBottom} />
      <View style={styles.glowCentre} />

      {/* ── Logo zone: ripple rings + floating logo ── */}
      <View style={styles.logoZone}>

        {/* Ripple rings expand from centre behind logo */}
        <Animated.View style={[styles.ring, {
          width: ringBase, height: ringBase, borderRadius: ringBase / 2,
          borderColor: 'rgba(2, 173, 245, 0.55)',
          transform: [{ scale: r1Scale }], opacity: r1Opacity,
        }]} />
        <Animated.View style={[styles.ring, {
          width: ringBase, height: ringBase, borderRadius: ringBase / 2,
          borderColor: 'rgba(187, 210, 255, 0.45)',
          transform: [{ scale: r2Scale }], opacity: r2Opacity,
        }]} />
        <Animated.View style={[styles.ring, {
          width: ringBase, height: ringBase, borderRadius: ringBase / 2,
          borderColor: 'rgba(255, 145, 55, 0.35)',
          transform: [{ scale: r3Scale }], opacity: r3Opacity,
        }]} />

        {/* Soft glow circle directly behind logo (no box, no border) */}
        <View style={[styles.logoGlow, { width: ringBase * 0.85, height: ringBase * 0.85, borderRadius: ringBase * 0.5 }]} />

        {/* Logo floats freely — transparent background, no card */}
        <Animated.View
          style={{
            width: logoW,
            height: logoH,
            opacity: logoOpacity,
            transform: [{ scale: Animated.multiply(logoScale, pulse) }],
          }}
        >
          <Image
            source={require('../../assets/imgs/new.png')}
            style={styles.logoImage}
            resizeMode="contain"
          />
        </Animated.View>
      </View>

      {/* ── Divider line ── */}
      <Animated.View style={[styles.divider, { opacity: contentFade }]} />

      {/* ── Bottom content: title → subtitle → progress ── */}
      <Animated.View
        style={[
          styles.bottomContent,
          {
            opacity: contentFade,
            transform: [{ translateY: contentSlide }],
          },
        ]}
      >
        <Text style={styles.appTitle}>{title}</Text>
        <Text style={styles.appSubtitle}>{subtitle}</Text>

        {/* Progress bar */}
        <View style={styles.progressTrack}>
          <Animated.View style={[styles.progressFill, { width: progressWidth }]} />
        </View>

        {/* Poweredby footer */}
        <Text style={styles.footer}>
          {isSplash ? 'Government of Khyber Pakhtunkhwa' : 'Water & Sanitation Services Peshawar'}
        </Text>
      </Animated.View>

    </Animated.View>
  );
};

const styles = StyleSheet.create({
  container: {
    ...StyleSheet.absoluteFill,
    backgroundColor: '#2A4799',
    zIndex: 99999,
    alignItems: 'center',
    justifyContent: 'center',
  },

  /* ── Ambient glow orbs ── */
  glowTop: {
    position: 'absolute',
    top: -width * 0.5,
    left: -width * 0.3,
    width: width * 1.6,
    height: width * 1.6,
    borderRadius: width * 0.8,
    backgroundColor: 'rgba(170, 200, 255, 0.18)',
  },
  glowBottom: {
    position: 'absolute',
    bottom: -width * 0.55,
    right: -width * 0.3,
    width: width * 1.5,
    height: width * 1.5,
    borderRadius: width * 0.75,
    backgroundColor: 'rgba(8, 20, 70, 0.5)',
  },
  glowCentre: {
    position: 'absolute',
    width: 260,
    height: 260,
    borderRadius: 130,
    backgroundColor: 'rgba(2, 150, 230, 0.12)',
  },

  /* ── Logo zone ── */
  logoZone: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 8,
  },

  ring: {
    position: 'absolute',
    borderWidth: 1.5,
  },

  // Soft cyan glow circle sits behind the logo
  logoGlow: {
    position: 'absolute',
    backgroundColor: 'rgba(2, 160, 240, 0.13)',
    shadowColor: '#02ADF5',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.55,
    shadowRadius: 40,
    elevation: 0,
  },

  // Logo itself — no background, no border, floats on the bg
  logoImage: {
    width: '100%',
    height: '100%',
  },

  /* ── Divider ── */
  divider: {
    width: 50,
    height: 1,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    borderRadius: 1,
    marginBottom: 20,
  },

  /* ── Bottom text block ── */
  bottomContent: {
    alignItems: 'center',
    paddingHorizontal: 28,
    paddingBottom: 56,
    width: '100%',
  },

  appTitle: {
    fontSize: 26,
    fontWeight: '900',
    color: '#FFFFFF',
    letterSpacing: 1.4,
    textAlign: 'center',
    textShadowColor: 'rgba(0,0,0,0.28)',
    textShadowOffset: { width: 0, height: 2 },
    textShadowRadius: 8,
  },
  appSubtitle: {
    fontSize: 13,
    color: '#C5DBFF',
    fontWeight: '600',
    marginTop: 7,
    textAlign: 'center',
    letterSpacing: 0.3,
    lineHeight: 19,
  },

  /* ── Progress bar ── */
  progressTrack: {
    width: 120,
    height: 3,
    borderRadius: 2,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    marginTop: 22,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#38BDF8',
    borderRadius: 2,
  },

  footer: {
    marginTop: 16,
    fontSize: 11,
    color: 'rgba(180, 210, 255, 0.65)',
    fontWeight: '500',
    letterSpacing: 0.3,
    textAlign: 'center',
  },
});
