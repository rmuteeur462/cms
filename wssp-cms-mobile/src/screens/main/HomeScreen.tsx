import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  ActivityIndicator,
  Linking,
} from 'react-native';
import { Colors, Spacing, BorderRadius, Typography } from '../../constants/theme';
import { StatCard } from '../../components/common/StatCard';
import { useAuth } from '../../store/AuthContext';
import { ComplaintsApi, DashboardData } from '../../api/complaints';
import { Ionicons } from '@expo/vector-icons';

interface HomeScreenProps {
  navigation?: any;
}

export const HomeScreen: React.FC<HomeScreenProps> = ({ navigation }) => {
  const { user } = useAuth();

  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 17) return 'Good Afternoon';
    return 'Good Evening';
  };

  const loadDashboardData = async () => {
    try {
      const data = await ComplaintsApi.getDashboard();
      setDashboard(data);
    } catch (err) {
      console.warn('[HomeScreen] Failed to load dashboard:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    loadDashboardData();
  }, []);

  return (
    <View style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={[Colors.primary]} />
        }
      >
        {/* Officer Greeting Header */}
        <View style={styles.greetingHeader}>
          <Text style={styles.greetingText}>{getGreeting()}</Text>
          <Text style={styles.sectionSubtitle}>Complaint Management</Text>
          <Text style={styles.officerNameText}>
            {user?.full_name || user?.username} •{' '}
            <Text style={styles.officerRoleText}>{user?.role || 'Departmental Officer'}</Text>
          </Text>
        </View>

        {/* Loading indicator */}
        {loading && (
          <View style={styles.statsHeaderRow}>
            <ActivityIndicator size="small" color={Colors.primary} />
          </View>
        )}

        {/* 2x2 Metric Cards Grid */}
        <View style={styles.gridContainer}>
          <View style={styles.gridRow}>
            <StatCard
              title="Total Complaints"
              value={dashboard?.metrics.total ?? (loading ? '...' : 0)}
              icon="layers-outline"
              color={Colors.primary}
              bgColor="#DCFCE7"
              onPress={() => navigation?.navigate('Complaints')}
            />
            <View style={{ width: Spacing.md }} />
            <StatCard
              title="Pending Issues"
              value={dashboard?.metrics.pending ?? (loading ? '...' : 0)}
              icon="time-outline"
              color={Colors.status.pending}
              bgColor={Colors.status.pendingBg}
              onPress={() => navigation?.navigate('Complaints', { status: 'pending' })}
            />
          </View>

          <View style={[styles.gridRow, { marginTop: Spacing.md }]}>
            <StatCard
              title="Resolved"
              value={dashboard?.metrics.resolved ?? (loading ? '...' : 0)}
              icon="checkmark-circle-outline"
              color={Colors.status.resolved}
              bgColor={Colors.status.resolvedBg}
              onPress={() => navigation?.navigate('Complaints', { status: 'resolved' })}
            />
            <View style={{ width: Spacing.md }} />
            <StatCard
              title="Registered Today"
              value={dashboard?.metrics.today ?? (loading ? '...' : 0)}
              icon="calendar-outline"
              color={Colors.secondary}
              bgColor="#E0F2FE"
              onPress={() => navigation?.navigate('Complaints')}
            />
          </View>
        </View>

        {/* Quick Departmental Utilities */}
        <View style={styles.servicesContainer}>
          <Text style={styles.servicesTitle}>Quick Navigation</Text>

          <View style={styles.serviceRow}>
            <TouchableOpacity
              style={styles.serviceCard}
              onPress={() => navigation?.navigate('Complaints')}
              activeOpacity={0.75}
            >
              <View style={[styles.serviceIconCircle, { backgroundColor: '#F0FDF4' }]}>
                <Ionicons name="folder-open" size={22} color={Colors.primary} />
              </View>
              <Text style={styles.serviceCardTitle}>Complaint Directory</Text>
              <Text style={styles.serviceCardSubtitle}>Search & filter all cases</Text>
            </TouchableOpacity>

            <View style={{ width: Spacing.md }} />

            <TouchableOpacity
              style={styles.serviceCard}
              onPress={() => navigation?.navigate('Reports')}
              activeOpacity={0.75}
            >
              <View style={[styles.serviceIconCircle, { backgroundColor: '#EFF6FF' }]}>
                <Ionicons name="pie-chart" size={22} color={Colors.secondary} />
              </View>
              <Text style={styles.serviceCardTitle}>Analytics & Reports</Text>
              <Text style={styles.serviceCardSubtitle}>Zonal & type statistics</Text>
            </TouchableOpacity>
          </View>

          {/* Helpline 1334 banner */}
          <TouchableOpacity
            style={styles.helplineBanner}
            onPress={() => Linking.openURL('tel:1334')}
            activeOpacity={0.8}
          >
            <View style={styles.helplineLeft}>
              <View style={styles.helplineIconBox}>
                <Ionicons name="call" size={18} color="#FFFFFF" />
              </View>
              <View>
                <Text style={styles.helplineTitle}>WSSP Citizen Toll-Free Helpline</Text>
                <Text style={styles.helplineSubtitle}>Dial 1334 for immediate public inquiries</Text>
              </View>
            </View>
            <View style={styles.helplineNumberBadge}>
              <Text style={styles.helplineNumberText}>1334</Text>
            </View>
          </TouchableOpacity>
        </View>
      </ScrollView>

      {/* Floating Plus Sign Button on Front Page */}
      <TouchableOpacity
        style={styles.floatingAddButton}
        onPress={() => navigation?.navigate('NewComplaint')}
        activeOpacity={0.85}
      >
        <Ionicons name="add" size={32} color="#FFFFFF" />
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  scrollContent: {
    paddingBottom: 90, // extra clearance for floating button & bottom tabs
  },
  greetingHeader: {
    paddingHorizontal: Spacing.md,
    paddingTop: Spacing.lg,
    paddingBottom: Spacing.xs,
  },
  greetingText: {
    fontSize: Typography.fontSize.xs,
    fontWeight: '800',
    color: '#64748B',
    textTransform: 'uppercase',
    letterSpacing: 1.2,
  },
  sectionSubtitle: {
    fontSize: Typography.fontSize.xxl,
    fontWeight: '900',
    color: Colors.textPrimary,
    letterSpacing: -0.5,
    marginTop: 2,
  },
  officerNameText: {
    fontSize: Typography.fontSize.sm,
    color: Colors.primary,
    fontWeight: '700',
    marginTop: 2,
  },
  officerRoleText: {
    color: Colors.textSecondary,
    fontWeight: '500',
  },

  // KPI Section
  statsHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: Spacing.md,
    marginBottom: Spacing.sm,
  },
  statsHeaderTitle: {
    fontSize: Typography.fontSize.sm,
    fontWeight: '800',
    color: Colors.textSecondary,
    textTransform: 'uppercase',
    letterSpacing: 0.8,
  },
  gridContainer: {
    paddingHorizontal: Spacing.md,
    marginBottom: Spacing.md,
  },
  gridRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },

  // Quick Services Section
  servicesContainer: {
    paddingHorizontal: Spacing.md,
  },
  servicesTitle: {
    fontSize: Typography.fontSize.sm,
    fontWeight: '800',
    color: Colors.textSecondary,
    textTransform: 'uppercase',
    letterSpacing: 0.8,
    marginBottom: Spacing.sm,
  },
  serviceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: Spacing.md,
  },
  serviceCard: {
    flex: 1,
    backgroundColor: Colors.surface,
    padding: Spacing.md,
    borderRadius: BorderRadius.lg,
    borderWidth: 1,
    borderColor: Colors.border,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.03,
    shadowRadius: 6,
    elevation: 1,
  },
  serviceIconCircle: {
    width: 42,
    height: 42,
    borderRadius: 21,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: Spacing.sm,
  },
  serviceCardTitle: {
    fontSize: Typography.fontSize.sm,
    fontWeight: '700',
    color: Colors.textPrimary,
  },
  serviceCardSubtitle: {
    fontSize: 11,
    color: Colors.textMuted,
    marginTop: 2,
  },

  // Helpline 1334
  helplineBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#0F172A',
    paddingVertical: 12,
    paddingHorizontal: Spacing.md,
    borderRadius: BorderRadius.lg,
    marginTop: Spacing.xs,
  },
  helplineLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  helplineIconBox: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#334155',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: Spacing.sm,
  },
  helplineTitle: {
    fontSize: 12,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  helplineSubtitle: {
    fontSize: 10,
    color: '#94A3B8',
  },
  helplineNumberBadge: {
    backgroundColor: Colors.accent,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: BorderRadius.full,
  },
  helplineNumberText: {
    fontSize: 12,
    fontWeight: '900',
    color: '#000000',
  },

  // Floating Plus Button (Circle)
  floatingAddButton: {
    position: 'absolute',
    bottom: 24,
    right: 20,
    width: 56,
    height: 56,
    borderRadius: 28,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: Colors.primary,
    shadowColor: Colors.primaryDark,
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.35,
    shadowRadius: 8,
    elevation: 8,
    borderWidth: 2,
    borderColor: '#34D399',
  },
});
