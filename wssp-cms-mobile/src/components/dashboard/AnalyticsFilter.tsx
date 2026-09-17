import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Modal,
  TextInput,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors, Spacing, BorderRadius, Typography } from '../../constants/theme';

export interface FilterPeriodState {
  year: number;
  month: number | null; // null for full year
  start_date?: string;
  end_date?: string;
}

interface AnalyticsFilterProps {
  currentPeriodLabel?: string;
  onFilterChange: (filter: {
    year?: number;
    month?: number;
    start_date?: string;
    end_date?: string;
  }) => void;
  loading?: boolean;
}

const YEARS = [2026, 2025, 2024];

const MONTHS = [
  { num: null, label: 'All Year' },
  { num: 1, label: 'Jan' },
  { num: 2, label: 'Feb' },
  { num: 3, label: 'Mar' },
  { num: 4, label: 'Apr' },
  { num: 5, label: 'May' },
  { num: 6, label: 'Jun' },
  { num: 7, label: 'Jul' },
  { num: 8, label: 'Aug' },
  { num: 9, label: 'Sep' },
  { num: 10, label: 'Oct' },
  { num: 11, label: 'Nov' },
  { num: 12, label: 'Dec' },
];

export const AnalyticsFilter: React.FC<AnalyticsFilterProps> = ({
  currentPeriodLabel,
  onFilterChange,
  loading = false,
}) => {
  const currentYear = new Date().getFullYear();
  const currentMonth = new Date().getMonth() + 1;

  const [selectedYear, setSelectedYear] = useState<number>(2026);
  const [selectedMonth, setSelectedMonth] = useState<number | null>(1); // Default Jan 2026 or current month
  const [isCustomModalOpen, setIsCustomModalOpen] = useState<boolean>(false);
  const [customStartDate, setCustomStartDate] = useState<string>('2026-01-01');
  const [customEndDate, setCustomEndDate] = useState<string>('2026-01-31');
  const [isCustomActive, setIsCustomActive] = useState<boolean>(false);

  const handleYearSelect = (year: number) => {
    setIsCustomActive(false);
    setSelectedYear(year);
    if (selectedMonth !== null) {
      onFilterChange({ year, month: selectedMonth });
    } else {
      onFilterChange({ year });
    }
  };

  const handleMonthSelect = (month: number | null) => {
    setIsCustomActive(false);
    setSelectedMonth(month);
    if (month === null) {
      onFilterChange({ year: selectedYear });
    } else {
      onFilterChange({ year: selectedYear, month });
    }
  };

  const handleApplyCustomRange = () => {
    if (customStartDate && customEndDate) {
      setIsCustomActive(true);
      setIsCustomModalOpen(false);
      onFilterChange({
        start_date: customStartDate.trim(),
        end_date: customEndDate.trim(),
      });
    }
  };

  return (
    <View style={styles.container}>
      {/* Top Header Row with Active Period Badge & Custom Range Button */}
      <View style={styles.headerRow}>
        <View style={styles.badgeContainer}>
          <Ionicons name="calendar-outline" size={14} color={Colors.primary} />
          <Text style={styles.badgeText}>
            {currentPeriodLabel || `${selectedMonth ? MONTHS.find(m => m.num === selectedMonth)?.label : 'Full'} ${selectedYear}`}
          </Text>
        </View>

        <TouchableOpacity
          style={[styles.customBtn, isCustomActive && styles.customBtnActive]}
          onPress={() => setIsCustomModalOpen(true)}
          activeOpacity={0.75}
        >
          <Ionicons
            name="options-outline"
            size={14}
            color={isCustomActive ? '#FFFFFF' : Colors.primaryDark}
          />
          <Text
            style={[styles.customBtnText, isCustomActive && styles.customBtnTextActive]}
          >
            Custom Range
          </Text>
        </TouchableOpacity>
      </View>

      {/* Year Selector Row */}
      <View style={styles.selectorSection}>
        <Text style={styles.sectionLabel}>YEAR</Text>
        <View style={styles.pillRow}>
          {YEARS.map((year) => {
            const isActive = !isCustomActive && selectedYear === year;
            return (
              <TouchableOpacity
                key={year}
                style={[styles.yearPill, isActive && styles.yearPillActive]}
                onPress={() => handleYearSelect(year)}
                disabled={loading}
              >
                <Text style={[styles.yearPillText, isActive && styles.yearPillTextActive]}>
                  {year}
                </Text>
              </TouchableOpacity>
            );
          })}
        </View>
      </View>

      {/* Month Selector Scroll */}
      <View style={[styles.selectorSection, { marginTop: Spacing.xs }]}>
        <Text style={styles.sectionLabel}>REPORTING PERIOD</Text>
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.monthScroll}
        >
          {MONTHS.map((m) => {
            const isActive = !isCustomActive && selectedMonth === m.num;
            return (
              <TouchableOpacity
                key={m.label}
                style={[styles.monthPill, isActive && styles.monthPillActive]}
                onPress={() => handleMonthSelect(m.num)}
                disabled={loading}
              >
                <Text
                  style={[styles.monthPillText, isActive && styles.monthPillTextActive]}
                >
                  {m.label}
                </Text>
              </TouchableOpacity>
            );
          })}
        </ScrollView>
      </View>

      {/* Custom Date Range Modal */}
      <Modal
        visible={isCustomModalOpen}
        transparent
        animationType="fade"
        onRequestClose={() => setIsCustomModalOpen(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalCard}>
            <View style={styles.modalHeader}>
              <View style={styles.modalHeaderLeft}>
                <Ionicons name="calendar" size={20} color={Colors.primary} />
                <Text style={styles.modalTitle}>Custom Date Range</Text>
              </View>
              <TouchableOpacity
                onPress={() => setIsCustomModalOpen(false)}
                style={styles.closeBtn}
              >
                <Ionicons name="close" size={20} color={Colors.textMuted} />
              </TouchableOpacity>
            </View>

            <Text style={styles.modalDesc}>
              Specify custom start and end dates (YYYY-MM-DD) for complaint analytics:
            </Text>

            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>START DATE (From)</Text>
              <TextInput
                style={styles.input}
                value={customStartDate}
                onChangeText={setCustomStartDate}
                placeholder="2026-01-01"
                placeholderTextColor={Colors.textMuted}
                autoCapitalize="none"
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>END DATE (To)</Text>
              <TextInput
                style={styles.input}
                value={customEndDate}
                onChangeText={setCustomEndDate}
                placeholder="2026-01-31"
                placeholderTextColor={Colors.textMuted}
                autoCapitalize="none"
              />
            </View>

            {/* Quick preset buttons */}
            <View style={styles.presetsRow}>
              <TouchableOpacity
                style={styles.presetChip}
                onPress={() => {
                  setCustomStartDate('2026-01-01');
                  setCustomEndDate('2026-01-15');
                }}
              >
                <Text style={styles.presetText}>01-15 Jan 2026</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.presetChip}
                onPress={() => {
                  setCustomStartDate('2026-01-01');
                  setCustomEndDate('2026-06-30');
                }}
              >
                <Text style={styles.presetText}>H1 2026 (Jan-Jun)</Text>
              </TouchableOpacity>
            </View>

            <View style={styles.modalActions}>
              <TouchableOpacity
                style={styles.cancelBtn}
                onPress={() => setIsCustomModalOpen(false)}
              >
                <Text style={styles.cancelBtnText}>Cancel</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.applyBtn}
                onPress={handleApplyCustomRange}
              >
                <Text style={styles.applyBtnText}>Apply Filter</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
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
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.sm,
  },
  badgeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#EFF6FF',
    paddingHorizontal: Spacing.sm,
    paddingVertical: 5,
    borderRadius: BorderRadius.full,
    borderWidth: 1,
    borderColor: '#BFDBFE',
  },
  badgeText: {
    fontSize: Typography.fontSize.xs,
    fontWeight: '800',
    color: Colors.primaryDark,
    marginLeft: 5,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  customBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F1F5F9',
    paddingHorizontal: Spacing.sm,
    paddingVertical: 6,
    borderRadius: BorderRadius.md,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  customBtnActive: {
    backgroundColor: Colors.primary,
    borderColor: Colors.primary,
  },
  customBtnText: {
    fontSize: Typography.fontSize.xs,
    fontWeight: '700',
    color: Colors.textSecondary,
    marginLeft: 4,
  },
  customBtnTextActive: {
    color: '#FFFFFF',
  },
  selectorSection: {
    marginTop: 2,
  },
  sectionLabel: {
    fontSize: 10,
    fontWeight: '800',
    color: Colors.textMuted,
    letterSpacing: 0.8,
    marginBottom: 6,
  },
  pillRow: {
    flexDirection: 'row',
  },
  yearPill: {
    paddingHorizontal: Spacing.md,
    paddingVertical: 6,
    backgroundColor: '#F8FAFC',
    borderRadius: BorderRadius.md,
    marginRight: Spacing.sm,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  yearPillActive: {
    backgroundColor: Colors.primaryDark,
    borderColor: Colors.primaryDark,
  },
  yearPillText: {
    fontSize: Typography.fontSize.xs,
    fontWeight: '700',
    color: Colors.textSecondary,
  },
  yearPillTextActive: {
    color: '#FFFFFF',
  },
  monthScroll: {
    paddingVertical: 2,
  },
  monthPill: {
    paddingHorizontal: Spacing.sm + 4,
    paddingVertical: 6,
    backgroundColor: '#F8FAFC',
    borderRadius: BorderRadius.md,
    marginRight: 6,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  monthPillActive: {
    backgroundColor: Colors.primary,
    borderColor: Colors.primary,
  },
  monthPillText: {
    fontSize: Typography.fontSize.xs,
    fontWeight: '600',
    color: Colors.textSecondary,
  },
  monthPillTextActive: {
    color: '#FFFFFF',
    fontWeight: '800',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: Colors.overlay,
    justifyContent: 'center',
    alignItems: 'center',
    padding: Spacing.lg,
  },
  modalCard: {
    width: '100%',
    maxWidth: 380,
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.lg,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 12,
    elevation: 8,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.sm,
  },
  modalHeaderLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  modalTitle: {
    fontSize: Typography.fontSize.md,
    fontWeight: '800',
    color: Colors.textPrimary,
    marginLeft: Spacing.xs,
  },
  closeBtn: {
    padding: 4,
  },
  modalDesc: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textMuted,
    marginBottom: Spacing.md,
    lineHeight: 18,
  },
  inputGroup: {
    marginBottom: Spacing.sm,
  },
  inputLabel: {
    fontSize: 10,
    fontWeight: '800',
    color: Colors.textSecondary,
    marginBottom: 4,
    letterSpacing: 0.5,
  },
  input: {
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: BorderRadius.md,
    paddingHorizontal: Spacing.sm,
    paddingVertical: 8,
    fontSize: Typography.fontSize.sm,
    color: Colors.textPrimary,
  },
  presetsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 4,
    marginBottom: Spacing.md,
  },
  presetChip: {
    backgroundColor: '#F1F5F9',
    paddingHorizontal: Spacing.sm,
    paddingVertical: 4,
    borderRadius: BorderRadius.sm,
    marginRight: Spacing.xs,
    marginTop: 4,
  },
  presetText: {
    fontSize: 11,
    fontWeight: '600',
    color: Colors.primary,
  },
  modalActions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    marginTop: Spacing.sm,
  },
  cancelBtn: {
    paddingHorizontal: Spacing.md,
    paddingVertical: 10,
    marginRight: Spacing.sm,
  },
  cancelBtnText: {
    fontSize: Typography.fontSize.sm,
    fontWeight: '600',
    color: Colors.textSecondary,
  },
  applyBtn: {
    backgroundColor: Colors.primary,
    paddingHorizontal: Spacing.lg,
    paddingVertical: 10,
    borderRadius: BorderRadius.md,
  },
  applyBtnText: {
    fontSize: Typography.fontSize.sm,
    fontWeight: '800',
    color: '#FFFFFF',
  },
});
