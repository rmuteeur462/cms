import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors, Spacing, BorderRadius, Typography } from '../../constants/theme';
import { StatusDistributionItem, AnalyticsSummary } from '../../api/complaints';

interface StatusDistributionChartProps {
  statusDistribution: StatusDistributionItem[];
  summary: AnalyticsSummary;
}

export const StatusDistributionChart: React.FC<StatusDistributionChartProps> = ({
  statusDistribution,
  summary,
}) => {
  const total = summary.total;
  const resolutionRate = total > 0 ? Math.round((summary.resolved / total) * 100) : 0;
  const pendingRate = total > 0 ? Math.round((summary.pending / total) * 100) : 0;

  return (
    <View style={styles.card}>
      <View style={styles.cardHeader}>
        <View style={styles.headerLeft}>
          <View style={[styles.iconBox, { backgroundColor: '#DCFCE7' }]}>
            <Ionicons name="pie-chart" size={18} color={Colors.status.resolved} />
          </View>
          <View>
            <Text style={styles.cardTitle}>Resolution Status Breakdown</Text>
            <Text style={styles.cardSubtitle}>
              Workflow status of all authorized complaints
            </Text>
          </View>
        </View>

        <View style={styles.rateBadge}>
          <Text style={styles.rateNumber}>{resolutionRate}%</Text>
          <Text style={styles.rateLabel}>Resolved</Text>
        </View>
      </View>

      {/* Segmented Visual Bar */}
      <View style={styles.barTrack}>
        <View
          style={[
            styles.barSegment,
            {
              width: `${resolutionRate}%`,
              backgroundColor: Colors.status.resolved,
            },
          ]}
        />
        <View
          style={[
            styles.barSegment,
            {
              width: `${pendingRate}%`,
              backgroundColor: Colors.status.pending,
            },
          ]}
        />
      </View>

      {/* Status Details Row */}
      <View style={styles.metricsRow}>
        {/* Resolved Metric */}
        <View style={[styles.metricBox, { backgroundColor: '#F0FDF4', borderColor: '#BBF7D0' }]}>
          <View style={styles.metricTop}>
            <View style={[styles.statusDot, { backgroundColor: Colors.status.resolved }]} />
            <Text style={styles.metricTitle}>RESOLVED</Text>
          </View>
          <Text style={[styles.metricCount, { color: Colors.status.resolved }]}>
            {summary.resolved.toLocaleString()}
          </Text>
          <Text style={styles.metricSub}>{resolutionRate}% of period</Text>
        </View>

        {/* Pending Metric */}
        <View style={[styles.metricBox, { backgroundColor: '#FFFBEB', borderColor: '#FDE68A' }]}>
          <View style={styles.metricTop}>
            <View style={[styles.statusDot, { backgroundColor: Colors.status.pending }]} />
            <Text style={styles.metricTitle}>PENDING</Text>
          </View>
          <Text style={[styles.metricCount, { color: Colors.status.pending }]}>
            {summary.pending.toLocaleString()}
          </Text>
          <Text style={styles.metricSub}>{pendingRate}% awaiting action</Text>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.md,
    marginBottom: Spacing.md,
    borderWidth: 1,
    borderColor: Colors.border,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.md,
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  iconBox: {
    width: 34,
    height: 34,
    borderRadius: BorderRadius.md,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: Spacing.sm,
  },
  cardTitle: {
    fontSize: Typography.fontSize.sm,
    fontWeight: '800',
    color: Colors.textPrimary,
  },
  cardSubtitle: {
    fontSize: Typography.fontSize.xs - 1,
    fontWeight: '600',
    color: Colors.textMuted,
    marginTop: 1,
  },
  rateBadge: {
    alignItems: 'center',
    backgroundColor: '#DCFCE7',
    paddingHorizontal: Spacing.sm,
    paddingVertical: 4,
    borderRadius: BorderRadius.md,
    borderWidth: 1,
    borderColor: '#BBF7D0',
  },
  rateNumber: {
    fontSize: Typography.fontSize.sm,
    fontWeight: '900',
    color: Colors.status.resolved,
  },
  rateLabel: {
    fontSize: 9,
    fontWeight: '700',
    color: Colors.status.resolved,
    textTransform: 'uppercase',
  },
  barTrack: {
    height: 10,
    backgroundColor: '#F1F5F9',
    borderRadius: 5,
    flexDirection: 'row',
    overflow: 'hidden',
    marginBottom: Spacing.md,
  },
  barSegment: {
    height: '100%',
  },
  metricsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  metricBox: {
    flex: 1,
    padding: Spacing.sm + 2,
    borderRadius: BorderRadius.md,
    borderWidth: 1,
    marginHorizontal: 3,
  },
  metricTop: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  statusDot: {
    width: 7,
    height: 7,
    borderRadius: 4,
    marginRight: 5,
  },
  metricTitle: {
    fontSize: 10,
    fontWeight: '800',
    color: Colors.textSecondary,
    letterSpacing: 0.5,
  },
  metricCount: {
    fontSize: Typography.fontSize.md,
    fontWeight: '900',
  },
  metricSub: {
    fontSize: 10,
    fontWeight: '600',
    color: Colors.textMuted,
    marginTop: 2,
  },
});
