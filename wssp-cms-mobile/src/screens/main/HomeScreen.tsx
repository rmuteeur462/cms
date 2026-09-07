import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  Modal,
  SafeAreaView,
  ActivityIndicator,
} from 'react-native';
import { Colors, Spacing, BorderRadius, Typography } from '../../constants/theme';
import { StatCard } from '../../components/common/StatCard';
import { ComplaintCard } from '../../components/common/ComplaintCard';
import { StatusBadge } from '../../components/common/StatusBadge';
import { EmptyState } from '../../components/common/EmptyState';
import { WSSPButton } from '../../components/common/WSSPButton';
import { useAuth } from '../../store/AuthContext';
import { ComplaintsApi, DashboardData, ComplaintSummaryItem } from '../../api/complaints';
import { Ionicons } from '@expo/vector-icons';
import { Formatters } from '../../utils/formatters';

interface HomeScreenProps {
  navigation?: any;
}

export const HomeScreen: React.FC<HomeScreenProps> = ({ navigation }) => {
  const { user } = useAuth();

  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [selectedComplaint, setSelectedComplaint] = useState<any | null>(null);
  const [detailModalVisible, setDetailModalVisible] = useState<boolean>(false);
  const [loadingDetail, setLoadingDetail] = useState<boolean>(false);

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

  const handleOpenDetail = async (complaintItem: ComplaintSummaryItem) => {
    setDetailModalVisible(true);
    setLoadingDetail(true);
    try {
      const fullDetail = await ComplaintsApi.getComplaintDetail(complaintItem.id);
      setSelectedComplaint(fullDetail);
    } catch (err) {
      console.warn('[HomeScreen] Detail load error, using summary:', err);
      setSelectedComplaint(complaintItem);
    } finally {
      setLoadingDetail(false);
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={[Colors.primary]} />
        }
      >
        {/* Officer Greeting Section */}
        <View style={styles.greetingHeader}>
          <Text style={styles.greetingText}>{getGreeting()}</Text>
          <Text style={styles.sectionSubtitle}>Complaint Management</Text>
          <Text style={styles.officerNameText}>
            {user?.full_name} • <Text style={styles.officerRoleText}>{user?.role}</Text>
          </Text>
        </View>

        {/* 2x2 Metric Grid */}
        <View style={styles.gridContainer}>
          <View style={styles.gridRow}>
            <StatCard
              title="Total Complaints"
              value={dashboard?.metrics.total ?? '...'}
              icon="layers-outline"
              color={Colors.primary}
              bgColor="#DCFCE7"
              onPress={() => navigation?.navigate('Complaints')}
            />
            <View style={{ width: Spacing.sm }} />
            <StatCard
              title="Pending Issues"
              value={dashboard?.metrics.pending ?? '...'}
              icon="time-outline"
              color={Colors.status.pending}
              bgColor={Colors.status.pendingBg}
              onPress={() => navigation?.navigate('Complaints', { status: 'pending' })}
            />
          </View>

          <View style={[styles.gridRow, { marginTop: Spacing.sm }]}>
            <StatCard
              title="Resolved"
              value={dashboard?.metrics.resolved ?? '...'}
              icon="checkmark-circle-outline"
              color={Colors.status.resolved}
              bgColor={Colors.status.resolvedBg}
              onPress={() => navigation?.navigate('Complaints', { status: 'resolved' })}
            />
            <View style={{ width: Spacing.sm }} />
            <StatCard
              title="Registered Today"
              value={dashboard?.metrics.today ?? '...'}
              icon="calendar-outline"
              color={Colors.secondary}
              bgColor="#E0F2FE"
            />
          </View>
        </View>

        {/* Assigned Zones Pill Bar */}
        {user?.allowed_locations && user.allowed_locations.length > 0 && (
          <View style={styles.zonesContainer}>
            <Text style={styles.zonesLabel}>OPERATIONAL JURISDICTION:</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.zonesScroll}>
              {user.allowed_locations.map((loc) => (
                <View key={loc.id} style={styles.zoneChip}>
                  <Ionicons name="location-outline" size={12} color={Colors.primary} style={{ marginRight: 3 }} />
                  <Text style={styles.zoneChipText}>{loc.name}</Text>
                </View>
              ))}
            </ScrollView>
          </View>
        )}

        {/* Recent Complaints Header */}
        <View style={styles.sectionHeaderRow}>
          <Text style={styles.sectionTitle}>Recent Complaints</Text>
          <TouchableOpacity onPress={() => navigation?.navigate('Complaints')} activeOpacity={0.7}>
            <Text style={styles.seeAllText}>View All &gt;</Text>
          </TouchableOpacity>
        </View>

        {/* Recent Complaints Feed */}
        {loading ? (
          <View style={styles.loadingBox}>
            <ActivityIndicator size="small" color={Colors.primary} />
            <Text style={styles.loadingText}>Fetching recent complaints...</Text>
          </View>
        ) : dashboard?.recent_complaints && dashboard.recent_complaints.length > 0 ? (
          dashboard.recent_complaints.map((item) => (
            <ComplaintCard
              key={item.id}
              complaint={item}
              onPress={() => handleOpenDetail(item)}
            />
          ))
        ) : (
          <EmptyState
            title="No Recent Complaints"
            description="All complaints in your assigned jurisdiction have been reviewed."
          />
        )}
      </ScrollView>

      {/* Complaint Detail Modal */}
      <Modal
        visible={detailModalVisible}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={() => setDetailModalVisible(false)}
      >
        <SafeAreaView style={styles.modalSafeArea}>
          <View style={styles.modalHeader}>
            <View style={styles.modalTitleBox}>
              <Text style={styles.modalComplaintNo}>{selectedComplaint?.complaint_no || 'Complaint Details'}</Text>
              <Text style={styles.modalSubheading}>{selectedComplaint?.category}</Text>
            </View>
            <TouchableOpacity
              onPress={() => setDetailModalVisible(false)}
              style={styles.closeBtn}
              activeOpacity={0.7}
            >
              <Ionicons name="close" size={24} color={Colors.textSecondary} />
            </TouchableOpacity>
          </View>

          {loadingDetail ? (
            <View style={styles.modalLoading}>
              <ActivityIndicator size="large" color={Colors.primary} />
              <Text style={styles.modalLoadingText}>Loading full record...</Text>
            </View>
          ) : selectedComplaint ? (
            <ScrollView contentContainerStyle={styles.modalBody}>
              {/* Status Banner */}
              <View style={styles.statusBanner}>
                <Text style={styles.bannerLabel}>Status:</Text>
                <StatusBadge status={selectedComplaint.status} />
              </View>

              {/* Issue Description Card */}
              <View style={styles.detailCard}>
                <Text style={styles.cardHeaderTitle}>Complaint Description</Text>
                <Text style={styles.detailText}>
                  {selectedComplaint.detail || selectedComplaint.title || 'No additional remarks.'}
                </Text>
              </View>

              {/* Citizen & Location Details */}
              <View style={styles.detailCard}>
                <Text style={styles.cardHeaderTitle}>Citizen & Location</Text>
                
                <View style={styles.detailRow}>
                  <Text style={styles.rowLabel}>Citizen Name:</Text>
                  <Text style={styles.rowValue}>{selectedComplaint.citizen_name}</Text>
                </View>

                <View style={styles.detailRow}>
                  <Text style={styles.rowLabel}>Cell Number:</Text>
                  <Text style={styles.rowValue}>{Formatters.formatPhone(selectedComplaint.cell_number)}</Text>
                </View>

                {selectedComplaint.cnic && (
                  <View style={styles.detailRow}>
                    <Text style={styles.rowLabel}>CNIC:</Text>
                    <Text style={styles.rowValue}>{Formatters.formatCNIC(selectedComplaint.cnic)}</Text>
                  </View>
                )}

                <View style={styles.detailRow}>
                  <Text style={styles.rowLabel}>Zone & UC:</Text>
                  <Text style={styles.rowValue}>{selectedComplaint.location} • {selectedComplaint.uc}</Text>
                </View>

                <View style={styles.detailRow}>
                  <Text style={styles.rowLabel}>Area / Address:</Text>
                  <Text style={styles.rowValue}>{selectedComplaint.area || selectedComplaint.address || 'Peshawar'}</Text>
                </View>

                <View style={styles.detailRow}>
                  <Text style={styles.rowLabel}>Registration Date:</Text>
                  <Text style={styles.rowValue}>{Formatters.formatDate(selectedComplaint.date)}</Text>
                </View>
              </View>

              {/* Resolution Info (if resolved) */}
              {selectedComplaint.resolution && (
                <View style={[styles.detailCard, styles.resolutionCard]}>
                  <Text style={[styles.cardHeaderTitle, { color: Colors.status.resolved }]}>
                    Resolution Details
                  </Text>
                  <Text style={styles.detailText}>
                    {selectedComplaint.resolution.description || 'Marked resolved by field officer.'}
                  </Text>
                  {selectedComplaint.resolution.customer_satisfaction && (
                    <View style={[styles.detailRow, { marginTop: 8 }]}>
                      <Text style={styles.rowLabel}>Citizen Satisfaction:</Text>
                      <Text style={[styles.rowValue, { textTransform: 'capitalize', fontWeight: '800' }]}>
                        {selectedComplaint.resolution.customer_satisfaction}
                      </Text>
                    </View>
                  )}
                </View>
              )}

              <WSSPButton
                title="Close Record"
                variant="secondary"
                onPress={() => setDetailModalVisible(false)}
                style={{ marginTop: Spacing.md }}
              />
            </ScrollView>
          ) : null}
        </SafeAreaView>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  scrollContent: {
    padding: Spacing.md,
    paddingBottom: Spacing.xxl,
  },
  greetingHeader: {
    marginBottom: Spacing.md,
    paddingTop: Spacing.xs,
  },
  greetingText: {
    fontSize: Typography.fontSize.sm,
    fontWeight: '700',
    color: Colors.textMuted,
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  sectionSubtitle: {
    fontSize: 26,
    fontWeight: '900',
    color: Colors.textPrimary,
    letterSpacing: -0.5,
    marginTop: 2,
  },
  officerNameText: {
    fontSize: Typography.fontSize.sm,
    fontWeight: '700',
    color: Colors.primary,
    marginTop: 4,
  },
  officerRoleText: {
    fontWeight: '600',
    color: Colors.textSecondary,
  },
  gridContainer: {
    marginBottom: Spacing.md,
  },
  gridRow: {
    flexDirection: 'row',
  },
  zonesContainer: {
    backgroundColor: '#F1F5F9',
    padding: Spacing.sm,
    borderRadius: BorderRadius.md,
    marginBottom: Spacing.md,
  },
  zonesLabel: {
    fontSize: 9,
    fontWeight: '800',
    color: Colors.textMuted,
    letterSpacing: 1,
    marginBottom: 6,
  },
  zonesScroll: {
    flexDirection: 'row',
    gap: Spacing.xs,
  },
  zoneChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.surface,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: BorderRadius.full,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  zoneChipText: {
    fontSize: 11,
    fontWeight: '700',
    color: Colors.primary,
  },
  sectionHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: Spacing.xs,
    marginBottom: Spacing.sm,
  },
  sectionTitle: {
    fontSize: Typography.fontSize.lg,
    fontWeight: '800',
    color: Colors.textPrimary,
  },
  seeAllText: {
    fontSize: Typography.fontSize.sm,
    fontWeight: '700',
    color: Colors.primary,
  },
  loadingBox: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: Spacing.xl,
  },
  loadingText: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textMuted,
    marginTop: Spacing.sm,
  },
  modalSafeArea: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  modalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: Spacing.md,
    backgroundColor: Colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  modalTitleBox: {
    flex: 1,
  },
  modalComplaintNo: {
    fontSize: Typography.fontSize.lg,
    fontWeight: '800',
    color: Colors.primary,
  },
  modalSubheading: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textSecondary,
    fontWeight: '600',
  },
  closeBtn: {
    padding: 6,
  },
  modalLoading: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  modalLoadingText: {
    marginTop: Spacing.sm,
    color: Colors.textMuted,
    fontSize: Typography.fontSize.sm,
  },
  modalBody: {
    padding: Spacing.md,
  },
  statusBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: Colors.surface,
    padding: Spacing.md,
    borderRadius: BorderRadius.md,
    marginBottom: Spacing.md,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  bannerLabel: {
    fontSize: Typography.fontSize.sm,
    fontWeight: '700',
    color: Colors.textSecondary,
  },
  detailCard: {
    backgroundColor: Colors.surface,
    padding: Spacing.md,
    borderRadius: BorderRadius.md,
    marginBottom: Spacing.md,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  resolutionCard: {
    backgroundColor: '#F0FDF4',
    borderColor: '#BBF7D0',
  },
  cardHeaderTitle: {
    fontSize: Typography.fontSize.sm,
    fontWeight: '800',
    color: Colors.textPrimary,
    marginBottom: Spacing.sm,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  detailText: {
    fontSize: Typography.fontSize.md,
    color: Colors.textPrimary,
    lineHeight: 22,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 4,
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
});
