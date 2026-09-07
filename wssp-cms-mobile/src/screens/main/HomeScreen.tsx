import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  SafeAreaView,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { Colors, Spacing, BorderRadius, Typography } from '../../constants/theme';
import { WSSPHeader } from '../../components/common/WSSPHeader';
import { StatusBadge } from '../../components/common/StatusBadge';
import { WSSPButton } from '../../components/common/WSSPButton';
import { useAuth } from '../../store/AuthContext';
import { AuthApi } from '../../api/auth';
import { Ionicons } from '@expo/vector-icons';

export const HomeScreen: React.FC = () => {
  const { user, logout } = useAuth();
  const [securityData, setSecurityData] = useState<any>(null);
  const [loadingSecurity, setLoadingSecurity] = useState<boolean>(false);

  // Auto-fetch server-side security stats on load
  useEffect(() => {
    fetchSecurityStats();
  }, []);

  const fetchSecurityStats = async () => {
    setLoadingSecurity(true);
    try {
      const data = await AuthApi.testSecurity();
      setSecurityData(data);
    } catch (err) {
      console.warn('[HomeScreen] Failed to load security stats:', err);
    } finally {
      setLoadingSecurity(false);
    }
  };

  if (!user) return null;

  return (
    <SafeAreaView style={styles.safeArea}>
      <WSSPHeader />
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Officer Welcome Card */}
        <View style={styles.welcomeCard}>
          <View style={styles.welcomeRow}>
            <View style={styles.avatar}>
              <Text style={styles.avatarText}>
                {user.full_name.charAt(0).toUpperCase()}
              </Text>
            </View>
            <View style={styles.welcomeTextColumn}>
              <Text style={styles.greetingText}>Welcome Back,</Text>
              <Text style={styles.officerNameText}>{user.full_name}</Text>
              <Text style={styles.roleSubtext}>{user.role}</Text>
            </View>
          </View>
        </View>

        {/* Permitted Zones Card */}
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Ionicons name="map-outline" size={20} color={Colors.primary} />
            <Text style={styles.cardTitle}>Assigned Operational Zones</Text>
          </View>
          <Text style={styles.cardDescription}>
            Server-side security restricts your visibility to these designated locations:
          </Text>
          <View style={styles.zonesRow}>
            {user.allowed_locations.map((loc) => (
              <StatusBadge key={loc.id} status={loc.name} style={styles.zoneBadge} />
            ))}
          </View>
        </View>

        {/* Live Server-Side Security Verification */}
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Ionicons name="shield-checkmark" size={20} color={Colors.status.resolved} />
            <Text style={styles.cardTitle}>Live Django Security Scope</Text>
          </View>
          <Text style={styles.cardDescription}>
            Active enforcement query evaluated on Django backend:
          </Text>

          {loadingSecurity ? (
            <ActivityIndicator size="small" color={Colors.primary} style={{ marginVertical: 20 }} />
          ) : securityData ? (
            <View style={styles.statsContainer}>
              <View style={styles.statBox}>
                <Text style={styles.statNumber}>
                  {securityData.scoped_stats.total_accessible_complaints.toLocaleString()}
                </Text>
                <Text style={styles.statLabel}>Total in Scope</Text>
              </View>

              <View style={[styles.statBox, styles.statBoxPending]}>
                <Text style={[styles.statNumber, { color: Colors.status.pending }]}>
                  {securityData.scoped_stats.pending_accessible.toLocaleString()}
                </Text>
                <Text style={styles.statLabel}>Pending</Text>
              </View>

              <View style={[styles.statBox, styles.statBoxResolved]}>
                <Text style={[styles.statNumber, { color: Colors.status.resolved }]}>
                  {securityData.scoped_stats.resolved_accessible.toLocaleString()}
                </Text>
                <Text style={styles.statLabel}>Resolved</Text>
              </View>
            </View>
          ) : null}

          <WSSPButton
            title="Refresh Server Security Scope"
            variant="secondary"
            onPress={fetchSecurityStats}
            loading={loadingSecurity}
            style={styles.refreshBtn}
          />
        </View>

        {/* CMS Action Modules (Ready for Next Phases) */}
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Ionicons name="grid-outline" size={20} color={Colors.primary} />
            <Text style={styles.cardTitle}>CMS Operations</Text>
          </View>
          <View style={styles.actionGrid}>
            <TouchableOpacity style={styles.actionTile} activeOpacity={0.8}>
              <View style={[styles.tileIcon, { backgroundColor: '#DCFCE7' }]}>
                <Ionicons name="add-circle" size={26} color={Colors.primary} />
              </View>
              <Text style={styles.tileTitle}>Register Complaint</Text>
              <Text style={styles.tileDesc}>New citizen intake</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.actionTile} activeOpacity={0.8}>
              <View style={[styles.tileIcon, { backgroundColor: '#FEF3C7' }]}>
                <Ionicons name="list-outline" size={26} color={Colors.status.pending} />
              </View>
              <Text style={styles.tileTitle}>View Directory</Text>
              <Text style={styles.tileDesc}>Inspect complaints</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.actionTile} activeOpacity={0.8}>
              <View style={[styles.tileIcon, { backgroundColor: '#E0F2FE' }]}>
                <Ionicons name="checkmark-done-circle" size={26} color={Colors.secondary} />
              </View>
              <Text style={styles.tileTitle}>Resolve Complaint</Text>
              <Text style={styles.tileDesc}>Submit after-photo</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.actionTile} activeOpacity={0.8}>
              <View style={[styles.tileIcon, { backgroundColor: '#F3E8FF' }]}>
                <Ionicons name="call" size={26} color="#7E22CE" />
              </View>
              <Text style={styles.tileTitle}>1334 Follow-up</Text>
              <Text style={styles.tileDesc}>Citizen feedback</Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  scrollContent: {
    padding: Spacing.md,
    paddingBottom: Spacing.xxl,
  },
  welcomeCard: {
    backgroundColor: Colors.surface,
    padding: Spacing.md,
    borderRadius: BorderRadius.lg,
    marginBottom: Spacing.md,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  welcomeRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatar: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: Colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: Spacing.md,
  },
  avatarText: {
    color: Colors.textInverse,
    fontSize: Typography.fontSize.xl,
    fontWeight: '800',
  },
  welcomeTextColumn: {
    flex: 1,
  },
  greetingText: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textMuted,
    fontWeight: '600',
    textTransform: 'uppercase',
  },
  officerNameText: {
    fontSize: Typography.fontSize.lg,
    fontWeight: '800',
    color: Colors.textPrimary,
  },
  roleSubtext: {
    fontSize: Typography.fontSize.xs,
    color: Colors.primary,
    fontWeight: '700',
  },
  card: {
    backgroundColor: Colors.surface,
    padding: Spacing.md,
    borderRadius: BorderRadius.lg,
    marginBottom: Spacing.md,
    borderWidth: 1,
    borderColor: Colors.border,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04,
    shadowRadius: 6,
    elevation: 1,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 6,
  },
  cardTitle: {
    fontSize: Typography.fontSize.md,
    fontWeight: '700',
    color: Colors.textPrimary,
    marginLeft: Spacing.xs,
  },
  cardDescription: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textSecondary,
    marginBottom: Spacing.md,
  },
  zonesRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: Spacing.sm,
  },
  zoneBadge: {
    marginBottom: 4,
  },
  statsContainer: {
    flexDirection: 'row',
    gap: Spacing.sm,
    marginBottom: Spacing.md,
  },
  statBox: {
    flex: 1,
    backgroundColor: '#F8FAFC',
    padding: Spacing.md,
    borderRadius: BorderRadius.md,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: Colors.border,
  },
  statBoxPending: {
    backgroundColor: '#FFFBEB',
    borderColor: '#FDE68A',
  },
  statBoxResolved: {
    backgroundColor: '#F0FDF4',
    borderColor: '#BBF7D0',
  },
  statNumber: {
    fontSize: Typography.fontSize.lg,
    fontWeight: '800',
    color: Colors.textPrimary,
  },
  statLabel: {
    fontSize: 11,
    fontWeight: '600',
    color: Colors.textSecondary,
    marginTop: 2,
  },
  refreshBtn: {
    height: 42,
  },
  actionGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: Spacing.sm,
  },
  actionTile: {
    width: '48%',
    backgroundColor: '#F8FAFC',
    padding: Spacing.md,
    borderRadius: BorderRadius.md,
    borderWidth: 1,
    borderColor: Colors.border,
    marginBottom: Spacing.xs,
  },
  tileIcon: {
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: Spacing.sm,
  },
  tileTitle: {
    fontSize: Typography.fontSize.sm,
    fontWeight: '700',
    color: Colors.textPrimary,
  },
  tileDesc: {
    fontSize: 11,
    color: Colors.textMuted,
    marginTop: 2,
  },
});
