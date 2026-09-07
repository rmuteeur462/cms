import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { Colors, Spacing, BorderRadius, Typography } from '../../constants/theme';
import { StatusBadge } from '../../components/common/StatusBadge';
import { WSSPButton } from '../../components/common/WSSPButton';
import { useAuth } from '../../store/AuthContext';
import { Config } from '../../constants/config';
import { Ionicons } from '@expo/vector-icons';

export const ProfileScreen: React.FC = () => {
  const { user, logout } = useAuth();

  const handleLogoutConfirm = () => {
    Alert.alert(
      'Sign Out',
      'Are you sure you want to sign out of the WSSP CMS portal?',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Sign Out', style: 'destructive', onPress: logout },
      ]
    );
  };

  if (!user) return null;

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Officer Profile Card */}
      <View style={styles.profileCard}>
        <View style={styles.avatarLarge}>
          <Text style={styles.avatarLargeText}>
            {user.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
          </Text>
        </View>
        <Text style={styles.userName}>{user.full_name}</Text>
        <Text style={styles.userUsername}>@{user.username}</Text>
        
        <View style={styles.roleChip}>
          <Ionicons name="shield-checkmark" size={14} color={Colors.primaryDark} style={{ marginRight: 4 }} />
          <Text style={styles.roleChipText}>{user.role}</Text>
        </View>
      </View>

      {/* Account Particulars */}
      <View style={styles.card}>
        <Text style={styles.cardHeaderTitle}>Account Particulars</Text>
        
        <View style={styles.row}>
          <Text style={styles.rowLabel}>Officer ID:</Text>
          <Text style={styles.rowValue}>#EMP-{user.id}</Text>
        </View>

        <View style={styles.row}>
          <Text style={styles.rowLabel}>Email Address:</Text>
          <Text style={styles.rowValue}>{user.email || 'officer@wssp.gov.pk'}</Text>
        </View>

        <View style={styles.row}>
          <Text style={styles.rowLabel}>Superuser Access:</Text>
          <Text style={[styles.rowValue, { color: user.is_superuser ? Colors.status.resolved : Colors.textSecondary }]}>
            {user.is_superuser ? 'Yes (Admin)' : 'Standard Officer'}
          </Text>
        </View>

        <View style={styles.row}>
          <Text style={styles.rowLabel}>Account Status:</Text>
          <Text style={[styles.rowValue, { color: Colors.status.resolved }]}>Active & Verified</Text>
        </View>
      </View>

      {/* Allowed Jurisdictions */}
      <View style={styles.card}>
        <Text style={styles.cardHeaderTitle}>Allowed Operational Zones</Text>
        <Text style={styles.cardDescription}>
          Your credentials strictly permit access to the following municipal zones:
        </Text>
        <View style={styles.zonesRow}>
          {user.allowed_locations.map((loc) => (
            <StatusBadge key={loc.id} status={loc.name} style={{ marginBottom: 4 }} />
          ))}
        </View>
      </View>

      {/* Department System Info */}
      <View style={styles.card}>
        <Text style={styles.cardHeaderTitle}>Department Information</Text>
        
        <View style={styles.row}>
          <Text style={styles.rowLabel}>Department:</Text>
          <Text style={styles.rowValue}>WSSP Peshawar</Text>
        </View>

        <View style={styles.row}>
          <Text style={styles.rowLabel}>Toll-Free Helpline:</Text>
          <Text style={[styles.rowValue, { color: Colors.primary, fontWeight: '800' }]}>1334</Text>
        </View>

        <View style={styles.row}>
          <Text style={styles.rowLabel}>Software Version:</Text>
          <Text style={styles.rowValue}>{Config.APP_VERSION}</Text>
        </View>

        <View style={styles.row}>
          <Text style={styles.rowLabel}>API Host:</Text>
          <Text style={styles.rowValue}>{Config.BASE_URL}</Text>
        </View>
      </View>

      {/* Logout Action */}
      <WSSPButton
        title="Sign Out from CMS"
        variant="danger"
        icon={<Ionicons name="log-out-outline" size={18} color={Colors.textInverse} />}
        onPress={handleLogoutConfirm}
        style={styles.logoutBtn}
      />
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  content: {
    padding: Spacing.md,
    paddingBottom: Spacing.xxl,
  },
  profileCard: {
    backgroundColor: Colors.surface,
    padding: Spacing.xl,
    borderRadius: BorderRadius.lg,
    alignItems: 'center',
    marginBottom: Spacing.md,
    borderWidth: 1,
    borderColor: Colors.border,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  avatarLarge: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: Colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: Spacing.sm,
    borderWidth: 3,
    borderColor: '#DCFCE7',
  },
  avatarLargeText: {
    color: Colors.textInverse,
    fontSize: 28,
    fontWeight: '900',
  },
  userName: {
    fontSize: Typography.fontSize.xl,
    fontWeight: '900',
    color: Colors.textPrimary,
  },
  userUsername: {
    fontSize: Typography.fontSize.sm,
    color: Colors.textMuted,
    marginTop: 2,
  },
  roleChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.accent,
    paddingHorizontal: 12,
    paddingVertical: 5,
    borderRadius: BorderRadius.full,
    marginTop: Spacing.sm,
  },
  roleChipText: {
    color: Colors.primaryDark,
    fontSize: 11,
    fontWeight: '800',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  card: {
    backgroundColor: Colors.surface,
    padding: Spacing.md,
    borderRadius: BorderRadius.lg,
    marginBottom: Spacing.md,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  cardHeaderTitle: {
    fontSize: Typography.fontSize.xs,
    fontWeight: '800',
    color: Colors.textMuted,
    textTransform: 'uppercase',
    letterSpacing: 0.8,
    marginBottom: Spacing.sm,
  },
  cardDescription: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textSecondary,
    marginBottom: Spacing.sm,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 6,
    borderBottomWidth: 1,
    borderBottomColor: '#F8FAFC',
  },
  rowLabel: {
    fontSize: Typography.fontSize.sm,
    color: Colors.textSecondary,
    fontWeight: '500',
  },
  rowValue: {
    fontSize: Typography.fontSize.sm,
    color: Colors.textPrimary,
    fontWeight: '700',
  },
  zonesRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: Spacing.xs,
    marginTop: Spacing.xs,
  },
  logoutBtn: {
    marginVertical: Spacing.md,
  },
});
