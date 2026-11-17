import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
  Linking,
  Image,
} from 'react-native';
import { useAuth } from '../../store/AuthContext';
import { CitizenComplaintsApi, CitizenDashboardData, CitizenComplaintItem } from '../../api/complaints';
import { Colors, Typography, Spacing, BorderRadius } from '../../constants/theme';
import { Ionicons } from '@expo/vector-icons';

interface CitizenHomeScreenProps {
  navigation: any;
}

export const CitizenHomeScreen: React.FC<CitizenHomeScreenProps> = ({ navigation }) => {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState<CitizenDashboardData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);

  const fetchDashboard = useCallback(async () => {
    try {
      const data = await CitizenComplaintsApi.getDashboard();
      setDashboardData(data);
    } catch (err) {
      console.warn('[CitizenHomeScreen] Failed to fetch dashboard data:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  const onRefresh = () => {
    setRefreshing(true);
    fetchDashboard();
  };

  const handleCallHelpline = () => {
    Linking.openURL('tel:1334');
  };

  const displayName = dashboardData?.citizen?.full_name || user?.full_name || 'Citizen';

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.contentContainer}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={[Colors.primary]} />}
      showsVerticalScrollIndicator={false}
    >
      {/* 1. Header Banner & Welcome */}
      <View style={styles.headerCard}>
        <View style={styles.welcomeRow}>
          <View style={styles.welcomeTextGroup}>
            <Text style={styles.subGreeting}>WSSP Peshawar Citizen Portal</Text>
            <Text style={styles.citizenName}>Welcome, {displayName}</Text>
            <Text style={styles.citizenMobile}>{dashboardData?.citizen?.mobile_number || user?.username}</Text>
          </View>
          <Image
            source={require('../../assets/imgs/wssp_logo.png')}
            style={styles.headerLogo}
            resizeMode="contain"
          />
        </View>

        {/* Big Action: Register New Complaint */}
        <TouchableOpacity
          style={styles.primaryActionButton}
          onPress={() => navigation.navigate('NewComplaint')}
          activeOpacity={0.85}
        >
          <View style={styles.actionIconCircle}>
            <Ionicons name="add" size={26} color="#1E40AF" />
          </View>
          <View style={styles.actionTextGroup}>
            <Text style={styles.actionButtonTitle}>Register New Complaint</Text>
            <Text style={styles.actionButtonSubtitle}>Report waste, water supply, drainage or billing issue</Text>
          </View>
          <Ionicons name="chevron-forward" size={22} color="#FFFFFF" />
        </TouchableOpacity>
      </View>

      {/* 2. Complaints Status Metric Cards */}
      <View style={styles.sectionHeaderRow}>
        <Text style={styles.sectionTitle}>Overview</Text>
        <TouchableOpacity onPress={() => navigation.navigate('Complaints')}>
          <Text style={styles.viewAllText}>View All</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.metricsRow}>
        <TouchableOpacity
          style={[styles.metricCard, { borderTopColor: '#3B82F6' }]}
          onPress={() => navigation.navigate('Complaints')}
          activeOpacity={0.8}
        >
          <View style={[styles.metricIconWrap, { backgroundColor: '#EFF6FF' }]}>
            <Ionicons name="file-tray-full" size={20} color="#2563EB" />
          </View>
          <Text style={styles.metricNumber}>{dashboardData?.metrics?.total ?? 0}</Text>
          <Text style={styles.metricLabel}>Total Filed</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.metricCard, { borderTopColor: '#F59E0B' }]}
          onPress={() => navigation.navigate('Complaints', { status: 'pending' })}
          activeOpacity={0.8}
        >
          <View style={[styles.metricIconWrap, { backgroundColor: '#FFFBEB' }]}>
            <Ionicons name="time" size={20} color="#D97706" />
          </View>
          <Text style={[styles.metricNumber, { color: '#D97706' }]}>
            {dashboardData?.metrics?.pending ?? 0}
          </Text>
          <Text style={styles.metricLabel}>Pending Action</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.metricCard, { borderTopColor: '#10B981' }]}
          onPress={() => navigation.navigate('Complaints', { status: 'resolved' })}
          activeOpacity={0.8}
        >
          <View style={[styles.metricIconWrap, { backgroundColor: '#ECFDF5' }]}>
            <Ionicons name="checkmark-done" size={20} color="#059669" />
          </View>
          <Text style={[styles.metricNumber, { color: '#059669' }]}>
            {dashboardData?.metrics?.resolved ?? 0}
          </Text>
          <Text style={styles.metricLabel}>Resolved</Text>
        </TouchableOpacity>
      </View>

      {/* 3. Quick Assistance / Helpline Banner */}
      <View style={styles.helplineBanner}>
        <View style={styles.helplineLeft}>
          <View style={styles.helplineIconBox}>
            <Ionicons name="call" size={22} color="#FFFFFF" />
          </View>
          <View>
            <Text style={styles.helplineTitle}>WSSP Citizen Helpline</Text>
            <Text style={styles.helplineSubtitle}>Call toll-free for municipal emergencies</Text>
          </View>
        </View>
        <TouchableOpacity style={styles.callButton} onPress={handleCallHelpline} activeOpacity={0.8}>
          <Text style={styles.callButtonText}>1334</Text>
        </TouchableOpacity>
      </View>

      {/* 4. Recent Complaint Activity */}
      <View style={styles.sectionHeaderRow}>
        <Text style={styles.sectionTitle}>Recent Complaint Activity</Text>
        <TouchableOpacity onPress={() => navigation.navigate('Complaints')}>
          <Text style={styles.viewAllText}>See all ({dashboardData?.metrics?.total ?? 0})</Text>
        </TouchableOpacity>
      </View>

      {loading ? (
        <ActivityIndicator size="small" color={Colors.primary} style={{ marginVertical: Spacing.xl }} />
      ) : !dashboardData?.recent_complaints || dashboardData.recent_complaints.length === 0 ? (
        <View style={styles.emptyCard}>
          <Ionicons name="document-text-outline" size={42} color={Colors.textMuted} />
          <Text style={styles.emptyTitle}>No Complaints Yet</Text>
          <Text style={styles.emptySubtitle}>
            When you submit a municipal issue, its progress and resolution details will appear here.
          </Text>
          <TouchableOpacity
            style={styles.emptyButton}
            onPress={() => navigation.navigate('NewComplaint')}
          >
            <Text style={styles.emptyButtonText}>Submit First Complaint</Text>
          </TouchableOpacity>
        </View>
      ) : (
        dashboardData.recent_complaints.map((item: CitizenComplaintItem) => (
          <TouchableOpacity
            key={item.id}
            style={styles.complaintCard}
            onPress={() => navigation.navigate('Tracking', { complaintId: item.id })}
            activeOpacity={0.75}
          >
            <View style={styles.cardHeader}>
              <View style={styles.cardRefGroup}>
                <Text style={styles.refNumber}>{item.complaint_no}</Text>
                <Text style={styles.categoryBadge}>{item.category}</Text>
              </View>
              <View
                style={[
                  styles.statusBadge,
                  item.status === 'resolved' ? styles.statusBadgeResolved : styles.statusBadgePending,
                ]}
              >
                <Text
                  style={[
                    styles.statusBadgeText,
                    item.status === 'resolved' ? styles.statusTextResolved : styles.statusTextPending,
                  ]}
                >
                  {item.status === 'resolved' ? 'Resolved' : 'Pending'}
                </Text>
              </View>
            </View>

            <Text style={styles.cardTitle} numberOfLines={1}>
              {item.title || item.subcategory || item.category}
            </Text>
            <Text style={styles.cardDetail} numberOfLines={2}>
              {item.complaint_detail}
            </Text>

            <View style={styles.cardFooter}>
              <View style={styles.locationGroup}>
                <Ionicons name="location-outline" size={14} color={Colors.textMuted} />
                <Text style={styles.locationText} numberOfLines={1}>
                  {item.uc_name ? `${item.uc_name}, ${item.location_name}` : item.location_name}
                </Text>
              </View>
              <View style={styles.trackLinkGroup}>
                <Text style={styles.trackLink}>Track Status</Text>
                <Ionicons name="arrow-forward" size={14} color="#1E40AF" />
              </View>
            </View>
          </TouchableOpacity>
        ))
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  contentContainer: {
    paddingBottom: Spacing.xxl + 20,
  },
  headerCard: {
    backgroundColor: '#0F2744',
    paddingTop: 16,
    paddingBottom: 24,
    paddingHorizontal: Spacing.lg,
    borderBottomLeftRadius: 24,
    borderBottomRightRadius: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.12,
    shadowRadius: 10,
    elevation: 4,
  },
  welcomeRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  welcomeTextGroup: {
    flex: 1,
  },
  subGreeting: {
    color: '#93C5FD',
    fontSize: Typography.fontSize.xs,
    fontWeight: '700',
    letterSpacing: 0.5,
    textTransform: 'uppercase',
  },
  citizenName: {
    color: '#FFFFFF',
    fontSize: Typography.fontSize.xl,
    fontWeight: '800',
    marginTop: 2,
  },
  citizenMobile: {
    color: 'rgba(255, 255, 255, 0.7)',
    fontSize: Typography.fontSize.xs,
    marginTop: 2,
  },
  headerLogo: {
    width: 48,
    height: 48,
    marginLeft: 12,
  },
  primaryActionButton: {
    backgroundColor: '#1E40AF',
    borderRadius: BorderRadius.lg,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#3B82F6',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.2,
    shadowRadius: 6,
    elevation: 3,
  },
  actionIconCircle: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#FFFFFF',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 14,
  },
  actionTextGroup: {
    flex: 1,
  },
  actionButtonTitle: {
    color: '#FFFFFF',
    fontSize: Typography.fontSize.md,
    fontWeight: '800',
  },
  actionButtonSubtitle: {
    color: '#BFDBFE',
    fontSize: Typography.fontSize.xs,
    marginTop: 2,
  },
  sectionHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: Spacing.lg,
    marginTop: 20,
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: Typography.fontSize.md,
    fontWeight: '700',
    color: '#1E293B',
  },
  viewAllText: {
    fontSize: Typography.fontSize.sm,
    color: '#1E40AF',
    fontWeight: '600',
  },
  metricsRow: {
    flexDirection: 'row',
    paddingHorizontal: Spacing.lg,
    gap: 10,
  },
  metricCard: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: BorderRadius.md,
    padding: 12,
    alignItems: 'center',
    borderTopWidth: 3,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04,
    shadowRadius: 4,
    elevation: 1,
  },
  metricIconWrap: {
    width: 34,
    height: 34,
    borderRadius: 17,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 6,
  },
  metricNumber: {
    fontSize: Typography.fontSize.xl,
    fontWeight: '800',
    color: '#1E293B',
  },
  metricLabel: {
    fontSize: 11,
    fontWeight: '600',
    color: '#64748B',
    marginTop: 2,
    textAlign: 'center',
  },
  helplineBanner: {
    marginHorizontal: Spacing.lg,
    marginTop: 18,
    backgroundColor: '#0F766E',
    borderRadius: BorderRadius.md,
    padding: 14,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  helplineLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  helplineIconBox: {
    width: 38,
    height: 38,
    borderRadius: 19,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  helplineTitle: {
    color: '#FFFFFF',
    fontSize: Typography.fontSize.sm,
    fontWeight: '700',
  },
  helplineSubtitle: {
    color: '#CCFBF1',
    fontSize: 11,
    marginTop: 1,
  },
  callButton: {
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 20,
    marginLeft: 10,
  },
  callButtonText: {
    color: '#0F766E',
    fontSize: Typography.fontSize.sm,
    fontWeight: '800',
  },
  complaintCard: {
    backgroundColor: '#FFFFFF',
    marginHorizontal: Spacing.lg,
    marginBottom: 10,
    borderRadius: BorderRadius.md,
    padding: 14,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.03,
    shadowRadius: 3,
    elevation: 1,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  cardRefGroup: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  refNumber: {
    fontSize: Typography.fontSize.xs,
    fontWeight: '800',
    color: '#1E40AF',
  },
  categoryBadge: {
    fontSize: 10,
    color: '#475569',
    backgroundColor: '#F1F5F9',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
    fontWeight: '600',
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 10,
  },
  statusBadgePending: {
    backgroundColor: '#FEF3C7',
  },
  statusBadgeResolved: {
    backgroundColor: '#D1FAE5',
  },
  statusBadgeText: {
    fontSize: 10,
    fontWeight: '700',
  },
  statusTextPending: {
    color: '#92400E',
  },
  statusTextResolved: {
    color: '#065F46',
  },
  cardTitle: {
    fontSize: Typography.fontSize.sm,
    fontWeight: '700',
    color: '#1E293B',
    marginBottom: 4,
  },
  cardDetail: {
    fontSize: Typography.fontSize.xs,
    color: '#64748B',
    lineHeight: 18,
    marginBottom: 10,
  },
  cardFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#F1F5F9',
    paddingTop: 8,
  },
  locationGroup: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    flex: 1,
  },
  locationText: {
    fontSize: 11,
    color: '#64748B',
  },
  trackLinkGroup: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 2,
  },
  trackLink: {
    fontSize: 11,
    fontWeight: '700',
    color: '#1E40AF',
  },
  emptyCard: {
    backgroundColor: '#FFFFFF',
    marginHorizontal: Spacing.lg,
    padding: 30,
    borderRadius: BorderRadius.md,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  emptyTitle: {
    fontSize: Typography.fontSize.md,
    fontWeight: '700',
    color: '#1E293B',
    marginTop: 10,
  },
  emptySubtitle: {
    fontSize: Typography.fontSize.xs,
    color: '#64748B',
    textAlign: 'center',
    marginTop: 4,
    lineHeight: 18,
  },
  emptyButton: {
    marginTop: 16,
    backgroundColor: '#1E40AF',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: BorderRadius.md,
  },
  emptyButtonText: {
    color: '#FFFFFF',
    fontSize: Typography.fontSize.xs,
    fontWeight: '700',
  },
});

