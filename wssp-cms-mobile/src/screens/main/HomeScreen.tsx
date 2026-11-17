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
import {
  ComplaintsApi,
  DashboardAnalyticsResponse,
} from '../../api/complaints';
import { Ionicons } from '@expo/vector-icons';
import { AnalyticsFilter } from '../../components/dashboard/AnalyticsFilter';
import { ComplaintTrendChart } from '../../components/dashboard/ComplaintTrendChart';
import { CategoryDistributionChart } from '../../components/dashboard/CategoryDistributionChart';

interface HomeScreenProps {
  navigation?: any;
}

export const HomeScreen: React.FC<HomeScreenProps> = ({ navigation }) => {
  const { user } = useAuth();

  const [analytics, setAnalytics] = useState<DashboardAnalyticsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Default filter: Year 2026, Month 1 (or current reporting period)
  const [filter, setFilter] = useState<{
    year?: number | 'all';
    month?: number;
    start_date?: string;
    end_date?: string;
  }>({
    year: 2026,
    month: 1,
  });

  // Zone filter: undefined = All Zones, number = specific location id
  const [selectedZoneId, setSelectedZoneId] = useState<number | undefined>(undefined);

  // Filter out Head Office from zone chips
  const zoneOptions = (user?.allowed_locations || []).filter(
    (loc) => !loc.name.toLowerCase().replace(/\s+/g, '').includes('headoffice')
  );

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 17) return 'Good Afternoon';
    return 'Good Evening';
  };

  const loadAnalyticsData = async (
    activeFilter = filter,
    zoneId: number | undefined = selectedZoneId
  ) => {
    setError(null);
    try {
      const data = await ComplaintsApi.getDashboardAnalytics({
        ...activeFilter,
        location_id: zoneId,
      });
      setAnalytics(data);
    } catch (err: any) {
      console.warn('[HomeScreen] Failed to load dashboard analytics:', err);
      setError('Unable to load analytics for the selected period.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadAnalyticsData(filter, selectedZoneId);
  }, []);

  const handleFilterChange = (newFilter: {
    year?: number | 'all';
    month?: number;
    start_date?: string;
    end_date?: string;
  }) => {
    setFilter(newFilter);
    setLoading(true);
    loadAnalyticsData(newFilter, selectedZoneId);
  };

  const handleZoneSelect = (zoneId: number | undefined) => {
    setSelectedZoneId(zoneId);
    setLoading(true);
    loadAnalyticsData(filter, zoneId);
  };

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    loadAnalyticsData(filter, selectedZoneId);
  }, [filter, selectedZoneId]);

  const summary = analytics?.summary;
  const isSingleDept = analytics?.scope?.is_single_department ?? false;

  return (
    <View style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={[Colors.primary]} />
        }
      >
        {/* Clean Executive Header */}
        <View style={styles.greetingHeader}>
          <Text style={styles.sectionSubtitle}>Complaint Management</Text>
          <Text style={styles.officerRoleText}>
            {analytics?.scope?.role_title || user?.role || 'Departmental Officer'}
          </Text>
        </View>

        {/* Analytics Filter Section */}
        <View style={styles.filterSectionWrapper}>
          <AnalyticsFilter
            currentPeriodLabel={analytics?.period?.label}
            onFilterChange={handleFilterChange}
            loading={loading}
          />
        </View>

        {/* Zone Selector Chips */}
        {zoneOptions.length > 1 && (
          <View style={styles.zoneFilterWrapper}>
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              contentContainerStyle={styles.zoneScrollContent}
            >
              {/* All Zones chip */}
              <TouchableOpacity
                style={[
                  styles.zoneChip,
                  selectedZoneId === undefined && styles.zoneChipActive,
                ]}
                onPress={() => handleZoneSelect(undefined)}
                activeOpacity={0.7}
              >
                <Ionicons
                  name="layers-outline"
                  size={13}
                  color={selectedZoneId === undefined ? '#FFFFFF' : Colors.textMuted}
                  style={{ marginRight: 4 }}
                />
                <Text
                  style={[
                    styles.zoneChipText,
                    selectedZoneId === undefined && styles.zoneChipTextActive,
                  ]}
                >
                  All Zones
                </Text>
              </TouchableOpacity>

              {/* Individual zone chips */}
              {zoneOptions.map((loc) => (
                <TouchableOpacity
                  key={loc.id}
                  style={[
                    styles.zoneChip,
                    selectedZoneId === loc.id && styles.zoneChipActive,
                  ]}
                  onPress={() => handleZoneSelect(loc.id)}
                  activeOpacity={0.7}
                >
                  <Ionicons
                    name="location-outline"
                    size={13}
                    color={selectedZoneId === loc.id ? '#FFFFFF' : Colors.textMuted}
                    style={{ marginRight: 4 }}
                  />
                  <Text
                    style={[
                      styles.zoneChipText,
                      selectedZoneId === loc.id && styles.zoneChipTextActive,
                    ]}
                  >
                    {loc.name}
                  </Text>
                </TouchableOpacity>
              ))}
            </ScrollView>

            {/* Zone label indicator */}
            <Text style={styles.zoneActiveLabel}>
              {selectedZoneId === undefined
                ? 'Showing data across all zones'
                : `Showing: ${zoneOptions.find((z) => z.id === selectedZoneId)?.name ?? 'Zone'}`}
            </Text>
          </View>
        )}

        {/* Loading Indicator */}
        {loading && (
          <View style={styles.loadingBanner}>
            <ActivityIndicator size="small" color={Colors.primary} />
            <Text style={styles.loadingBannerText}>Updating analytics for selected period...</Text>
          </View>
        )}

        {/* Error State with Retry Button */}
        {error && !loading && (
          <View style={styles.errorCard}>
            <Ionicons name="alert-circle-outline" size={24} color={Colors.status.rejected} />
            <Text style={styles.errorText}>{error}</Text>
            <TouchableOpacity
              style={styles.retryBtn}
              onPress={() => {
                setLoading(true);
                loadAnalyticsData(filter, selectedZoneId);
              }}
            >
              <Text style={styles.retryBtnText}>Retry</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* 3 Metric Summary Cards Row */}
        <View style={styles.gridContainer}>
          <View style={styles.gridRow}>
            <StatCard
              title="Total"
              value={summary?.total ?? (loading ? '...' : 0)}
              icon="layers-outline"
              color={Colors.primary}
              bgColor="#DCFCE7"
              onPress={() =>
                navigation?.navigate('Complaints', {
                  status: 'all',
                  year: filter.year,
                  month: filter.month,
                  start_date: filter.start_date,
                  end_date: filter.end_date,
                  location_id: selectedZoneId,
                })
              }
            />
            <View style={{ width: Spacing.sm }} />
            <StatCard
              title="Pending"
              value={summary?.pending ?? (loading ? '...' : 0)}
              icon="time-outline"
              color={Colors.status.pending}
              bgColor={Colors.status.pendingBg}
              onPress={() =>
                navigation?.navigate('Complaints', {
                  status: 'pending',
                  year: filter.year,
                  month: filter.month,
                  start_date: filter.start_date,
                  end_date: filter.end_date,
                  location_id: selectedZoneId,
                })
              }
            />
            <View style={{ width: Spacing.sm }} />
            <StatCard
              title="Resolved"
              value={summary?.resolved ?? (loading ? '...' : 0)}
              icon="checkmark-circle-outline"
              color={Colors.status.resolved}
              bgColor={Colors.status.resolvedBg}
              onPress={() =>
                navigation?.navigate('Complaints', {
                  status: 'resolved',
                  year: filter.year,
                  month: filter.month,
                  start_date: filter.start_date,
                  end_date: filter.end_date,
                  location_id: selectedZoneId,
                })
              }
            />
          </View>
        </View>

        {/* Empty Period State */}
        {!loading && analytics && summary?.total === 0 && (
          <View style={styles.emptyCard}>
            <Ionicons name="folder-open-outline" size={36} color={Colors.textMuted} />
            <Text style={styles.emptyTitle}>No Complaints Found</Text>
            <Text style={styles.emptySubtitle}>
              No complaints were registered within your authorized scope for {analytics.period.label}.
            </Text>
          </View>
        )}

        {/* Dynamic Charts Section */}
        {analytics && summary && summary.total > 0 && (
          <View style={styles.chartsContainer}>
            {/* Chart 1: Time Trend Bar Chart */}
            <ComplaintTrendChart
              data={analytics.trend}
              periodLabel={analytics.period.label}
              isMonthlyView={analytics.period.period_type === 'month'}
            />


            {/* Chart 3: Role-Aware Category / Subtype Distribution (Interactive: click to open complaints) */}
            <CategoryDistributionChart
              isSingleDepartment={isSingleDept}
              typeDistribution={analytics.type_distribution}
              subtypeDistribution={analytics.subtype_distribution}
              departmentName={analytics.scope.department}
              onItemPress={(item) => {
                navigation?.navigate('Complaints', {
                  category: !item.isSubtype ? item.name : undefined,
                  subtype: item.isSubtype ? item.name : undefined,
                  categoryId: !item.isSubtype ? item.id : undefined,
                  subtypeId: item.isSubtype ? item.id : undefined,
                  isSubtype: item.isSubtype,
                  year: filter.year,
                  month: filter.month,
                  start_date: filter.start_date,
                  end_date: filter.end_date,
                  location_id: selectedZoneId,
                });
              }}
            />
          </View>
        )}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  scrollContent: {
    paddingBottom: 90, // Clearance for bottom tabs & floating button
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
  filterSectionWrapper: {
    paddingHorizontal: Spacing.md,
    marginTop: Spacing.sm,
  },
  zoneFilterWrapper: {
    marginTop: Spacing.xs,
    marginBottom: 2,
  },
  zoneScrollContent: {
    paddingHorizontal: Spacing.md,
    gap: 8,
    flexDirection: 'row',
    alignItems: 'center',
  },
  zoneChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.surface,
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: BorderRadius.full,
    paddingHorizontal: 12,
    paddingVertical: 6,
    marginRight: 6,
  },
  zoneChipActive: {
    backgroundColor: Colors.primary,
    borderColor: Colors.primary,
  },
  zoneChipText: {
    fontSize: 12,
    fontWeight: '600',
    color: Colors.textMuted,
  },
  zoneChipTextActive: {
    color: '#FFFFFF',
  },
  zoneActiveLabel: {
    fontSize: 11,
    color: Colors.textMuted,
    fontWeight: '500',
    paddingHorizontal: Spacing.md,
    marginTop: 4,
    marginBottom: Spacing.xs,
  },

  loadingBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 6,
    paddingHorizontal: Spacing.md,
    marginHorizontal: Spacing.md,
    marginBottom: Spacing.sm,
    backgroundColor: '#EFF6FF',
    borderRadius: BorderRadius.md,
  },
  loadingBannerText: {
    fontSize: Typography.fontSize.xs,
    color: Colors.primary,
    fontWeight: '600',
    marginLeft: 6,
  },
  errorCard: {
    backgroundColor: '#FEF2F2',
    borderRadius: BorderRadius.lg,
    padding: Spacing.md,
    marginHorizontal: Spacing.md,
    marginBottom: Spacing.md,
    borderWidth: 1,
    borderColor: '#FCA5A5',
    alignItems: 'center',
  },
  errorText: {
    fontSize: Typography.fontSize.xs,
    color: Colors.status.rejected,
    fontWeight: '600',
    marginVertical: Spacing.xs,
    textAlign: 'center',
  },
  retryBtn: {
    backgroundColor: Colors.status.rejected,
    paddingHorizontal: Spacing.md,
    paddingVertical: 6,
    borderRadius: BorderRadius.sm,
    marginTop: 4,
  },
  retryBtnText: {
    fontSize: 11,
    fontWeight: '800',
    color: '#FFFFFF',
  },
  gridContainer: {
    paddingHorizontal: Spacing.md,
    marginBottom: Spacing.md,
  },
  gridRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  emptyCard: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.xl,
    marginHorizontal: Spacing.md,
    marginBottom: Spacing.md,
    borderWidth: 1,
    borderColor: Colors.border,
    alignItems: 'center',
    justifyContent: 'center',
  },
  emptyTitle: {
    fontSize: Typography.fontSize.md,
    fontWeight: '800',
    color: Colors.textPrimary,
    marginTop: Spacing.sm,
  },
  emptySubtitle: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textMuted,
    textAlign: 'center',
    marginTop: 4,
    lineHeight: 18,
  },
  chartsContainer: {
    paddingHorizontal: Spacing.md,
  },
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
