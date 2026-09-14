import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Colors, Spacing, BorderRadius, Typography } from '../../constants/theme';
import { StatusBadge } from './StatusBadge';
import { ComplaintSummaryItem } from '../../api/complaints';
import { Ionicons } from '@expo/vector-icons';
import { Formatters } from '../../utils/formatters';

interface ComplaintCardProps {
  complaint: ComplaintSummaryItem;
  onPress?: () => void;
}

export const ComplaintCard: React.FC<ComplaintCardProps> = ({ complaint, onPress }) => {
  return (
    <TouchableOpacity
      activeOpacity={0.8}
      onPress={onPress}
      style={styles.card}
    >
      {/* Header Row: ID + Status Badge */}
      <View style={styles.headerRow}>
        <View style={styles.idContainer}>
          <Ionicons name="document-text-outline" size={16} color={Colors.primary} style={{ marginRight: 4 }} />
          <Text style={styles.complaintNoText}>{complaint.complaint_no}</Text>
        </View>
        <StatusBadge status={complaint.status} />
      </View>

      {/* Main Issue Title */}
      <Text style={styles.titleText} numberOfLines={2}>
        {complaint.title}
      </Text>

      {/* Category & Location Badges */}
      <View style={styles.metaRow}>
        <View style={styles.categoryPill}>
          <Text style={styles.categoryText}>{complaint.category}</Text>
        </View>
        <View style={styles.locationContainer}>
          <Ionicons name="location-sharp" size={13} color={Colors.textMuted} style={{ marginRight: 2 }} />
          <Text style={styles.locationText} numberOfLines={1}>
            {complaint.location} • {complaint.uc}
          </Text>
        </View>
      </View>

      {/* Footer Row: Citizen & Date */}
      <View style={styles.footerRow}>
        <View style={styles.citizenContainer}>
          <Ionicons name="person-outline" size={13} color={Colors.textSecondary} style={{ marginRight: 4 }} />
          <Text style={styles.citizenText} numberOfLines={1}>
            {complaint.citizen_name} ({Formatters.formatPhone(complaint.cell_number)})
          </Text>
        </View>
        <Text style={styles.dateText}>{Formatters.formatDate(complaint.date)}</Text>
      </View>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.md,
    padding: 10,
    paddingHorizontal: 12,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: Colors.border,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.03,
    shadowRadius: 4,
    elevation: 1,
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  idContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F0FDF4',
    paddingVertical: 2,
    paddingHorizontal: 6,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#DCFCE7',
  },
  complaintNoText: {
    fontSize: 10,
    fontWeight: '800',
    color: Colors.primary,
    letterSpacing: 0.4,
  },
  titleText: {
    fontSize: 13,
    fontWeight: '700',
    color: Colors.textPrimary,
    lineHeight: 19,
    marginBottom: 4,
  },
  metaRow: {
    flexDirection: 'row',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: 4,
    marginBottom: 4,
  },
  categoryPill: {
    backgroundColor: '#F1F5F9',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  categoryText: {
    fontSize: 10,
    fontWeight: '700',
    color: Colors.textSecondary,
  },
  locationContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  locationText: {
    fontSize: 11,
    color: Colors.textSecondary,
    fontWeight: '500',
  },
  footerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingTop: 4,
    borderTopWidth: 1,
    borderTopColor: '#F1F5F9',
    marginTop: 2,
  },
  citizenContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    marginRight: 8,
  },
  citizenText: {
    fontSize: 11,
    color: Colors.textSecondary,
    fontWeight: '500',
  },
  dateText: {
    fontSize: 10,
    color: Colors.textMuted,
    fontWeight: '600',
  },
});
