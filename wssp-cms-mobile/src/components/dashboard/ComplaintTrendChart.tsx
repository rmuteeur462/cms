import React, { useState, useMemo, useRef } from 'react';
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

// ─── Layout constants ───────────────────────────────────────────────────────
const BAR_W        = 36;   // fixed bar width (px) — wide enough for any label
const CELL_PADX    = 8;    // padding on each side of bar within its cell
const CELL_W       = BAR_W + CELL_PADX * 2; // total cell width
const TRACK_H      = 160;  // height of the filled portion of each bar
const TOP_SPACE    = 28;   // space above bars for count label
const LABEL_H      = 36;   // space below bars for axis labels

const C_RESOLVED   = '#16A34A';
const C_PENDING    = '#F59E0B';
const C_PEAK       = '#6366F1';
const C_TRACK      = '#F1F5F9';
const C_GRID       = '#E2E8F0';
// ────────────────────────────────────────────────────────────────────────────

interface ComplaintTrendChartProps {
  data: TrendItem[];
  periodLabel: string;
  isMonthlyView?: boolean;
}

interface BarData {
  label: string;       // short label shown on axis  e.g. "Jan", "Aug", "Wk1", "01"
  fullLabel: string;   // shown in inspector         e.g. "January 2026", "14 Aug 2026"
  count: number;
  resolved: number;
  pending: number;
  resolvedPct: number;
  pendingPct: number;
}

function buildBar(label: string, fullLabel: string, c: number, res: number, pnd: number): BarData {
  const rp = c > 0 ? +((res / c) * 100).toFixed(1) : 0;
  const pp = c > 0 ? +((pnd / c) * 100).toFixed(1) : 0;
  return { label, fullLabel, count: c, resolved: res, pending: pnd, resolvedPct: rp, pendingPct: pp };
}

function fmt(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000)     return `${(n / 1_000).toFixed(1)}k`;
  return String(n);
}

