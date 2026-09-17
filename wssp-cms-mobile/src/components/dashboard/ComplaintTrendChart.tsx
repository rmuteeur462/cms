import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors, Spacing, BorderRadius, Typography } from '../../constants/theme';
import { TrendItem } from '../../api/complaints';

interface ComplaintTrendChartProps {
  data: TrendItem[];
  periodLabel: string;
  isMonthlyView?: boolean;
}

export const ComplaintTrendChart: React.FC<ComplaintTrendChartProps> = ({
  data,
  periodLabel,
  isMonthlyView = false,
}) => {
  const [selectedBar, setSelectedBar] = useState<TrendItem | null>(null);

  if (!data || data.length === 0) {
    return (
      <View style={styles.emptyContainer}>
        <Ionicons name="bar-chart-outline" size={32} color={Colors.textMuted} />
        <Text style={styles.emptyText}>No trend activity recorded for this period.</Text>
      </View>
    );
  }

  const maxCount = Math.max(...data.map((d) => d.count), 1);
  const totalCount = data.reduce((acc, curr) => acc + curr.count, 0);

  return (
    <View style={styles.card}>
      <View style={styles.cardHeader}>
        <View style={styles.headerLeft}>
          <View style={[styles.iconBox, { backgroundColor: '#EFF6FF' }]}>
            <Ionicons name="trending-up-outline" size={18} color={Colors.primary} />
          </View>
          <View>
            <Text style={styles.cardTitle}>Complaint Frequency Trend</Text>
            <Text style={styles.cardSubtitle}>
              {periodLabel} • {totalCount.toLocaleString()} total logged
            </Text>
          </View>
        </View>

        {selectedBar && (
          <View style={styles.tooltipBadge}>
            <Text style={styles.tooltipText}>
              {selectedBar.full_label || selectedBar.label}:{' '}
              <Text style={styles.tooltipBold}>{selectedBar.count.toLocaleString()}</Text>
            </Text>
          </View>
        )}
      </View>

      {/* Bar Chart Scroll Area */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.chartScroll}
      >
        <View style={styles.chartArea}>
          {data.map((item, index) => {
            const heightPercent = maxCount > 0 ? (item.count / maxCount) * 100 : 0;
            const isSelected = selectedBar?.label === item.label;
            const isPeak = item.count === maxCount && item.count > 0;

            return (
              <TouchableOpacity
                key={index}
                style={styles.barColumn}
                onPress={() => setSelectedBar(item)}
                activeOpacity={0.7}
              >
                {/* Value on top if peak or selected */}
                <View style={styles.valWrapper}>
                  {(isSelected || isPeak) && item.count > 0 && (
                    <Text style={[styles.barValText, isPeak && styles.peakValText]}>
                      {item.count > 999 ? `${(item.count / 1000).toFixed(1)}k` : item.count}
                    </Text>
                  )}
                </View>

                {/* Track and fill bar */}
                <View style={styles.barTrack}>
                  <View
                    style={[
                      styles.barFill,
                      { height: `${Math.max(heightPercent, item.count > 0 ? 6 : 2)}%` },
                      isSelected && styles.barFillSelected,
                      isPeak && styles.barFillPeak,
                      item.count === 0 && styles.barFillZero,
                    ]}
                  />
                </View>

                {/* X-axis Label */}
                <Text
                  style={[
                    styles.barLabel,
                    isSelected && styles.barLabelSelected,
                    isPeak && styles.barLabelPeak,
                  ]}
                  numberOfLines={1}
                >
                  {item.label}
                </Text>
              </TouchableOpacity>
            );
          })}
        </View>
      </ScrollView>

      {/* Footer Legend */}
      <View style={styles.legendRow}>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, { backgroundColor: Colors.primary }]} />
          <Text style={styles.legendLabel}>Frequency</Text>
        </View>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, { backgroundColor: Colors.secondary }]} />
          <Text style={styles.legendLabel}>Peak Volume ({maxCount.toLocaleString()})</Text>
        </View>
        <Text style={styles.tapHint}>Tap any bar for details</Text>
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
    marginBottom: Spacing.sm,
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
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
  tooltipBadge: {
    backgroundColor: Colors.primaryDark,
    paddingHorizontal: Spacing.sm,
    paddingVertical: 4,
    borderRadius: BorderRadius.sm,
  },
  tooltipText: {
    fontSize: 11,
    color: '#FFFFFF',
    fontWeight: '600',
  },
  tooltipBold: {
    fontWeight: '800',
    color: '#93C5FD',
  },
  chartScroll: {
    paddingVertical: Spacing.sm,
  },
  chartArea: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    height: 140,
    paddingTop: 20,
  },
  barColumn: {
    alignItems: 'center',
    width: 32,
    marginHorizontal: 3,
    height: '100%',
    justifyContent: 'flex-end',
  },
  valWrapper: {
    height: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  barValText: {
    fontSize: 9,
    fontWeight: '700',
    color: Colors.primary,
  },
  peakValText: {
    color: Colors.secondary,
    fontWeight: '900',
  },
  barTrack: {
    width: 14,
    height: 95,
    backgroundColor: '#F1F5F9',
    borderRadius: 7,
    justifyContent: 'flex-end',
    overflow: 'hidden',
    marginVertical: 4,
  },
  barFill: {
    width: '100%',
    backgroundColor: Colors.primary,
    borderRadius: 7,
  },
  barFillSelected: {
    backgroundColor: Colors.primaryDark,
  },
  barFillPeak: {
    backgroundColor: Colors.secondary,
  },
  barFillZero: {
    backgroundColor: '#E2E8F0',
  },
  barLabel: {
    fontSize: 10,
    fontWeight: '600',
    color: Colors.textMuted,
    marginTop: 2,
    textAlign: 'center',
  },
  barLabelSelected: {
    fontWeight: '800',
    color: Colors.primaryDark,
  },
  barLabelPeak: {
    color: Colors.secondary,
    fontWeight: '800',
  },
  legendRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: Spacing.sm,
    paddingTop: Spacing.sm,
    borderTopWidth: 1,
    borderTopColor: '#F1F5F9',
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: Spacing.md,
  },
  legendDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 4,
  },
  legendLabel: {
    fontSize: 11,
    fontWeight: '600',
    color: Colors.textSecondary,
  },
  tapHint: {
    marginLeft: 'auto',
    fontSize: 10,
    color: Colors.textMuted,
    fontStyle: 'italic',
  },
  emptyContainer: {
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.xl,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: Spacing.md,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  emptyText: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textMuted,
    fontWeight: '600',
    marginTop: Spacing.sm,
  },
});
