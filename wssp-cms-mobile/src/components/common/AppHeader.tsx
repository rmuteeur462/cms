import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView, Platform } from 'react-native';
import { Colors, Spacing, BorderRadius, Typography } from '../../constants/theme';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../store/AuthContext';

interface AppHeaderProps {
  title?: string;
  onNotificationPress?: () => void;
  onProfilePress?: () => void;
}

export const AppHeader: React.FC<AppHeaderProps> = ({
  title = 'WSSP CMS',
  onNotificationPress,
  onProfilePress,
}) => {
  const { user } = useAuth();

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.header}>
        {/* Left Branding */}
        <View style={styles.leftSection}>
          <View style={styles.emblemBadge}>
            <Ionicons name="water" size={20} color={Colors.accent} />
          </View>
          <View>
            <Text style={styles.titleText}>{title}</Text>
            <Text style={styles.deptText}>Peshawar Municipality</Text>
          </View>
        </View>

        {/* Right Actions: 🔔 Notifications & 👤 Profile */}
        <View style={styles.rightSection}>
          <TouchableOpacity
            style={styles.actionBtn}
            onPress={onNotificationPress}
            activeOpacity={0.7}
            accessibilityLabel="Notifications"
          >
            <Ionicons name="notifications-outline" size={20} color={Colors.textInverse} />
            <View style={styles.notiBadge}>
              <Text style={styles.notiBadgeText}>3</Text>
            </View>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.avatarBtn}
            onPress={onProfilePress}
            activeOpacity={0.7}
            accessibilityLabel="Officer Profile"
          >
            <Text style={styles.avatarInitial}>
              {user?.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
            </Text>
          </TouchableOpacity>
        </View>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    backgroundColor: Colors.primaryDark,
  },
  header: {
    backgroundColor: Colors.primaryDark,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: Spacing.md,
    paddingTop: Platform.OS === 'android' ? 32 : Spacing.sm,
    paddingBottom: Spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.1)',
  },
  leftSection: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  emblemBadge: {
    width: 34,
    height: 34,
    borderRadius: 17,
    backgroundColor: 'rgba(255, 255, 255, 0.15)',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: Spacing.sm,
    borderWidth: 1.2,
    borderColor: Colors.accent,
  },
  titleText: {
    fontSize: Typography.fontSize.md,
    fontWeight: '900',
    color: Colors.textInverse,
    letterSpacing: 0.5,
  },
  deptText: {
    fontSize: 10,
    color: 'rgba(255, 255, 255, 0.75)',
    fontWeight: '600',
  },
  rightSection: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
  },
  actionBtn: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: 'rgba(255, 255, 255, 0.12)',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
  },
  notiBadge: {
    position: 'absolute',
    top: 4,
    right: 4,
    backgroundColor: Colors.accent,
    width: 14,
    height: 14,
    borderRadius: 7,
    alignItems: 'center',
    justifyContent: 'center',
  },
  notiBadgeText: {
    fontSize: 9,
    fontWeight: '900',
    color: Colors.primaryDark,
  },
  avatarBtn: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: Colors.accent,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarInitial: {
    fontSize: Typography.fontSize.sm,
    fontWeight: '800',
    color: Colors.primaryDark,
  },
});
