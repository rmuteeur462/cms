import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
  Image,
  Alert,
  Modal,
  TextInput,
} from 'react-native';
import {
  CitizenComplaintsApi,
  CitizenTrackingResponse,
  CitizenTimelineStep,
} from '../../api/complaints';
import { Colors, Typography, Spacing, BorderRadius } from '../../constants/theme';
import { Ionicons } from '@expo/vector-icons';

interface CitizenTrackingScreenProps {
  navigation: any;
  route?: any;
}

export const CitizenTrackingScreen: React.FC<CitizenTrackingScreenProps> = ({
  navigation,
  route,
}) => {
  const initialComplaintId = route?.params?.complaintId;
  const [complaintId, setComplaintId] = useState<number | null>(initialComplaintId || null);
  const [trackingData, setTrackingData] = useState<CitizenTrackingResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);

  // Search by reference #
  const [searchTicket, setSearchTicket] = useState<string>('');

  // Feedback Modal State
  const [feedbackModalVisible, setFeedbackModalVisible] = useState<boolean>(false);
  const [isHappy, setIsHappy] = useState<boolean>(true);
  const [feedbackComment, setFeedbackComment] = useState<string>('');
  const [isSubmittingFeedback, setIsSubmittingFeedback] = useState<boolean>(false);

  const fetchTracking = useCallback(async (id: number) => {
    try {
      const data = await CitizenComplaintsApi.getComplaintTracking(id);
      setTrackingData(data);
    } catch (err: any) {
      console.warn('[TrackingScreen] Fetch error:', err);
      Alert.alert('Complaint Not Found', 'Could not retrieve tracking details for this ticket.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    if (complaintId) {
      fetchTracking(complaintId);
    } else {
      setLoading(false);
    }
  }, [complaintId, fetchTracking]);

  const onRefresh = () => {
    if (complaintId) {
      setRefreshing(true);
      fetchTracking(complaintId);
    }
  };

  const handleSearchSubmit = () => {
    const raw = searchTicket.trim();
    if (!raw) return;

    let targetId: number | null = null;
    if (raw.toUpperCase().startsWith('CMS-')) {
      targetId = parseInt(raw.substring(4), 10);
    } else if (/^\d+$/.test(raw)) {
      targetId = parseInt(raw, 10);
    }

    if (targetId && !isNaN(targetId)) {
      setComplaintId(targetId);
      setLoading(true);
      fetchTracking(targetId);
    } else {
      Alert.alert('Invalid Ticket', 'Please enter a valid ticket number like CMS-123 or 123.');
    }
  };

  const handleFeedbackSubmit = async () => {
    if (!complaintId) return;

    setIsSubmittingFeedback(true);
    try {
      const res = await CitizenComplaintsApi.submitFeedback(complaintId, {
        happy: isHappy,
        complaint_feedback: feedbackComment.trim(),
      });

      if (res.success) {
        Alert.alert('Feedback Recorded', 'Thank you! Your feedback has been recorded successfully.');
        setFeedbackModalVisible(false);
        fetchTracking(complaintId);
      }
    } catch (err: any) {
      Alert.alert('Error', err.response?.data?.message || 'Failed to submit feedback.');
    } finally {
      setIsSubmittingFeedback(false);
    }
  };

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.contentContainer}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={[Colors.primary]} />}
      showsVerticalScrollIndicator={false}
    >
      {/* Header Bar */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Track Complaint</Text>
        <Text style={styles.headerSubtitle}>
          Live status timeline & field resolution evidence
        </Text>
      </View>

      {/* Ticket Search Bar */}
      <View style={styles.searchBox}>
        <Ionicons name="search" size={18} color={Colors.textMuted} style={styles.searchIcon} />
        <TextInput
          style={styles.searchInput}
          placeholder="Enter ticket number (e.g. CMS-101)..."
          value={searchTicket}
          onChangeText={setSearchTicket}
          onSubmitEditing={handleSearchSubmit}
          returnKeyType="search"
          placeholderTextColor={Colors.textMuted}
        />
        <TouchableOpacity style={styles.trackSearchButton} onPress={handleSearchSubmit}>
          <Text style={styles.trackSearchButtonText}>Track</Text>
        </TouchableOpacity>
      </View>

      {loading ? (
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color={Colors.primary} />
          <Text style={styles.loadingText}>Loading tracking timeline...</Text>
        </View>
      ) : !trackingData ? (
        <View style={styles.centerContainer}>
          <Ionicons name="git-network-outline" size={54} color={Colors.textMuted} />
          <Text style={styles.emptyTitle}>Enter a Ticket Number to Track</Text>
          <Text style={styles.emptySubtitle}>
            Track any municipal complaint filed by your mobile number.
          </Text>
          <TouchableOpacity
            style={styles.browseButton}
            onPress={() => navigation.navigate('Complaints')}
          >
            <Text style={styles.browseButtonText}>Select from My Complaints</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <View style={styles.detailsWrapper}>
          {/* Ticket Information Card */}
          <View style={styles.summaryCard}>
            <View style={styles.cardHeaderRow}>
              <View>
                <Text style={styles.ticketBadge}>{trackingData.complaint.complaint_no}</Text>
                <Text style={styles.complaintCategory}>{trackingData.complaint.category}</Text>
              </View>
              <View
                style={[
                  styles.statusBadge,
                  trackingData.complaint.status === 'resolved'
                    ? styles.statusResolved
                    : styles.statusPending,
                ]}
              >
                <Text
                  style={[
                    styles.statusBadgeText,
                    trackingData.complaint.status === 'resolved'
                      ? styles.statusTextResolved
                      : styles.statusTextPending,
                  ]}
                >
                  {trackingData.complaint.status === 'resolved' ? 'Resolved' : 'Pending Action'}
                </Text>
              </View>
            </View>

            <Text style={styles.complaintTitle}>{trackingData.complaint.title}</Text>
            <Text style={styles.complaintDescription}>{trackingData.complaint.complaint_detail}</Text>

            <View style={styles.metaRow}>
              <Ionicons name="location-outline" size={14} color="#64748B" />
              <Text style={styles.metaText}>
                {trackingData.complaint.uc ? `${trackingData.complaint.uc}, ` : ''}
                {trackingData.complaint.location}
              </Text>
            </View>

            {/* Photos Row (Before / After) */}
            {(trackingData.complaint.before_image_url ||
              trackingData.timeline.find((t) => t.after_image_url)?.after_image_url) && (
              <View style={styles.photosSection}>
                <Text style={styles.photosHeading}>Photographic Evidence</Text>
                <View style={styles.photosRow}>
                  {trackingData.complaint.before_image_url && (
                    <View style={styles.photoBox}>
                      <Image
                        source={{ uri: trackingData.complaint.before_image_url }}
                        style={styles.photoImg}
                        resizeMode="cover"
                      />
                      <Text style={styles.photoCaption}>Reported Issue</Text>
                    </View>
                  )}
                  {trackingData.timeline.find((t) => t.after_image_url)?.after_image_url && (
                    <View style={styles.photoBox}>
                      <Image
                        source={{
                          uri: trackingData.timeline.find((t) => t.after_image_url)!.after_image_url!,
                        }}
                        style={styles.photoImg}
                        resizeMode="cover"
                      />
                      <Text style={[styles.photoCaption, { color: '#059669' }]}>After Resolution</Text>
                    </View>
                  )}
                </View>
              </View>
            )}

            {/* Feedback Button if Resolved */}
            {trackingData.can_give_feedback && !trackingData.feedback_given && (
              <TouchableOpacity
                style={styles.rateButton}
                onPress={() => setFeedbackModalVisible(true)}
                activeOpacity={0.85}
              >
                <Ionicons name="star" size={16} color="#FFFFFF" />
                <Text style={styles.rateButtonText}>Rate Resolution & Service</Text>
              </TouchableOpacity>
            )}
          </View>

          {/* 4-Stage Vertical Timeline */}
          <View style={styles.timelineCard}>
            <Text style={styles.timelineHeading}>Progress Tracking</Text>

            {trackingData.timeline.map((step: CitizenTimelineStep, index: number) => {
              const isLast = index === trackingData.timeline.length - 1;
              const isCompleted = step.status === 'completed';
              const isInProgress = step.status === 'in_progress';
              const isAvailable = step.status === 'available';

              return (
                <View key={step.step} style={styles.timelineRow}>
                  {/* Left Column: Icon + Connecting Line */}
                  <View style={styles.timelineLeftCol}>
                    <View
                      style={[
                        styles.stepIconWrap,
                        isCompleted && styles.stepCompleted,
                        isInProgress && styles.stepInProgress,
                        isAvailable && styles.stepAvailable,
                      ]}
                    >
                      <Ionicons
                        name={
                          isCompleted
                            ? 'checkmark'
                            : isInProgress
                            ? 'time'
                            : isAvailable
                            ? 'star'
                            : 'ellipse-outline'
                        }
                        size={14}
                        color={
                          isCompleted
                            ? '#FFFFFF'
                            : isInProgress
                            ? '#1E40AF'
                            : isAvailable
                            ? '#D97706'
                            : '#94A3B8'
                        }
                      />
                    </View>
                    {!isLast && (
                      <View
                        style={[
                          styles.timelineLine,
                          isCompleted && styles.timelineLineCompleted,
                        ]}
                      />
                    )}
                  </View>

                  {/* Right Column: Content */}
                  <View style={styles.timelineRightCol}>
                    <View style={styles.stepHeaderRow}>
                      <Text style={styles.stepTitle}>{step.title}</Text>
                      <View
                        style={[
                          styles.stepBadge,
                          isCompleted && styles.stepBadgeCompleted,
                          isInProgress && styles.stepBadgeInProgress,
                          isAvailable && styles.stepBadgeAvailable,
                        ]}
                      >
                        <Text
                          style={[
                            styles.stepBadgeText,
                            isCompleted && styles.stepBadgeTextCompleted,
                            isInProgress && styles.stepBadgeTextInProgress,
                            isAvailable && styles.stepBadgeTextAvailable,
                          ]}
                        >
                          {step.badge}
                        </Text>
                      </View>
                    </View>

                    <Text style={styles.stepSubtitle}>{step.subtitle}</Text>
                    <Text style={styles.stepDescription}>{step.description}</Text>

                    {step.feedback_data && (
                      <View style={styles.feedbackRecordedBox}>
                        <View style={styles.feedbackRatingRow}>
                          <Ionicons
                            name={step.feedback_data.happy ? 'happy' : 'sad'}
                            size={16}
                            color={step.feedback_data.happy ? '#059669' : '#DC2626'}
                          />
                          <Text
                            style={[
                              styles.feedbackRatingText,
                              { color: step.feedback_data.happy ? '#059669' : '#DC2626' },
                            ]}
                          >
                            Citizen Rating: {step.feedback_data.happy ? 'Satisfied' : 'Not Satisfied'}
                          </Text>
                        </View>
                        {step.feedback_data.comment ? (
                          <Text style={styles.feedbackCommentText}>
                            "{step.feedback_data.comment}"
                          </Text>
                        ) : null}
                      </View>
                    )}
                  </View>
                </View>
              );
            })}
          </View>
        </View>
      )}

      {/* Citizen Feedback Modal */}
      <Modal
        visible={feedbackModalVisible}
        transparent
        animationType="slide"
        onRequestClose={() => setFeedbackModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Rate WSSP Service</Text>
              <TouchableOpacity onPress={() => setFeedbackModalVisible(false)}>
                <Ionicons name="close" size={22} color="#64748B" />
              </TouchableOpacity>
            </View>

            <Text style={styles.modalSubtitle}>
              Are you satisfied with the resolution of ticket #{trackingData?.complaint?.complaint_no}?
            </Text>

            <View style={styles.satisfactionRow}>
              <TouchableOpacity
                style={[styles.satOption, isHappy && styles.satOptionSelectedYes]}
                onPress={() => setIsHappy(true)}
              >
                <Ionicons
                  name="happy"
                  size={24}
                  color={isHappy ? '#059669' : '#64748B'}
                />
                <Text style={[styles.satOptionText, isHappy && styles.satOptionTextYes]}>
                  Yes, Satisfied
                </Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.satOption, !isHappy && styles.satOptionSelectedNo]}
                onPress={() => setIsHappy(false)}
              >
                <Ionicons
                  name="sad"
                  size={24}
                  color={!isHappy ? '#DC2626' : '#64748B'}
                />
                <Text style={[styles.satOptionText, !isHappy && styles.satOptionTextNo]}>
                  No, Unsatisfied
                </Text>
              </TouchableOpacity>
            </View>

            <Text style={styles.commentLabel}>Additional Comments (Optional)</Text>
            <TextInput
              style={styles.commentInput}
              placeholder="Provide any additional feedback or remarks for WSSP management..."
              value={feedbackComment}
              onChangeText={setFeedbackComment}
              multiline
              numberOfLines={3}
              placeholderTextColor={Colors.textMuted}
            />

            <TouchableOpacity
              style={[styles.modalSubmitButton, isSubmittingFeedback && styles.modalSubmitDisabled]}
              onPress={handleFeedbackSubmit}
              disabled={isSubmittingFeedback}
            >
              {isSubmittingFeedback ? (
                <ActivityIndicator color="#FFFFFF" size="small" />
              ) : (
                <Text style={styles.modalSubmitText}>Submit Feedback</Text>
              )}
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  contentContainer: {
    paddingBottom: Spacing.xxl + 30,
  },
  header: {
    backgroundColor: '#0F2744',
    paddingHorizontal: Spacing.lg,
    paddingTop: 16,
    paddingBottom: 22,
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
    marginTop: -12,
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
    marginRight: 6,
  },
  searchInput: {
    flex: 1,
    fontSize: Typography.fontSize.sm,
    color: '#1E293B',
  },
  trackSearchButton: {
    backgroundColor: '#1E40AF',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: BorderRadius.sm,
  },
  trackSearchButtonText: {
    color: '#FFFFFF',
    fontSize: Typography.fontSize.xs,
    fontWeight: '700',
  },
  centerContainer: {
    padding: 30,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 30,
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
    marginTop: 4,
  },
  browseButton: {
    marginTop: 16,
    backgroundColor: '#1E40AF',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: BorderRadius.md,
  },
  browseButtonText: {
    color: '#FFFFFF',
    fontSize: Typography.fontSize.xs,
    fontWeight: '700',
  },
  detailsWrapper: {
    paddingHorizontal: Spacing.md,
    marginTop: 14,
  },
  summaryCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: BorderRadius.md,
    padding: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    marginBottom: 12,
  },
  cardHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 6,
  },
  ticketBadge: {
    fontSize: Typography.fontSize.sm,
    fontWeight: '800',
    color: '#1E40AF',
  },
  complaintCategory: {
    fontSize: 11,
    color: '#64748B',
    fontWeight: '600',
    marginTop: 1,
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 3,
    borderRadius: 12,
  },
  statusPending: {
    backgroundColor: '#FEF3C7',
  },
  statusResolved: {
    backgroundColor: '#D1FAE5',
  },
  statusBadgeText: {
    fontSize: 11,
    fontWeight: '700',
  },
  statusTextPending: {
    color: '#92400E',
  },
  statusTextResolved: {
    color: '#065F46',
  },
  complaintTitle: {
    fontSize: Typography.fontSize.md,
    fontWeight: '700',
    color: '#1E293B',
    marginTop: 6,
  },
  complaintDescription: {
    fontSize: Typography.fontSize.xs,
    color: '#475569',
    lineHeight: 18,
    marginTop: 4,
    marginBottom: 8,
  },
  metaRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  metaText: {
    fontSize: 11,
    color: '#64748B',
  },
  photosSection: {
    marginTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#F1F5F9',
    paddingTop: 10,
  },
  photosHeading: {
    fontSize: Typography.fontSize.xs,
    fontWeight: '700',
    color: '#1E293B',
    marginBottom: 8,
  },
  photosRow: {
    flexDirection: 'row',
    gap: 12,
  },
  photoBox: {
    alignItems: 'center',
  },
  photoImg: {
    width: 90,
    height: 90,
    borderRadius: BorderRadius.md,
    borderWidth: 1,
    borderColor: '#CBD5E1',
  },
  photoCaption: {
    fontSize: 10,
    color: '#475569',
    marginTop: 4,
    fontWeight: '600',
  },
  rateButton: {
    backgroundColor: '#D97706',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
    paddingVertical: 10,
    borderRadius: BorderRadius.md,
    marginTop: 14,
  },
  rateButtonText: {
    color: '#FFFFFF',
    fontSize: Typography.fontSize.xs,
    fontWeight: '700',
  },
  timelineCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: BorderRadius.md,
    padding: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  timelineHeading: {
    fontSize: Typography.fontSize.md,
    fontWeight: '700',
    color: '#1E293B',
    marginBottom: 16,
  },
  timelineRow: {
    flexDirection: 'row',
    marginBottom: 10,
  },
  timelineLeftCol: {
    alignItems: 'center',
    width: 30,
  },
  stepIconWrap: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#F1F5F9',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: '#CBD5E1',
  },
  stepCompleted: {
    backgroundColor: '#1E40AF',
    borderColor: '#1E40AF',
  },
  stepInProgress: {
    backgroundColor: '#EFF6FF',
    borderColor: '#1E40AF',
  },
  stepAvailable: {
    backgroundColor: '#FFFBEB',
    borderColor: '#F59E0B',
  },
  timelineLine: {
    width: 2,
    flex: 1,
    backgroundColor: '#E2E8F0',
    marginVertical: 4,
  },
  timelineLineCompleted: {
    backgroundColor: '#1E40AF',
  },
  timelineRightCol: {
    flex: 1,
    paddingLeft: 10,
    paddingBottom: 16,
  },
  stepHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  stepTitle: {
    fontSize: Typography.fontSize.sm,
    fontWeight: '700',
    color: '#1E293B',
  },
  stepBadge: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8,
    backgroundColor: '#F1F5F9',
  },
  stepBadgeCompleted: {
    backgroundColor: '#EFF6FF',
  },
  stepBadgeInProgress: {
    backgroundColor: '#FEF3C7',
  },
  stepBadgeAvailable: {
    backgroundColor: '#FFFBEB',
  },
  stepBadgeText: {
    fontSize: 9,
    fontWeight: '700',
    color: '#64748B',
  },
  stepBadgeTextCompleted: {
    color: '#1E40AF',
  },
  stepBadgeTextInProgress: {
    color: '#92400E',
  },
  stepBadgeTextAvailable: {
    color: '#D97706',
  },
  stepSubtitle: {
    fontSize: 11,
    color: '#64748B',
    marginTop: 2,
  },
  stepDescription: {
    fontSize: Typography.fontSize.xs,
    color: '#475569',
    lineHeight: 18,
    marginTop: 4,
  },
  feedbackRecordedBox: {
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    borderRadius: BorderRadius.sm,
    padding: 8,
    marginTop: 8,
  },
  feedbackRatingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  feedbackRatingText: {
    fontSize: 11,
    fontWeight: '700',
  },
  feedbackCommentText: {
    fontSize: 11,
    color: '#475569',
    fontStyle: 'italic',
    marginTop: 4,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: Spacing.lg,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  modalTitle: {
    fontSize: Typography.fontSize.md,
    fontWeight: '800',
    color: '#1E293B',
  },
  modalSubtitle: {
    fontSize: Typography.fontSize.xs,
    color: '#64748B',
    marginBottom: 16,
  },
  satisfactionRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
  },
  satOption: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#CBD5E1',
    borderRadius: BorderRadius.md,
    paddingVertical: 12,
    alignItems: 'center',
    backgroundColor: '#F8FAFC',
  },
  satOptionSelectedYes: {
    borderColor: '#059669',
    backgroundColor: '#ECFDF5',
  },
  satOptionSelectedNo: {
    borderColor: '#DC2626',
    backgroundColor: '#FEF2F2',
  },
  satOptionText: {
    fontSize: Typography.fontSize.xs,
    fontWeight: '600',
    color: '#475569',
    marginTop: 4,
  },
  satOptionTextYes: {
    color: '#059669',
    fontWeight: '700',
  },
  satOptionTextNo: {
    color: '#DC2626',
    fontWeight: '700',
  },
  commentLabel: {
    fontSize: Typography.fontSize.xs,
    fontWeight: '600',
    color: '#475569',
    marginBottom: 6,
  },
  commentInput: {
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#CBD5E1',
    borderRadius: BorderRadius.md,
    padding: 10,
    fontSize: Typography.fontSize.xs,
    color: '#1E293B',
    minHeight: 70,
    textAlignVertical: 'top',
    marginBottom: 16,
  },
  modalSubmitButton: {
    backgroundColor: '#1E40AF',
    borderRadius: BorderRadius.md,
    paddingVertical: 12,
    alignItems: 'center',
  },
  modalSubmitDisabled: {
    opacity: 0.6,
  },
  modalSubmitText: {
    color: '#FFFFFF',
    fontSize: Typography.fontSize.sm,
    fontWeight: '700',
  },
});

