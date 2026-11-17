import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
  TextInput,
  Image,
} from 'react-native';
import { CitizenComplaintsApi, CitizenComplaintItem } from '../../api/complaints';
import { Colors, Typography, Spacing, BorderRadius } from '../../constants/theme';
import { Ionicons } from '@expo/vector-icons';

interface CitizenComplaintsScreenProps {
  navigation: any;
  route?: any;
}

export const CitizenComplaintsScreen: React.FC<CitizenComplaintsScreenProps> = ({
  navigation,
  route,
}) => {
  const initialStatus = route?.params?.status || 'all';
  const [activeFilter, setActiveFilter] = useState<string>(initialStatus);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [complaints, setComplaints] = useState<CitizenComplaintItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [totalCount, setTotalCount] = useState<number>(0);

  const fetchComplaints = useCallback(async () => {
    try {
      const params: any = {};
      if (activeFilter !== 'all') {
        params.status = activeFilter;
      }
      if (searchQuery.trim()) {
        params.q = searchQuery.trim();
      }

      const res = await CitizenComplaintsApi.getComplaints(params);
      setComplaints(res.results || []);
      setTotalCount(res.count || 0);
    } catch (err) {
      console.warn('[CitizenComplaintsScreen] Failed to fetch complaints:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [activeFilter, searchQuery]);

  useEffect(() => {
    fetchComplaints();
  }, [fetchComplaints]);

  const onRefresh = () => {
    setRefreshing(true);
    fetchComplaints();
  };

  const renderItem = ({ item }: { item: CitizenComplaintItem }) => {
    const isResolved = item.status === 'resolved';

    return (
      <TouchableOpacity
        style={styles.card}
        onPress={() => navigation.navigate('Tracking', { complaintId: item.id })}
        activeOpacity={0.75}
      >
        <View style={styles.cardTopRow}>
          <View style={styles.refGroup}>
            <Text style={styles.complaintNo}>{item.complaint_no}</Text>
            <Text style={styles.categoryBadge}>{item.category}</Text>
          </View>
          <View
            style={[
              styles.statusBadge,
              isResolved ? styles.statusBadgeResolved : styles.statusBadgePending,
            ]}
          >
            <Text
              style={[
                styles.statusBadgeText,
                isResolved ? styles.statusTextResolved : styles.statusTextPending,
              ]}
            >
              {isResolved ? 'Resolved' : 'Pending'}
            </Text>
          </View>
        </View>

        <Text style={styles.titleText} numberOfLines={1}>
          {item.title || item.subcategory || item.category}
        </Text>
        <Text style={styles.detailText} numberOfLines={2}>
          {item.complaint_detail}
        </Text>

        {item.before_image_url && (
          <View style={styles.imageThumbnailRow}>
            <Image
              source={{ uri: item.before_image_url }}
              style={styles.imageThumbnail}
              resizeMode="cover"
            />
            <Text style={styles.attachmentLabel}>Photo Attached</Text>
          </View>
        )}

        <View style={styles.cardBottomRow}>
          <View style={styles.locationContainer}>
            <Ionicons name="location-outline" size={14} color={Colors.textMuted} />
            <Text style={styles.locationText} numberOfLines={1}>
              {item.uc_name ? `${item.uc_name}, ${item.location_name}` : item.location_name}
            </Text>
          </View>

          <View style={styles.actionGroup}>
            {isResolved && !item.has_feedback && (
              <View style={styles.feedbackPill}>
                <Ionicons name="star-outline" size={12} color="#D97706" />
                <Text style={styles.feedbackPillText}>Rate Service</Text>
              </View>
            )}
            <View style={styles.trackButton}>
              <Text style={styles.trackButtonText}>Track</Text>
              <Ionicons name="chevron-forward" size={14} color="#1E40AF" />
            </View>
          </View>
        </View>
      </TouchableOpacity>
    );
  };

  return (
    <View style={styles.container}>
      {/* Header Bar */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>My Complaints</Text>
        <Text style={styles.headerSubtitle}>{totalCount} Total Registered</Text>
      </View>

      {/* Search Input */}
      <View style={styles.searchBox}>
        <Ionicons name="search-outline" size={18} color={Colors.textMuted} style={styles.searchIcon} />
        <TextInput
          style={styles.searchInput}
          placeholder="Search by ticket # or keyword..."
          value={searchQuery}
          onChangeText={setSearchQuery}
          returnKeyType="search"
          placeholderTextColor={Colors.textMuted}
        />
        {searchQuery.length > 0 && (
          <TouchableOpacity onPress={() => setSearchQuery('')}>
            <Ionicons name="close-circle" size={18} color={Colors.textMuted} />
          </TouchableOpacity>
        )}
      </View>

      {/* Status Filter Chips */}
      <View style={styles.filterRow}>
        <TouchableOpacity
          style={[styles.filterChip, activeFilter === 'all' && styles.filterChipActive]}
          onPress={() => setActiveFilter('all')}
        >
          <Text style={[styles.filterText, activeFilter === 'all' && styles.filterTextActive]}>
            All
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.filterChip, activeFilter === 'pending' && styles.filterChipActive]}
          onPress={() => setActiveFilter('pending')}
        >
          <Text style={[styles.filterText, activeFilter === 'pending' && styles.filterTextActive]}>
            Pending
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.filterChip, activeFilter === 'resolved' && styles.filterChipActive]}
          onPress={() => setActiveFilter('resolved')}
        >
          <Text style={[styles.filterText, activeFilter === 'resolved' && styles.filterTextActive]}>
            Resolved
          </Text>
        </TouchableOpacity>
      </View>

      {/* Complaints List */}
      {loading ? (
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color={Colors.primary} />
          <Text style={styles.loadingText}>Loading complaints...</Text>
        </View>
      ) : complaints.length === 0 ? (
        <View style={styles.centerContainer}>
          <Ionicons name="file-tray-outline" size={48} color={Colors.textMuted} />
          <Text style={styles.emptyTitle}>No Complaints Found</Text>
          <Text style={styles.emptySubtitle}>
            {searchQuery
              ? 'No complaints match your search query.'
              : 'You have not submitted any complaints in this category.'}
          </Text>
          <TouchableOpacity
            style={styles.newButton}
            onPress={() => navigation.navigate('NewComplaint')}
          >
            <Text style={styles.newButtonText}>Register New Complaint</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <FlatList
          data={complaints}
          keyExtractor={(item) => item.id.toString()}
          renderItem={renderItem}
          contentContainerStyle={styles.listContent}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={[Colors.primary]} />
          }
          showsVerticalScrollIndicator={false}
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  header: {
    backgroundColor: '#0F2744',
    paddingHorizontal: Spacing.lg,
    paddingTop: 16,
    paddingBottom: 20,
  },
  headerTitle: {
    fontSize: Typography.fontSize.xl,
    fontWeight: '800',
    color: '#FFFFFF',
  },
  headerSubtitle: {
    fontSize: Typography.fontSize.xs,
    color: '#93C5FD',
    marginTop: 2,
  },
  searchBox: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    marginHorizontal: Spacing.lg,
    marginTop: -14,
    borderRadius: BorderRadius.md,
    paddingHorizontal: 12,
    height: 44,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  searchIcon: {
    marginRight: 8,
  },
  searchInput: {
    flex: 1,
    fontSize: Typography.fontSize.sm,
    color: '#1E293B',
  },
  filterRow: {
    flexDirection: 'row',
    paddingHorizontal: Spacing.lg,
    marginTop: 12,
    marginBottom: 8,
    gap: 8,
  },
  filterChip: {
    paddingHorizontal: 16,
    paddingVertical: 7,
    borderRadius: 20,
    backgroundColor: '#E2E8F0',
  },
  filterChipActive: {
    backgroundColor: '#1E40AF',
  },
  filterText: {
    fontSize: Typography.fontSize.xs,
    fontWeight: '600',
    color: '#475569',
  },
  filterTextActive: {
    color: '#FFFFFF',
    fontWeight: '700',
  },
  listContent: {
    paddingHorizontal: Spacing.lg,
    paddingTop: 6,
    paddingBottom: Spacing.xxl + 20,
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: BorderRadius.md,
    padding: 14,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.03,
    shadowRadius: 3,
    elevation: 1,
  },
  cardTopRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  refGroup: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  complaintNo: {
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
  titleText: {
    fontSize: Typography.fontSize.sm,
    fontWeight: '700',
    color: '#1E293B',
    marginBottom: 4,
  },
  detailText: {
    fontSize: Typography.fontSize.xs,
    color: '#64748B',
    lineHeight: 18,
    marginBottom: 8,
  },
  imageThumbnailRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 8,
  },
  imageThumbnail: {
    width: 38,
    height: 38,
    borderRadius: 6,
  },
  attachmentLabel: {
    fontSize: 11,
    color: '#64748B',
    fontStyle: 'italic',
  },
  cardBottomRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#F1F5F9',
    paddingTop: 8,
  },
  locationContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    flex: 1,
  },
  locationText: {
    fontSize: 11,
    color: '#64748B',
  },
  actionGroup: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  feedbackPill: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    backgroundColor: '#FEF3C7',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 12,
  },
  feedbackPillText: {
    fontSize: 10,
    fontWeight: '700',
    color: '#D97706',
  },
  trackButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 2,
  },
  trackButtonText: {
    fontSize: 11,
    fontWeight: '700',
    color: '#1E40AF',
  },
  centerContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 30,
  },
  loadingText: {
    marginTop: 10,
    fontSize: Typography.fontSize.sm,
    color: '#64748B',
  },
  emptyTitle: {
    fontSize: Typography.fontSize.md,
    fontWeight: '700',
    color: '#1E293B',
    marginTop: 12,
  },
  emptySubtitle: {
    fontSize: Typography.fontSize.xs,
    color: '#64748B',
    textAlign: 'center',
    marginTop: 6,
    lineHeight: 18,
  },
  newButton: {
    marginTop: 18,
    backgroundColor: '#1E40AF',
    paddingHorizontal: 18,
    paddingVertical: 10,
    borderRadius: BorderRadius.md,
  },
  newButtonText: {
    color: '#FFFFFF',
    fontSize: Typography.fontSize.xs,
    fontWeight: '700',
  },
});