export const ComplaintTrendChart: React.FC<ComplaintTrendChartProps> = ({ data, periodLabel }) => {
  const [viewMode, setViewMode]   = useState<'summary' | 'detailed'>('summary');
  const [selectedIdx, setSelectedIdx] = useState<number | null>(null);
  const scrollRef = useRef<any>(null);

  // ── Empty state ──────────────────────────────────────────────────────────
  if (!data || data.length === 0) {
    return (
      <View style={styles.emptyCard}>
        <Ionicons name="bar-chart-outline" size={36} color={Colors.textMuted} />
        <Text style={styles.emptyText}>No trend data for this period.</Text>
      </View>
    );
  }

  // ── Aggregate totals ─────────────────────────────────────────────────────
  const totalCount    = data.reduce((s, d) => s + (d.count    || 0), 0);
  const totalResolved = data.reduce((s, d) => s + (d.resolved || 0), 0);
  const totalPending  = data.reduce((s, d) => s + (d.pending  || 0), 0);
  const globalResPct  = totalCount > 0 ? ((totalResolved / totalCount) * 100).toFixed(1) : '0';
  const globalPndPct  = totalCount > 0 ? ((totalPending  / totalCount) * 100).toFixed(1) : '0';

  const isDailyMonth = data.length >= 28 && data.length <= 31;

  // ── Build display bars ───────────────────────────────────────────────────
  const bars: BarData[] = useMemo(() => {
    if (isDailyMonth && viewMode === 'summary') {
      const wks = [
        { lbl: 'Wk 1', full: 'Week 1  (Days 1 – 7)'        },
        { lbl: 'Wk 2', full: 'Week 2  (Days 8 – 14)'        },
        { lbl: 'Wk 3', full: 'Week 3  (Days 15 – 21)'       },
        { lbl: 'Wk 4', full: 'Week 4  (Days 22 – 28)'       },
        { lbl: 'Wk 5', full: `Week 5  (Days 29 – ${data.length})` },
      ].map(w => ({ ...w, c: 0, r: 0, p: 0 }));
      data.forEach((d, i) => {
        const wi = i < 7 ? 0 : i < 14 ? 1 : i < 21 ? 2 : i < 28 ? 3 : 4;
        wks[wi].c += d.count    || 0;
        wks[wi].r += d.resolved || 0;
        wks[wi].p += d.pending  || 0;
      });
      return wks.map(w => buildBar(w.lbl, w.full, w.c, w.r, w.p));
    }
    return data.map(d => {
      const c   = d.count    || 0;
      const res = d.resolved ?? 0;
      const pnd = d.pending  ?? Math.max(0, c - res);
      return buildBar(d.label, d.full_label || d.label, c, res, pnd);
    });
  }, [data, isDailyMonth, viewMode]);

  // ── Derived ──────────────────────────────────────────────────────────────
  const maxCount = useMemo(() => Math.max(...bars.map(b => b.count), 1), [bars]);
  const peakIdx  = useMemo(
    () => bars.reduce((pi, b, i) => (b.count > bars[pi].count ? i : pi), 0),
    [bars],
  );
  const activeIdx = selectedIdx !== null ? selectedIdx : peakIdx;
  const active    = bars[activeIdx] ?? bars[0];

  // ── Pixel heights for a bar ──────────────────────────────────────────────
  const barH = (count: number) =>
    count === 0 ? 0 : Math.max(10, Math.round((count / maxCount) * TRACK_H));

  // ── Grid values ─────────────────────────────────────────────────────────
  const gridSteps = [1, 0.75, 0.5, 0.25].map(f => ({
    val: Math.round(maxCount * f),
    pct: f,
  }));

  // ── Render a single bar cell ─────────────────────────────────────────────
  const renderBar = (bar: BarData, idx: number) => {
    const isPeak   = idx === peakIdx && bar.count > 0;
    const isActive = idx === activeIdx;
    const totalBarH  = barH(bar.count);
    const resolvedH  = bar.count > 0 ? Math.round((bar.resolved / bar.count) * totalBarH) : 0;
    const pendingH   = totalBarH - resolvedH;

    const showLabel = isPeak || isActive;

    return (
      <TouchableOpacity
        key={idx}
        style={styles.cell}
        onPress={() => setSelectedIdx(isActive ? null : idx)}
        activeOpacity={0.75}
      >
        {/* Count label above bar — only peak or selected */}
        <View style={styles.topSpace}>
          {showLabel && bar.count > 0 && (
            isPeak ? (
              <View style={styles.peakPill}>
                <Ionicons name="trending-up" size={9} color="#fff" />
                <Text style={styles.peakPillText}>{fmt(bar.count)}</Text>
              </View>
            ) : (
              <Text style={styles.activeValText}>{fmt(bar.count)}</Text>
            )
          )}
        </View>

        {/* Bar track */}
        <View
          style={[
            styles.track,
            isPeak   && styles.trackPeak,
            isActive && !isPeak && styles.trackActive,
          ]}
        >
          {/* Fill grows from bottom upwards */}
          {totalBarH > 0 && (
            <View style={[styles.fillWrap, { height: totalBarH }]}>
              {/* Pending on top (rendered first → visually at top) */}
              {pendingH > 0 && (
                <View style={{ height: pendingH, width: '100%', backgroundColor: isPeak ? '#D97706' : C_PENDING }} />
              )}
              {/* Resolved on bottom */}
              {resolvedH > 0 && (
                <View style={{ height: resolvedH, width: '100%', backgroundColor: isPeak ? '#15803D' : C_RESOLVED }} />
              )}
            </View>
          )}

          {/* Glow ring for peak */}
          {isPeak && (
            <View
              style={[StyleSheet.absoluteFill, styles.peakRing]}
            />
          )}
          {/* Selection ring */}
          {isActive && !isPeak && (
            <View
              style={[StyleSheet.absoluteFill, styles.activeRing]}
            />
          )}
        </View>

        {/* Axis label */}
        <Text
          style={[
            styles.axisLabel,
            isPeak   && styles.axisLabelPeak,
            isActive && !isPeak && styles.axisLabelActive,
          ]}
          numberOfLines={2}
        >
          {bar.label}
        </Text>
      </TouchableOpacity>
    );
  };

  // ────────────────────────────────────────────────────────────────────────
  return (
    <View style={styles.card}>

      {/* ── HEADER ───────────────────────────────────────────────────────── */}
      <View style={styles.headerRow}>
        <View style={{ flex: 1 }}>
          <Text style={styles.sectionTag}>COMPLAINT FREQUENCY</Text>
          <View style={styles.totalRow}>
            <Text style={styles.totalNum}>{totalCount.toLocaleString()}</Text>
            <View style={styles.periodTag}>
              <Text style={styles.periodTagText}>{periodLabel}</Text>
            </View>
          </View>
        </View>

        {isDailyMonth && (
          <TouchableOpacity
            style={styles.viewToggle}
            onPress={() => { setViewMode(v => v === 'summary' ? 'detailed' : 'summary'); setSelectedIdx(null); }}
            activeOpacity={0.8}
          >
            <Ionicons
              name={viewMode === 'summary' ? 'calendar-outline' : 'stats-chart-outline'}
              size={13} color={Colors.primary}
            />
            <Text style={styles.viewToggleText}>
              {viewMode === 'summary' ? 'Daily' : 'Weekly'}
            </Text>
          </TouchableOpacity>
        )}
      </View>

      {/* ── LEGEND ───────────────────────────────────────────────────────── */}
      <View style={styles.legendRow}>
        {[
          { color: C_RESOLVED, label: 'Resolved', pct: globalResPct, pctColor: '#15803D' },
          { color: C_PENDING,  label: 'Pending',  pct: globalPndPct, pctColor: '#B45309' },
          { color: C_PEAK,     label: 'Peak bar', pct: null,         pctColor: null      },
        ].map((item, i) => (
          <View key={i} style={styles.legendChip}>
            <View style={[styles.legendDot, { backgroundColor: item.color }]} />
            <Text style={styles.legendChipLabel}>{item.label}</Text>
            {item.pct !== null && (
              <Text style={[styles.legendChipPct, { color: item.pctColor! }]}>{item.pct}%</Text>
            )}
          </View>
        ))}
      </View>

      {/* ── INSPECTOR ────────────────────────────────────────────────────── */}
      <View style={styles.inspector}>
        {/* Header */}
        <View style={styles.inspectorTopRow}>
          <View style={styles.inspectorTitleWrap}>
            <Ionicons name="analytics" size={14} color={Colors.primary} />
            <Text style={styles.inspectorTitle} numberOfLines={1}>{active.fullLabel}</Text>
          </View>
          {activeIdx === peakIdx && active.count > 0 ? (
            <View style={styles.inspectorPeakBadge}>
              <Ionicons name="trending-up" size={11} color={C_PEAK} />
              <Text style={styles.inspectorPeakText}>Peak</Text>
            </View>
          ) : (
            <Text style={styles.inspectorTotalText}>{active.count.toLocaleString()} total</Text>
          )}
        </View>

        {/* Proportion bar */}
        <View style={styles.propBar}>
          {active.count > 0 ? (
            <>
              <View style={{ flex: Math.max(active.resolved, 0.001), height: '100%', backgroundColor: C_RESOLVED }} />
              <View style={{ flex: Math.max(active.pending,  0.001), height: '100%', backgroundColor: C_PENDING  }} />
            </>
          ) : (
            <View style={{ flex: 1, height: '100%', backgroundColor: C_GRID }} />
          )}
        </View>

        {/* Stat tiles */}
        <View style={styles.tilesRow}>
          {/* Resolved */}
          <View style={[styles.tile, styles.tileGreen]}>
            <View style={styles.tileTitleRow}>
              <View style={[styles.tileDot, { backgroundColor: C_RESOLVED }]} />
              <Text style={styles.tileTitleText}>Resolved</Text>
            </View>
            <Text style={[styles.tileNumber, { color: '#166534' }]}>
              {active.resolved.toLocaleString()}
            </Text>
            <View style={[styles.tilePill, { backgroundColor: '#DCFCE7' }]}>
              <Text style={[styles.tilePillText, { color: '#15803D' }]}>{active.resolvedPct}%</Text>
            </View>
          </View>

          {/* Pending */}
          <View style={[styles.tile, styles.tileAmber]}>
            <View style={styles.tileTitleRow}>
              <View style={[styles.tileDot, { backgroundColor: C_PENDING }]} />
              <Text style={styles.tileTitleText}>Pending</Text>
            </View>
            <Text style={[styles.tileNumber, { color: '#92400E' }]}>
              {active.pending.toLocaleString()}
            </Text>
            <View style={[styles.tilePill, { backgroundColor: '#FEF3C7' }]}>
              <Text style={[styles.tilePillText, { color: '#B45309' }]}>{active.pendingPct}%</Text>
            </View>
          </View>
        </View>
      </View>

      {/* ── CHART ────────────────────────────────────────────────────────── */}
      {/* Grid lines overlay (behind scroll area) */}
      <View style={styles.chartOuter}>
        {/* Grid reference lines */}
        <View style={styles.gridLines}>
          {gridSteps.map((g, i) => (
            <View
              key={i}
              style={[
                styles.gridLine,
                { bottom: LABEL_H + Math.round(g.pct * TRACK_H) },
              ]}
            >
              <Text style={styles.gridLabel}>{fmt(g.val)}</Text>
            </View>
          ))}
          {/* Zero line */}
          <View style={[styles.gridLine, styles.gridLineZero, { bottom: LABEL_H }]}>
            <Text style={styles.gridLabel}>0</Text>
          </View>
        </View>

        {/* Scrollable / centered bars */}
        <ScrollView
          ref={scrollRef}
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={[
            styles.scrollContent,
            bars.length <= 6 && styles.scrollContentCentered,
          ]}
          decelerationRate="fast"
        >
          {bars.map((b, i) => renderBar(b, i))}
        </ScrollView>
      </View>

      {/* Tap hint */}
      <View style={styles.hintRow}>
        <Ionicons name="hand-left-outline" size={12} color={Colors.textMuted} />
        <Text style={styles.hintText}>Tap any bar to see resolved vs. pending details</Text>
      </View>
    </View>
  );
};

