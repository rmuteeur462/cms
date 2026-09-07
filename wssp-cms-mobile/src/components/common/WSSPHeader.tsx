import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView } from 'react-native';
import { Colors, Spacing, BorderRadius, Typography } from '../../constants/theme';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../store/AuthContext';

interface WSSPHeaderProps {
  title?: string;
  subtitle?: string;
  showOfficerBadge?: boolean;
  onLogoutPress?: () => void;
}

export const WSSPHeader: React.FC<WSSPHeaderProps> = ({
  title = 'WSSP CMS',
  subtitle = 'Complaint Management System',
  showOfficerBadge = true,
}) => {
  const { user, logout } = useAuth();

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        <View style={styles.brandingRow}>
          <View style={styles.logoBadge}>
            <Ionicons name="shield-checkmark" size={24} color={Colors.accent} />
          </View>
          <View style={styles.titleColumn}>
            <Text style={styles.titleText}>{title}</Text>
            <Text style={styles.subtitleText}>{subtitle}</Text>
          </View>
          {user && (
            <TouchableOpacity
              style={styles.logoutBtn}
              onPress={logout}
              activeOpacity={0.7}
              accessibilityLabel="Log out"
            >
              <Ionicons name="log-out-outline" size={22} color={Colors.textInverse} />
            </TouchableOpacity>
          )}
        </View>

        {showOfficerBadge && user && (
          <View style={styles.officerBar}>
            <View style={styles.officerInfo}>
              <Ionicons name="person-circle-outline" size={18} color={Colors.accent} style={{ marginRight: 6 }} />
              <Text style={styles.officerName} numberOfLines={1}>
                {user.full_name}
              </Text>
            </View>
            <View style={styles.roleBadge}>
              <Text style={styles.roleText} numberOfLines={1}>
                {user.role}
              </Text>
            </View>
          </View>
        )}
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    backgroundColor: Colors.primaryDark,
  },
  container: {
    backgroundColor: Colors.primaryDark,
    paddingHorizontal: Spacing.md,
    paddingTop: Spacing.sm,
    paddingBottom: Spacing.md,
    borderBottomLeftRadius: BorderRadius.lg,
    borderBottomRightRadius: BorderRadius.lg,
  },
  brandingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  logoBadge: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.12)',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: Spacing.sm,
  },
  titleColumn: {
    flex: 1,
  },
  titleText: {
    fontSize: Typography.fontSize.lg,
    fontWeight: '800',
    color: Colors.textInverse,
    letterSpacing: 0.5,
  },
  subtitleText: {
    fontSize: Typography.fontSize.xs,
    color: 'rgba(255, 255, 255, 0.75)',
    fontWeight: '500',
  },
  logoutBtn: {
    padding: Spacing.sm,
    backgroundColor: 'rgba(255, 255, 255, 0.12)',
    borderRadius: BorderRadius.full,
    marginLeft: Spacing.sm,
  },
  officerBar: {
    marginTop: Spacing.sm,
    paddingTop: Spacing.sm,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255, 255, 255, 0.15)',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  officerInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    marginRight: Spacing.sm,
  },
  officerName: {
    color: Colors.textInverse,
    fontSize: Typography.fontSize.sm,
    fontWeight: '600',
  },
  roleBadge: {
    backgroundColor: Colors.accent,
    paddingHorizontal: Spacing.sm,
    paddingVertical: 3,
    borderRadius: BorderRadius.full,
  },
  roleText: {
    color: Colors.primaryDark,
    fontSize: Typography.fontSize.xs,
    fontWeight: '800',
    textTransform: 'uppercase',
  },
});
