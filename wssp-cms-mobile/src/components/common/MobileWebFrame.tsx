import React from 'react';
import { View, StyleSheet, Platform, useWindowDimensions, Text } from 'react-native';
import { Colors } from '../../constants/theme';
import { Ionicons } from '@expo/vector-icons';

interface MobileWebFrameProps {
  children: React.ReactNode;
}

export const MobileWebFrame: React.FC<MobileWebFrameProps> = ({ children }) => {
  const { width, height } = useWindowDimensions();

  // If on a real mobile device OR browser resized to mobile width (DevTools)
  if (Platform.OS !== 'web' || width <= 520) {
    return <View style={styles.nativeContainer}>{children}</View>;
  }

  const phoneHeight = Math.min(height * 0.94, 860);

  // Desktop Web Preview: render realistic mobile device mockup
  return (
    <View style={styles.webBackdrop}>
      {/* Top Device Header Bar */}
      <View style={styles.desktopBar}>
        <View style={styles.desktopBrand}>
          <Ionicons name="phone-portrait-outline" size={18} color="#94A3B8" style={{ marginRight: 6 }} />
          <Text style={styles.desktopTitle}>WSSP CMS Mobile App</Text>
        </View>
        <View style={styles.desktopInfoPill}>
          <Text style={styles.desktopInfoText}>Mobile Viewport (412 × {Math.round(phoneHeight)})</Text>
        </View>
      </View>

      {/* Phone Chassis */}
      <View style={[styles.phoneChassis, { height: phoneHeight }]}>
        {/* Dynamic Island / Speaker Pill */}
        <View style={styles.dynamicIslandContainer}>
          <View style={styles.dynamicIslandPill}>
            <View style={styles.cameraLens} />
          </View>
        </View>

        {/* Inner Phone Screen */}
        <View style={styles.phoneScreen}>
          {children}
        </View>

        {/* Bottom Home Indicator Bar */}
        <View style={styles.homeIndicatorBar}>
          <View style={styles.homeIndicatorPill} />
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  nativeContainer: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  webBackdrop: {
    flex: 1,
    width: '100%',
    height: '100%',
    backgroundColor: '#0F172A', // Dark Slate backdrop
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
  },
  desktopBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    width: 412,
    marginBottom: 10,
    paddingHorizontal: 4,
  },
  desktopBrand: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  desktopTitle: {
    color: '#CBD5E1',
    fontSize: 13,
    fontWeight: '700',
    letterSpacing: 0.3,
  },
  desktopInfoPill: {
    backgroundColor: '#1E293B',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#334155',
  },
  desktopInfoText: {
    color: '#94A3B8',
    fontSize: 11,
    fontWeight: '600',
  },
  phoneChassis: {
    width: 412,
    backgroundColor: '#000000',
    borderRadius: 46,
    borderWidth: 10,
    borderColor: '#1E293B',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 25 },
    shadowOpacity: 0.65,
    shadowRadius: 45,
    elevation: 24,
    overflow: 'hidden',
    position: 'relative',
  },
  dynamicIslandContainer: {
    position: 'absolute',
    top: 6,
    left: 0,
    right: 0,
    zIndex: 9999,
    alignItems: 'center',
  },
  dynamicIslandPill: {
    width: 104,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#000000',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-end',
    paddingRight: 10,
  },
  cameraLens: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: '#111827',
    borderWidth: 1,
    borderColor: '#1F2937',
  },
  phoneScreen: {
    flex: 1,
    backgroundColor: Colors.background,
    overflow: 'hidden',
  },
  homeIndicatorBar: {
    height: 14,
    backgroundColor: Colors.surface,
    alignItems: 'center',
    justifyContent: 'center',
  },
  homeIndicatorPill: {
    width: 120,
    height: 4,
    borderRadius: 2,
    backgroundColor: '#CBD5E1',
  },
});