// ─── STYLES ─────────────────────────────────────────────────────────────────
const styles = StyleSheet.create({
  /* card */
  card: {
    backgroundColor: Colors.surface,
    borderRadius: 18,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: Colors.border,
    shadowColor: '#0A3663',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.08,
    shadowRadius: 12,
    elevation: 5,
  },

  /* header */
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  sectionTag: {
    fontSize: 10,
    fontWeight: '800',
    letterSpacing: 1.4,
    color: Colors.textMuted,
    textTransform: 'uppercase',
  },
  totalRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 3,
    gap: 8,
  },
  totalNum: {
    fontSize: 30,
    fontWeight: '900',
    color: Colors.textPrimary,
    letterSpacing: -1.5,
  },
  periodTag: {
    backgroundColor: '#EFF6FF',
    borderRadius: 20,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderWidth: 1,
    borderColor: '#BFDBFE',
  },
  periodTagText: {
    fontSize: 11,
    fontWeight: '700',
    color: Colors.primary,
  },
  viewToggle: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F0F9FF',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#BAE6FD',
    gap: 5,
    marginTop: 4,
  },
  viewToggleText: {
    fontSize: 11,
    fontWeight: '700',
    color: Colors.primary,
  },

  /* legend */
  legendRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    marginBottom: 12,
  },
  legendChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F8FAFC',
    borderRadius: 20,
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderWidth: 1,
    borderColor: Colors.border,
    gap: 5,
  },
  legendDot: {
    width: 9,
    height: 9,
    borderRadius: 5,
  },
  legendChipLabel: {
    fontSize: 11,
    fontWeight: '600',
    color: Colors.textSecondary,
  },
  legendChipPct: {
    fontSize: 11,
    fontWeight: '800',
  },

  /* inspector */
  inspector: {
    backgroundColor: '#F8FAFC',
    borderRadius: 12,
    padding: 10,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: C_GRID,
  },
  inspectorTopRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 6,
  },
  inspectorTitleWrap: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    gap: 5,
  },
  inspectorTitle: {
    fontSize: 12,
    fontWeight: '800',
    color: Colors.textPrimary,
    flex: 1,
  },
  inspectorPeakBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#EEF2FF',
    borderRadius: 20,
    paddingHorizontal: 7,
    paddingVertical: 2,
    borderWidth: 1,
    borderColor: '#C7D2FE',
    gap: 3,
  },
  inspectorPeakText: {
    fontSize: 10,
    fontWeight: '800',
    color: C_PEAK,
  },
  inspectorTotalText: {
    fontSize: 11,
    fontWeight: '700',
    color: Colors.textSecondary,
  },
  propBar: {
    height: 5,
    borderRadius: 3,
    backgroundColor: C_GRID,
    flexDirection: 'row',
    overflow: 'hidden',
    marginBottom: 8,
  },
  tilesRow: {
    flexDirection: 'row',
    gap: 8,
  },
  tile: {
    flex: 1,
    borderRadius: 8,
    paddingHorizontal: 8,
    paddingVertical: 6,
    borderWidth: 1,
  },
  tileGreen: {
    backgroundColor: '#F0FDF4',
    borderColor: '#BBF7D0',
  },
  tileAmber: {
    backgroundColor: '#FFFBEB',
    borderColor: '#FDE68A',
  },
  tileTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginBottom: 2,
  },
  tileDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
  },
  tileTitleText: {
    fontSize: 10,
    fontWeight: '700',
    color: Colors.textSecondary,
  },
  tileNumber: {
    fontSize: 15,
    fontWeight: '900',
    letterSpacing: -0.3,
    marginBottom: 2,
  },
  tilePill: {
    alignSelf: 'flex-start',
    borderRadius: 4,
    paddingHorizontal: 5,
    paddingVertical: 1,
  },
  tilePillText: {
    fontSize: 9.5,
    fontWeight: '800',
  },

  /* chart */
  chartOuter: {
    height: TOP_SPACE + TRACK_H + LABEL_H,
    position: 'relative',
    marginBottom: 8,
  },
  gridLines: {
    position: 'absolute',
    left: 0,
    right: 0,
    bottom: 0,
    top: 0,
    zIndex: 1,
    pointerEvents: 'none',
  } as any,
  gridLine: {
    position: 'absolute',
    left: 0,
    right: 0,
    height: 1,
    backgroundColor: C_GRID,
    flexDirection: 'row',
    alignItems: 'center',
  },
  gridLineZero: {
    backgroundColor: '#CBD5E1',
    height: 1.5,
  },
  gridLabel: {
    fontSize: 9,
    fontWeight: '700',
    color: '#94A3B8',
    paddingRight: 6,
    textAlign: 'left',
    position: 'absolute',
    left: 2,
    top: -12,
  },
  scrollContent: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    paddingBottom: 0,
    height: TOP_SPACE + TRACK_H + LABEL_H,
    paddingHorizontal: 12,
  },
  scrollContentCentered: {
    flexGrow: 1,
    justifyContent: 'space-around',
  },

  /* bar cell */
  cell: {
    width: CELL_W,
    paddingHorizontal: CELL_PADX,
    alignItems: 'center',
    justifyContent: 'flex-end',
    height: TOP_SPACE + TRACK_H + LABEL_H,
  },
  topSpace: {
    height: TOP_SPACE,
    justifyContent: 'flex-end',
    alignItems: 'center',
    width: BAR_W,
    paddingBottom: 4,
  },
  peakPill: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: C_PEAK,
    borderRadius: 5,
    paddingHorizontal: 5,
    paddingVertical: 2,
    gap: 3,
  },
  peakPillText: {
    fontSize: 9,
    fontWeight: '900',
    color: '#fff',
    letterSpacing: 0.3,
  },
  activeValText: {
    fontSize: 10,
    fontWeight: '800',
    color: Colors.primary,
  },
  track: {
    width: BAR_W,
    height: TRACK_H,
    borderRadius: 8,
    backgroundColor: C_TRACK,
    overflow: 'hidden',
    justifyContent: 'flex-end',
    position: 'relative',
  },
  trackPeak: {
    backgroundColor: '#EEF2FF',
  },
  trackActive: {
    backgroundColor: '#EFF6FF',
  },
  fillWrap: {
    width: '100%',
    flexDirection: 'column',
    overflow: 'hidden',
    borderRadius: 8,
  },
  peakRing: {
    borderRadius: 8,
    borderWidth: 2,
    borderColor: C_PEAK,
    pointerEvents: 'none',
  } as any,
  activeRing: {
    borderRadius: 8,
    borderWidth: 2,
    borderColor: Colors.primary,
    pointerEvents: 'none',
  } as any,
  axisLabel: {
    width: BAR_W,
    marginTop: 6,
    fontSize: 11,
    fontWeight: '600',
    color: Colors.textSecondary,
    textAlign: 'center',
    height: LABEL_H - 6,
  },
  axisLabelPeak: {
    color: C_PEAK,
    fontWeight: '900',
  },
  axisLabelActive: {
    color: Colors.primary,
    fontWeight: '800',
  },

  /* hint */
  hintRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 5,
  },
  hintText: {
    fontSize: 10,
    color: Colors.textMuted,
    fontStyle: 'italic',
  },

  /* empty */
  emptyCard: {
    backgroundColor: Colors.surface,
    borderRadius: 18,
    padding: 32,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  emptyText: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textMuted,
    marginTop: 10,
  },
});
