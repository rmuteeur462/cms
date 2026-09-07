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

export const ComplaintsScreen: React.FC = () => {
  const { user } = useAuth();

  const [complaints, setComplaints] = useState<ComplaintSummaryItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'pending' | 'resolved'>('all');
  const [selectedLocationId, setSelectedLocationId] = useState<number | undefined>(undefined);
  const [totalCount, setTotalCount] = useState<number>(0);

  // Detail Modal
  const [selectedComplaint, setSelectedComplaint] = useState<any | null>(null);
  const [detailModalVisible, setDetailModalVisible] = useState<boolean>(false);
  const [loadingDetail, setLoadingDetail] = useState<boolean>(false);

  const fetchComplaints = async () => {
    try {
      const data = await ComplaintsApi.getComplaints({
        search: searchQuery.trim() || undefined,
        status: statusFilter,
        location_id: selectedLocationId,
        page: 1,
      });
      setComplaints(data.results);
      setTotalCount(data.total_count);
    } catch (err) {
      console.warn('[ComplaintsScreen] Load error:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchComplaints();
  }, [statusFilter, selectedLocationId]);

  const handleSearchSubmit = () => {
    setLoading(true);
    fetchComplaints();
  };

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    fetchComplaints();
  }, [statusFilter, selectedLocationId, searchQuery]);

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
            <TouchableOpacity onPress={() => { setSearchQuery(''); fetchComplaints(); }}>
              <Ionicons name="close-circle" size={18} color={Colors.textMuted} />
            </TouchableOpacity>
          ) : null}
        </View>
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
            Pending
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tabBtn, statusFilter === 'resolved' && styles.activeTabBtnResolved]}
          onPress={() => setStatusFilter('resolved')}
          activeOpacity={0.7}
        >
          <Text style={[styles.tabText, statusFilter === 'resolved' && styles.activeTabTextResolved]}>
            Resolved
          </Text>
        </TouchableOpacity>
      </View>

      {/* Zone Selector Chips */}
      {user?.allowed_locations && user.allowed_locations.length > 1 && (
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.zonesScroll}
          style={styles.zonesContainer}
        >
          <TouchableOpacity
            style={[styles.zoneChip, selectedLocationId === undefined && styles.zoneChipActive]}
            onPress={() => setSelectedLocationId(undefined)}
            activeOpacity={0.7}
          >
            <Text style={[styles.zoneChipText, selectedLocationId === undefined && styles.zoneChipTextActive]}>
              All Zones
            </Text>
          </TouchableOpacity>
          {user.allowed_locations.map((loc) => (
            <TouchableOpacity
              key={loc.id}
              style={[styles.zoneChip, selectedLocationId === loc.id && styles.zoneChipActive]}
              onPress={() => setSelectedLocationId(loc.id)}
              activeOpacity={0.7}
            >
              <Text style={[styles.zoneChipText, selectedLocationId === loc.id && styles.zoneChipTextActive]}>
                {loc.name}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
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
                setSelectedLocationId(undefined);
                setSearchQuery('');
              }}
            />
          }
        />
      )}

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
    maxHeight: 40,
    marginBottom: Spacing.xs,
  },
  zonesScroll: {
    paddingHorizontal: Spacing.md,
    gap: Spacing.xs,
    alignItems: 'center',
  },
  zoneChip: {
    paddingHorizontal: 12,
    paddingVertical: 5,
    borderRadius: BorderRadius.full,
    backgroundColor: Colors.surface,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  zoneChipActive: {
    backgroundColor: '#E0F2FE',
    borderColor: Colors.secondary,
  },
  zoneChipText: {
    fontSize: 11,
    fontWeight: '600',
    color: Colors.textSecondary,
  },
  zoneChipTextActive: {
    color: Colors.secondary,
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
});
