import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TextInput,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
  Modal,
  SafeAreaView,
  ScrollView,
} from 'react-native';
import { Colors, Spacing, BorderRadius, Typography } from '../../constants/theme';
import { ComplaintCard } from '../../components/common/ComplaintCard';
import { EmptyState } from '../../components/common/EmptyState';
import { StatusBadge } from '../../components/common/StatusBadge';
import { WSSPButton } from '../../components/common/WSSPButton';
import { ComplaintsApi, ComplaintSummaryItem } from '../../api/complaints';
import { useAuth } from '../../store/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import { Formatters } from '../../utils/formatters';
import { AnalyticsFilter } from '../../components/dashboard/AnalyticsFilter';

export const ComplaintsScreen: React.FC<{ navigation?: any; route?: any }> = ({ navigation, route }) => {
  const { user } = useAuth();

  const [complaints, setComplaints] = useState<ComplaintSummaryItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'pending' | 'resolved'>('all');
  
  // Category / Type / Subtype filter passed from Home screen clicks
  const [selectedCategory, setSelectedCategory] = useState<{
    id?: number | null;
    name: string;
    isSubtype: boolean;
  } | null>(null);

  // Date period filter (same as Home analytics: 2026, month 1 by default, or all years/custom)
  const [dateFilter, setDateFilter] = useState<{
    year?: number | 'all';
    month?: number;
    start_date?: string;
    end_date?: string;
  }>({
    year: 2026,
    month: 1,
  });

  // Filter out 'Head Office' / 'Headoffice'
  const filteredLocations = (user?.allowed_locations || []).filter(
    (loc) => !loc.name.toLowerCase().replace(/\s+/g, '').includes('headoffice')
  );

  const [selectedLocationId, setSelectedLocationId] = useState<number | undefined>(
    filteredLocations.length > 1 ? undefined : filteredLocations[0]?.id
  );
  const [totalCount, setTotalCount] = useState<number>(0);
  const [resolvedCount, setResolvedCount] = useState<number>(0);
  const [pendingCount, setPendingCount] = useState<number>(0);

  // Sync route params whenever navigated to with params
  useEffect(() => {
    if (route?.params) {
      const p = route.params;
      if (p.status && ['all', 'pending', 'resolved'].includes(p.status)) {
        setStatusFilter(p.status);
      }
      if (p.category || p.subtype) {
        setSelectedCategory({
          id: p.categoryId ?? p.subtypeId ?? null,
          name: p.subtype || p.category,
          isSubtype: Boolean(p.subtype || p.isSubtype),
        });
      }
      if (p.year !== undefined || p.month !== undefined || p.start_date || p.end_date) {
        setDateFilter({
          year: p.year ?? 2026,
          month: p.month,
          start_date: p.start_date,
          end_date: p.end_date,
        });
      }
      setSelectedLocationId(p.location_id);
    }
  }, [route?.params]);

  // Update selected location if filteredLocations loads or changes
  useEffect(() => {
    if (filteredLocations.length === 1 && selectedLocationId === undefined) {
      setSelectedLocationId(filteredLocations[0].id);
    }
  }, [user?.allowed_locations]);

  // Detail Modal
  const [selectedComplaint, setSelectedComplaint] = useState<any | null>(null);
  const [detailModalVisible, setDetailModalVisible] = useState<boolean>(false);
  const [loadingDetail, setLoadingDetail] = useState<boolean>(false);

  const fetchComplaints = async (
    customDateFilter = dateFilter,
    locId = selectedLocationId,
    categoryObj = selectedCategory
  ) => {
    try {
      const data = await ComplaintsApi.getComplaints({
        search: searchQuery.trim() || undefined,
        status: statusFilter,
        location_id: locId,
        year: customDateFilter.year,
        month: customDateFilter.month,
        start_date: customDateFilter.start_date,
        end_date: customDateFilter.end_date,
        category_id: categoryObj && !categoryObj.isSubtype && categoryObj.id ? categoryObj.id : undefined,
        subtype_id: categoryObj && categoryObj.isSubtype && categoryObj.id ? categoryObj.id : undefined,
        category: categoryObj && !categoryObj.isSubtype && !categoryObj.id ? categoryObj.name : undefined,
        subtype: categoryObj && categoryObj.isSubtype && !categoryObj.id ? categoryObj.name : undefined,
        page: 1,
        page_size: 100, // Load comprehensive records for the zone
      });
      setComplaints(data.results);
      setTotalCount(data.total_count);
      if (data.resolved_count !== undefined) setResolvedCount(data.resolved_count);
      if (data.pending_count !== undefined) setPendingCount(data.pending_count);
    } catch (err) {
      console.warn('[ComplaintsScreen] Load error:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchComplaints();
  }, [statusFilter, selectedLocationId, dateFilter, selectedCategory]);

  const handleDateFilterChange = (newDateFilter: {
    year?: number | 'all';
    month?: number;
    start_date?: string;
    end_date?: string;
  }) => {
    setDateFilter(newDateFilter);
    setLoading(true);
    fetchComplaints(newDateFilter);
  };

  const handleSearchSubmit = () => {
    setLoading(true);
    fetchComplaints();
  };

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    fetchComplaints();
  }, [statusFilter, selectedLocationId, searchQuery, dateFilter]);

  const handleOpenDetail = async (item: ComplaintSummaryItem) => {
    setDetailModalVisible(true);
    setLoadingDetail(true);
    try {
      const fullDetail = await ComplaintsApi.getComplaintDetail(item.id);
      setSelectedComplaint(fullDetail);
    } catch {
      setSelectedComplaint(item);
    } finally {
      setLoadingDetail(false);
    }
  };

  return (
    <View style={styles.container}>
      {/* Search Bar */}
      <View style={styles.searchSection}>
        <View style={styles.searchBar}>
          <Ionicons name="search" size={18} color={Colors.textMuted} style={{ marginRight: 8 }} />
          <TextInput
            style={styles.searchInput}
            placeholder="Search by ID, Phone, Citizen, Area..."
            placeholderTextColor={Colors.textMuted}
            value={searchQuery}
            onChangeText={setSearchQuery}
            onSubmitEditing={handleSearchSubmit}
            returnKeyType="search"
          />
          {searchQuery ? (
            <TouchableOpacity onPress={() => { setSearchQuery(''); fetchComplaints(dateFilter); }}>
              <Ionicons name="close-circle" size={18} color={Colors.textMuted} />
            </TouchableOpacity>
          ) : null}
        </View>
      </View>

      {/* Date & Period Filter (Identical to Home screen) */}
      <View style={styles.filterSectionWrapper}>
        <AnalyticsFilter
          initialYear={dateFilter.year}
          initialMonth={dateFilter.month}
          initialStartDate={dateFilter.start_date}
          initialEndDate={dateFilter.end_date}
          onFilterChange={handleDateFilterChange}
          loading={loading}
        />
      </View>

      {/* Quick Status Stats Small Boxes */}
      <View style={styles.statusStatsRow}>
        <TouchableOpacity
          style={[styles.smallStatBox, styles.smallStatBoxResolved, statusFilter === 'resolved' && styles.smallStatBoxActiveResolved]}
          onPress={() => setStatusFilter(statusFilter === 'resolved' ? 'all' : 'resolved')}
          activeOpacity={0.7}
        >
          <View style={styles.smallStatHeader}>
            <View style={[styles.statDot, { backgroundColor: '#16A34A' }]} />
            <Text style={styles.smallStatLabel}>Resolved</Text>
          </View>
          <Text style={[styles.smallStatValue, { color: '#15803D' }]}>
            {resolvedCount.toLocaleString()}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.smallStatBox, styles.smallStatBoxPending, statusFilter === 'pending' && styles.smallStatBoxActivePending]}
          onPress={() => setStatusFilter(statusFilter === 'pending' ? 'all' : 'pending')}
          activeOpacity={0.7}
        >
          <View style={styles.smallStatHeader}>
            <View style={[styles.statDot, { backgroundColor: '#F59E0B' }]} />
            <Text style={styles.smallStatLabel}>Pending</Text>
          </View>
          <Text style={[styles.smallStatValue, { color: '#B45309' }]}>
            {pendingCount.toLocaleString()}
          </Text>
        </TouchableOpacity>
      </View>

      {/* Filter Tabs */}
      <View style={styles.tabBar}>
        <TouchableOpacity
          style={[styles.tabBtn, statusFilter === 'all' && styles.activeTabBtn]}
          onPress={() => setStatusFilter('all')}
          activeOpacity={0.7}
        >
          <Text style={[styles.tabText, statusFilter === 'all' && styles.activeTabText]}>
            All ({totalCount})
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tabBtn, statusFilter === 'pending' && styles.activeTabBtnPending]}
          onPress={() => setStatusFilter('pending')}
          activeOpacity={0.7}
        >
          <Text style={[styles.tabText, statusFilter === 'pending' && styles.activeTabTextPending]}>
            Pending ({pendingCount})
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tabBtn, statusFilter === 'resolved' && styles.activeTabBtnResolved]}
          onPress={() => setStatusFilter('resolved')}
          activeOpacity={0.7}
        >
          <Text style={[styles.tabText, statusFilter === 'resolved' && styles.activeTabTextResolved]}>
            Resolved ({resolvedCount})
          </Text>
        </TouchableOpacity>
      </View>

      {/* Zone Selector Chips */}
      {filteredLocations.length > 1 && (
        <View style={styles.zonesContainer}>
          <TouchableOpacity
            style={[styles.zoneChip, selectedLocationId === undefined && styles.zoneChipActive]}
            onPress={() => setSelectedLocationId(undefined)}
            activeOpacity={0.7}
          >
            <Ionicons
              name="layers-outline"
              size={13}
              color={selectedLocationId === undefined ? Colors.primary : Colors.textMuted}
              style={{ marginRight: 4 }}
            />
            <Text style={[styles.zoneChipText, selectedLocationId === undefined && styles.zoneChipTextActive]}>
              All Zones
            </Text>
          </TouchableOpacity>
          {filteredLocations.map((loc) => (
            <TouchableOpacity
              key={loc.id}
              style={[styles.zoneChip, selectedLocationId === loc.id && styles.zoneChipActive]}
              onPress={() => setSelectedLocationId(loc.id)}
              activeOpacity={0.7}
            >
              <Ionicons
                name="location-outline"
                size={13}
                color={selectedLocationId === loc.id ? Colors.primary : Colors.textMuted}
                style={{ marginRight: 4 }}
              />
              <Text style={[styles.zoneChipText, selectedLocationId === loc.id && styles.zoneChipTextActive]}>
                {loc.name}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      )}

      {/* Active Category Filter Tag / Breadcrumb */}
      {selectedCategory && (
        <View style={styles.categoryFilterBanner}>
          <View style={styles.categoryPill}>
            <Ionicons
              name={selectedCategory.isSubtype ? 'list-outline' : 'business-outline'}
              size={13}
              color={Colors.primary}
              style={{ marginRight: 5 }}
            />
            <Text style={styles.categoryPillText} numberOfLines={1}>
              Filtered by {selectedCategory.isSubtype ? 'Subtype' : 'Department'}:{' '}
              <Text style={styles.categoryPillBold}>{selectedCategory.name}</Text>
            </Text>
            <TouchableOpacity
              onPress={() => setSelectedCategory(null)}
              style={styles.categoryPillClose}
              hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
            >
              <Ionicons name="close-circle" size={16} color={Colors.primary} />
            </TouchableOpacity>
          </View>
        </View>
      )}

      {/* Complaint List */}
      {loading ? (
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color={Colors.primary} />
          <Text style={styles.loadingMsg}>Loading departmental records...</Text>
        </View>
      ) : (
        <FlatList
          data={complaints}
          keyExtractor={(item) => item.id.toString()}
          renderItem={({ item }) => (
            <ComplaintCard complaint={item} onPress={() => handleOpenDetail(item)} />
          )}
          contentContainerStyle={styles.listContent}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={[Colors.primary]} />
          }
          ListEmptyComponent={
            <EmptyState
              title="No Complaints Found"
              description="No complaints matched your current filter criteria."
              actionTitle="Reset Filters"
              onAction={() => {
                setStatusFilter('all');
                setSelectedLocationId(filteredLocations[0]?.id);
                setSearchQuery('');
                setSelectedCategory(null);
              }}
            />
          }
        />
      )}

      {/* Floating Action Button (FAB) for New Complaint */}
      <TouchableOpacity
        style={styles.fabBtn}
        onPress={() => navigation?.navigate('NewComplaint')}
        activeOpacity={0.85}
      >
        <Ionicons name="add" size={24} color="#FFFFFF" style={{ marginRight: 6 }} />
        <Text style={styles.fabBtnText}>New Complaint</Text>
      </TouchableOpacity>

      {/* Detail Modal */}
      <Modal
        visible={detailModalVisible}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={() => setDetailModalVisible(false)}
      >
        <SafeAreaView style={styles.modalSafeArea}>
          <View style={styles.modalHeader}>
            <View>
              <Text style={styles.modalTitle}>{selectedComplaint?.complaint_no}</Text>
              <Text style={styles.modalSubtitle}>{selectedComplaint?.category}</Text>
            </View>
            <TouchableOpacity onPress={() => setDetailModalVisible(false)} style={styles.closeBtn}>
              <Ionicons name="close" size={24} color={Colors.textSecondary} />
            </TouchableOpacity>
          </View>

          {loadingDetail ? (
            <View style={styles.centerContainer}>
              <ActivityIndicator size="large" color={Colors.primary} />
            </View>
          ) : selectedComplaint ? (
            <ScrollView contentContainerStyle={styles.modalBody}>
              <View style={styles.modalStatusRow}>
                <Text style={styles.modalStatusLabel}>Status:</Text>
                <StatusBadge status={selectedComplaint.status} />
              </View>

              <View style={styles.infoCard}>
                <Text style={styles.infoHeading}>Citizen Information</Text>
                <Text style={styles.infoRow}><Text style={styles.bold}>Name:</Text> {selectedComplaint.citizen_name}</Text>
                <Text style={styles.infoRow}><Text style={styles.bold}>Cell:</Text> {Formatters.formatPhone(selectedComplaint.cell_number)}</Text>
                {selectedComplaint.cnic && (
                  <Text style={styles.infoRow}><Text style={styles.bold}>CNIC:</Text> {Formatters.formatCNIC(selectedComplaint.cnic)}</Text>
                )}
                <Text style={styles.infoRow}><Text style={styles.bold}>Zone/UC:</Text> {selectedComplaint.location} • {selectedComplaint.uc}</Text>
                <Text style={styles.infoRow}><Text style={styles.bold}>Address:</Text> {selectedComplaint.area || selectedComplaint.address}</Text>
              </View>

              <View style={styles.infoCard}>
                <Text style={styles.infoHeading}>Complaint Particulars</Text>
                <Text style={styles.infoRow}><Text style={styles.bold}>Title:</Text> {selectedComplaint.title}</Text>
                <Text style={styles.infoRow}><Text style={styles.bold}>Type:</Text> {selectedComplaint.category} {selectedComplaint.subtype ? `(${selectedComplaint.subtype})` : ''}</Text>
                <Text style={styles.infoRow}><Text style={styles.bold}>Date:</Text> {Formatters.formatDate(selectedComplaint.date)}</Text>
                <Text style={[styles.infoRow, { marginTop: 8 }]}><Text style={styles.bold}>Details:</Text> {selectedComplaint.detail}</Text>
              </View>

              {selectedComplaint.resolution && (
                <View style={[styles.infoCard, { backgroundColor: '#F0FDF4', borderColor: '#BBF7D0' }]}>
                  <Text style={[styles.infoHeading, { color: Colors.status.resolved }]}>Resolution Proof</Text>
                  <Text style={styles.infoRow}><Text style={styles.bold}>Remarks:</Text> {selectedComplaint.resolution.description || 'Resolved.'}</Text>
                  <Text style={styles.infoRow}><Text style={styles.bold}>Citizen Satisfaction:</Text> {selectedComplaint.resolution.customer_satisfaction || 'N/A'}</Text>
                </View>
              )}

              <WSSPButton
                title="Close"
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
  searchSection: {
    paddingHorizontal: Spacing.md,
    paddingTop: Spacing.md,
    paddingBottom: Spacing.xs,
  },
  filterSectionWrapper: {
    paddingHorizontal: Spacing.md,
    marginBottom: Spacing.xs,
  },
  searchBar: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.surface,
    paddingHorizontal: Spacing.md,
    height: 46,
    borderRadius: BorderRadius.md,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  searchInput: {
    flex: 1,
    fontSize: Typography.fontSize.sm,
    color: Colors.textPrimary,
  },
  statusStatsRow: {
    flexDirection: 'row',
    paddingHorizontal: Spacing.md,
    paddingVertical: 4,
    gap: 8,
  },
  smallStatBox: {
    flex: 1,
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
    borderWidth: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  smallStatBoxResolved: {
    backgroundColor: '#F0FDF4',
    borderColor: '#BBF7D0',
  },
  smallStatBoxActiveResolved: {
    borderColor: '#16A34A',
    backgroundColor: '#DCFCE7',
  },
  smallStatBoxPending: {
    backgroundColor: '#FFFBEB',
    borderColor: '#FDE68A',
  },
  smallStatBoxActivePending: {
    borderColor: '#F59E0B',
    backgroundColor: '#FEF3C7',
  },
  smallStatHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
  },
  statDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
  },
  smallStatLabel: {
    fontSize: 11,
    fontWeight: '700',
    color: Colors.textSecondary,
  },
  smallStatValue: {
    fontSize: 14,
    fontWeight: '900',
    letterSpacing: -0.3,
  },
  tabBar: {
    flexDirection: 'row',
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.xs,
    gap: Spacing.xs,
  },
  tabBtn: {
    flex: 1,
    paddingVertical: 8,
    alignItems: 'center',
    borderRadius: BorderRadius.md,
    backgroundColor: Colors.surface,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  activeTabBtn: {
    backgroundColor: Colors.primary,
    borderColor: Colors.primary,
  },
  activeTabBtnPending: {
    backgroundColor: Colors.status.pending,
    borderColor: Colors.status.pending,
  },
  activeTabBtnResolved: {
    backgroundColor: Colors.status.resolved,
    borderColor: Colors.status.resolved,
  },
  tabText: {
    fontSize: Typography.fontSize.xs,
    fontWeight: '700',
    color: Colors.textSecondary,
  },
  activeTabText: {
    color: Colors.textInverse,
  },
  activeTabTextPending: {
    color: Colors.textInverse,
  },
  activeTabTextResolved: {
    color: Colors.textInverse,
  },
  zonesContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: Spacing.md,
    paddingTop: 2,
    paddingBottom: Spacing.sm,
    gap: 8,
  },
  categoryFilterBanner: {
    paddingHorizontal: Spacing.md,
    paddingBottom: Spacing.xs,
  },
  categoryPill: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#EFF6FF',
    borderWidth: 1,
    borderColor: '#BFDBFE',
    borderRadius: BorderRadius.full,
    paddingHorizontal: 12,
    paddingVertical: 6,
    alignSelf: 'flex-start',
    maxWidth: '100%',
  },
  categoryPillText: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textSecondary,
    flexShrink: 1,
  },
  categoryPillBold: {
    fontWeight: '800',
    color: Colors.primary,
  },
  categoryPillClose: {
    marginLeft: 8,
    padding: 2,
  },
  zoneChip: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: BorderRadius.full,
    backgroundColor: Colors.surface,
    borderWidth: 1.5,
    borderColor: Colors.border,
  },
  zoneChipActive: {
    backgroundColor: '#E0F2FE',
    borderColor: Colors.primary,
  },
  zoneChipText: {
    fontSize: Typography.fontSize.sm,
    fontWeight: '600',
    color: Colors.textSecondary,
  },
  zoneChipTextActive: {
    color: Colors.primary,
    fontWeight: '800',
  },
  listContent: {
    padding: Spacing.md,
    paddingBottom: Spacing.xxl,
  },
  centerContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: Spacing.xl,
  },
  loadingMsg: {
    marginTop: Spacing.sm,
    color: Colors.textMuted,
    fontSize: Typography.fontSize.sm,
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
  modalTitle: {
    fontSize: Typography.fontSize.lg,
    fontWeight: '800',
    color: Colors.primary,
  },
  modalSubtitle: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textSecondary,
    fontWeight: '600',
  },
  closeBtn: {
    padding: 6,
  },
  modalBody: {
    padding: Spacing.md,
  },
  modalStatusRow: {
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
  modalStatusLabel: {
    fontSize: Typography.fontSize.sm,
    fontWeight: '700',
    color: Colors.textSecondary,
  },
  infoCard: {
    backgroundColor: Colors.surface,
    padding: Spacing.md,
    borderRadius: BorderRadius.md,
    marginBottom: Spacing.md,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  infoHeading: {
    fontSize: Typography.fontSize.sm,
    fontWeight: '800',
    color: Colors.textPrimary,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: Spacing.sm,
  },
  infoRow: {
    fontSize: Typography.fontSize.sm,
    color: Colors.textPrimary,
    lineHeight: 22,
  },
  bold: {
    fontWeight: '700',
    color: Colors.textSecondary,
  },
  fabBtn: {
    position: 'absolute',
    bottom: 20,
    right: 20,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.primary,
    paddingVertical: 12,
    paddingHorizontal: 18,
    borderRadius: BorderRadius.full,
    shadowColor: Colors.primaryDark,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.35,
    shadowRadius: 8,
    elevation: 6,
    borderWidth: 1.5,
    borderColor: '#34D399',
  },
  fabBtnText: {
    color: '#FFFFFF',
    fontSize: Typography.fontSize.sm,
    fontWeight: '700',
    letterSpacing: 0.3,
  },
});
