import React, { useState, useMemo } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors, Spacing, BorderRadius, Typography } from '../../constants/theme';
import { TrendItem } from '../../api/complaints';

interface ComplaintTrendChartProps {
  data: TrendItem[];
  periodLabel: string;
  isMonthlyView?: boolean;
}

interface DisplayBar {
  label: string;
  sublabel?: string;
  count: number;
}

export const ComplaintTrendChart: React.FC<ComplaintTrendChartProps> = ({
  data,
  periodLabel,
  isMonthlyView = false,
}) => {
  const [viewMode, setViewMode] = useState<'summary' | 'detailed'>('summary');
  const [activeBarIndex, setActiveBarIndex] = useState<number | null>(null);

  if (!data || data.length === 0) {
    return (
      <View style={styles.emptyCard}>
        <Ionicons name="bar-chart-outline" size={28} color={Colors.textMuted} />
        <Text style={styles.emptyText}>No trend activity recorded for this period.</Text>
      </View>
    );
  }

  const totalCount = data.reduce((acc, curr) => acc + curr.count, 0);

  // Group into clean weekly intervals if viewing a full month with 28-31 daily points
  const isDailyMonthData = data.length >= 28 && data.length <= 31;

  const displayBars: DisplayBar[] = useMemo(() => {
    if (isDailyMonthData && viewMode === 'summary') {
      const weeks: DisplayBar[] = [
        { label: 'Week 1', sublabel: '1–7', count: 0 },
        { label: 'Week 2', sublabel: '8–14', count: 0 },
        { label: 'Week 3', sublabel: '15–21', count: 0 },
        { label: 'Week 4', sublabel: '22–28', count: 0 },
        { label: 'Week 5', sublabel: `29–${data.length}`, count: 0 },
      ];

      data.forEach((d, idx) => {
        const day = idx + 1;
        if (day <= 7) weeks[0].count += d.count;
        else if (day <= 14) weeks[1].count += d.count;
        else if (day <= 21) weeks[2].count += d.count;
        else if (day <= 28) weeks[3].count += d.count;
        else weeks[4].count += d.count;
      });

      return weeks;
    }

    return data.map((d) => ({
      label: d.label,
      sublabel: d.full_label,
      count: d.count,
    }));
  }, [data, isDailyMonthData, viewMode]);

  const maxCount = Math.max(...displayBars.map((b) => b.count), 1);
  const peakBar = displayBars.reduce((prev, curr) => (curr.count > prev.count ? curr : prev), displayBars[0]);

  return (
    <View style={styles.card}>
      {/* Chart Top Header */}
      <View style={styles.headerRow}>
        <View>
          <Text style={styles.titleLabel}>COMPLAINT FREQUENCY</Text>
          <View style={styles.statRow}>
            <Text style={styles.bigTotal}>{totalCount.toLocaleString()}</Text>
            <Text style={styles.periodText}>{periodLabel}</Text>
          </View>
        </View>

        {/* View mode toggle button if daily data exists */}
        {isDailyMonthData && (
          <TouchableOpacity
            style={styles.toggleBtn}
            onPress={() => {
              setViewMode(viewMode === 'summary' ? 'detailed' : 'summary');
              setActiveBarIndex(null);
            }}
            activeOpacity={0.8}
          >
            <Ionicons
              name={viewMode === 'summary' ? 'calendar-outline' : 'stats-chart-outline'}
              size={13}
              color={Colors.primary}
            />
            <Text style={styles.toggleBtnText}>
              {viewMode === 'summary' ? 'Daily View' : 'Weekly View'}
            </Text>
          </TouchableOpacity>
        )}
      </View>

      {/* Peak volume notice */}
      <View style={styles.peakNotice}>
        <Ionicons name="trending-up" size={13} color={Colors.secondary} />
        <Text style={styles.peakText}>
          Peak: <Text style={styles.peakBold}>{peakBar.label}</Text> with{' '}
          <Text style={styles.peakBold}>{peakBar.count.toLocaleString()}</Text> complaints
        </Text>
      </View>

      {/* Background horizontal grid lines */}
      <View style={styles.chartContainer}>
        <View style={styles.gridLinesContainer}>
          <View style={[styles.gridLine, { top: '15%' }]} />
          <View style={[styles.gridLine, { top: '50%' }]} />
          <View style={[styles.gridLine, { top: '85%' }]} />
        </View>

        {/* The Bars Area */}
        {displayBars.length <= 12 ? (
          // Fixed width grid without scrolling (Summary weekly / Year view)
          <View style={styles.barsRow}>
            {displayBars.map((bar, idx) => {
              const heightPct = maxCount > 0 ? (bar.count / maxCount) * 100 : 0;
              const isPeak = bar.count === maxCount && bar.count > 0;
              const isSelected = activeBarIndex === idx;

              return (
                <TouchableOpacity
                  key={idx}
                  style={styles.barItem}
                  onPress={() => setActiveBarIndex(isSelected ? null : idx)}
                  activeOpacity={0.7}
                >
                  {/* Value on top */}
                  <Text style={[styles.barVal, isPeak && styles.barValPeak]}>
                    {bar.count > 999 ? `${(bar.count / 1000).toFixed(1)}k` : bar.count}
                  </Text>

                  {/* Track and Fill */}
                  <View style={styles.barTrack}>
                    <View
                      style={[
                        styles.barFill,
                        { height: `${Math.max(heightPct, bar.count > 0 ? 8 : 2)}%` },
                        isPeak && styles.barFillPeak,
                        isSelected && styles.barFillSelected,
                        bar.count === 0 && styles.barFillZero,
                      ]}
                    />
                  </View>

                  {/* Axis Label */}
                  <Text style={[styles.barLabel, isPeak && styles.barLabelPeak]} numberOfLines={1}>
                    {bar.label}
                  </Text>
                  {bar.sublabel && (
                    <Text style={styles.barSublabel} numberOfLines={1}>
                      {bar.sublabel}
                    </Text>
                  )}
                </TouchableOpacity>
              );
            })}
          </View>
        ) : (
          // Scrollable Detailed Daily View
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.scrollBarsRow}
          >
            {displayBars.map((bar, idx) => {
              const heightPct = maxCount > 0 ? (bar.count / maxCount) * 100 : 0;
              const isPeak = bar.count === maxCount && bar.count > 0;

              return (
                <View key={idx} style={styles.dailyBarItem}>
                  <Text style={[styles.barVal, isPeak && styles.barValPeak]}>
                    {bar.count > 0 ? (bar.count > 999 ? `${(bar.count / 1000).toFixed(1)}k` : bar.count) : ''}
                  </Text>
                  <View style={styles.dailyBarTrack}>
                    <View
                      style={[
                        styles.barFill,
                        { height: `${Math.max(heightPct, bar.count > 0 ? 8 : 2)}%` },
                        isPeak && styles.barFillPeak,
                        bar.count === 0 && styles.barFillZero,
                      ]}
                    />
                  </View>
                  <Text style={[styles.barLabel, isPeak && styles.barLabelPeak]}>
                    {bar.label}
                  </Text>
                </View>
              );
            })}
          </ScrollView>
        )}
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
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04,
    shadowRadius: 6,
    elevation: 2,
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 4,
  },
  titleLabel: {
    fontSize: 10,
    fontWeight: '800',
    color: Colors.textMuted,
    letterSpacing: 0.8,
  },
  statRow: {
    flexDirection: 'row',
    alignItems: 'baseline',
    marginTop: 2,
  },
  bigTotal: {
    fontSize: 26,
    fontWeight: '900',
    color: Colors.textPrimary,
    letterSpacing: -0.5,
  },
  periodText: {
    fontSize: Typography.fontSize.xs,
    fontWeight: '600',
    color: Colors.textSecondary,
    marginLeft: Spacing.sm,
  },
  toggleBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#EFF6FF',
    paddingHorizontal: Spacing.sm + 2,
    paddingVertical: 5,
    borderRadius: BorderRadius.full,
    borderWidth: 1,
    borderColor: '#BFDBFE',
  },
  toggleBtnText: {
    fontSize: 11,
    fontWeight: '700',
    color: Colors.primary,
    marginLeft: 4,
  },
  peakNotice: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: Spacing.md,
    marginTop: 2,
  },
  peakText: {
    fontSize: 11,
    color: Colors.textSecondary,
    marginLeft: 4,
  },
  peakBold: {
    fontWeight: '800',
    color: Colors.secondary,
  },
  chartContainer: {
    height: 155,
    position: 'relative',
    justifyContent: 'flex-end',
    paddingTop: 15,
  },
  gridLinesContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'space-between',
  },
  gridLine: {
    position: 'absolute',
    left: 0,
    right: 0,
    height: 1,
    backgroundColor: '#F1F5F9',
    borderStyle: 'dashed',
  },
  barsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    height: '100%',
  },
  barItem: {
    flex: 1,
    alignItems: 'center',
    height: '100%',
    justifyContent: 'flex-end',
    paddingHorizontal: 2,
  },
  barVal: {
    fontSize: 10,
    fontWeight: '700',
    color: Colors.textSecondary,
    marginBottom: 4,
  },
  barValPeak: {
    color: Colors.secondary,
    fontWeight: '900',
  },
  barTrack: {
    width: '65%',
    maxWidth: 36,
    height: 96,
    backgroundColor: '#F1F5F9',
    borderRadius: 8,
    justifyContent: 'flex-end',
    overflow: 'hidden',
  },
  barFill: {
    width: '100%',
    backgroundColor: Colors.primary,
    borderRadius: 8,
  },
  barFillPeak: {
    backgroundColor: Colors.secondary,
  },
  barFillSelected: {
    backgroundColor: Colors.primaryDark,
  },
  barFillZero: {
    backgroundColor: '#E2E8F0',
  },
  barLabel: {
    fontSize: 10,
    fontWeight: '700',
    color: Colors.textPrimary,
    marginTop: 6,
  },
  barLabelPeak: {
    color: Colors.secondary,
    fontWeight: '900',
  },
  barSublabel: {
    fontSize: 9,
    color: Colors.textMuted,
    marginTop: 1,
  },
  scrollBarsRow: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    paddingHorizontal: Spacing.xs,
  },
  dailyBarItem: {
    width: 28,
    alignItems: 'center',
    marginHorizontal: 2,
  },
  dailyBarTrack: {
    width: 12,
    height: 96,
    backgroundColor: '#F1F5F9',
    borderRadius: 6,
    justifyContent: 'flex-end',
    overflow: 'hidden',
  },
  emptyCard: {
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
    marginTop: Spacing.xs,
  },
});
