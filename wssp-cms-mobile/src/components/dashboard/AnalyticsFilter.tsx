import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Modal,
  TextInput,
  ScrollView,
  Pressable,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors, Spacing, BorderRadius, Typography } from '../../constants/theme';

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

const AVAILABLE_YEARS: { id: number | 'all'; label: string; desc?: string }[] = [
  { id: 'all', label: 'All Years (All Time)', desc: 'Aggregate data across all recorded years (2021 – 2026)' },
  { id: 2026, label: 'Year 2026', desc: 'Current operating year' },
  { id: 2025, label: 'Year 2025', desc: 'Previous operating year' },
  { id: 2024, label: 'Year 2024', desc: 'Historical operating year' },
];

const MONTH_OPTIONS = [
  { num: null, name: 'Full Year (All Months)', short: 'All Year' },
  { num: 1, name: 'January', short: 'Jan' },
  { num: 2, name: 'February', short: 'Feb' },
  { num: 3, name: 'March', short: 'Mar' },
  { num: 4, name: 'April', short: 'Apr' },
  { num: 5, name: 'May', short: 'May' },
  { num: 6, name: 'June', short: 'Jun' },
  { num: 7, name: 'July', short: 'Jul' },
  { num: 8, name: 'August', short: 'Aug' },
  { num: 9, name: 'September', short: 'Sep' },
  { num: 10, name: 'October', short: 'Oct' },
  { num: 11, name: 'November', short: 'Nov' },
  { num: 12, name: 'December', short: 'Dec' },
];

export const AnalyticsFilter: React.FC<AnalyticsFilterProps> = ({
  currentPeriodLabel,
  onFilterChange,
  loading = false,
}) => {
  const [selectedYear, setSelectedYear] = useState<number | 'all'>(2026);
  const [selectedMonth, setSelectedMonth] = useState<number | null>(1); // Default Jan

  const [yearDropdownOpen, setYearDropdownOpen] = useState<boolean>(false);
  const [monthDropdownOpen, setMonthDropdownOpen] = useState<boolean>(false);
  const [customModalOpen, setCustomModalOpen] = useState<boolean>(false);

  const [customStartDate, setCustomStartDate] = useState<string>('2026-01-01');
  const [customEndDate, setCustomEndDate] = useState<string>('2026-01-31');
  const [isCustomActive, setIsCustomActive] = useState<boolean>(false);

  const activeMonthObj = MONTH_OPTIONS.find((m) => m.num === selectedMonth) || MONTH_OPTIONS[0];

  const handleSelectYear = (year: number | 'all') => {
    setIsCustomActive(false);
    setSelectedYear(year);
    setYearDropdownOpen(false);

    if (year === 'all') {
      setSelectedMonth(null);
      onFilterChange({ year: 'all' as any });
    } else {
      if (selectedMonth !== null) {
        onFilterChange({ year, month: selectedMonth });
      } else {
        onFilterChange({ year });
      }
    }
  };

  const handleSelectMonth = (monthNum: number | null) => {
    setIsCustomActive(false);
    setSelectedMonth(monthNum);
    setMonthDropdownOpen(false);

    // If previously in 'all' years mode, switch to 2026 when picking a specific month
    const effectiveYear = selectedYear === 'all' ? 2026 : selectedYear;
    if (selectedYear === 'all') {
      setSelectedYear(2026);
    }

    if (monthNum === null) {
      onFilterChange({ year: effectiveYear });
    } else {
      onFilterChange({ year: effectiveYear, month: monthNum });
    }
  };

  const handleApplyCustom = () => {
    if (customStartDate && customEndDate) {
      setIsCustomActive(true);
      setCustomModalOpen(false);
      onFilterChange({
        start_date: customStartDate.trim(),
        end_date: customEndDate.trim(),
      });
    }
  };

  return (
    <View style={styles.card}>
      {/* Modern Side-by-Side Dropdown Selectors */}
      <View style={styles.dropdownRow}>
        {/* YEAR DROPDOWN FIELD */}
        <View style={styles.dropdownFieldContainer}>
          <Text style={styles.fieldLabel}>YEAR</Text>
          <TouchableOpacity
            style={[styles.dropdownButton, yearDropdownOpen && styles.dropdownButtonActive]}
            onPress={() => setYearDropdownOpen(true)}
            disabled={loading}
            activeOpacity={0.75}
          >
            <View style={styles.btnContent}>
              <Ionicons name="calendar-clear-outline" size={16} color={Colors.primary} />
              <Text style={styles.dropdownSelectedText} numberOfLines={1}>
                {isCustomActive ? 'Custom' : selectedYear === 'all' ? 'All Years' : `Year ${selectedYear}`}
              </Text>
            </View>
            <Ionicons
              name={yearDropdownOpen ? 'chevron-up' : 'chevron-down'}
              size={16}
              color={Colors.textSecondary}
            />
          </TouchableOpacity>
        </View>

        <View style={{ width: Spacing.sm }} />

        {/* MONTH DROPDOWN FIELD */}
        <View style={[styles.dropdownFieldContainer, { flex: 1.5 }]}>
          <Text style={styles.fieldLabel}>MONTH / PERIOD</Text>
          <TouchableOpacity
            style={[styles.dropdownButton, monthDropdownOpen && styles.dropdownButtonActive]}
            onPress={() => setMonthDropdownOpen(true)}
            disabled={loading}
            activeOpacity={0.75}
          >
            <View style={styles.btnContent}>
              <Ionicons name="time-outline" size={16} color={Colors.secondary} />
              <Text style={styles.dropdownSelectedText} numberOfLines={1}>
                {isCustomActive
                  ? `${customStartDate.slice(5)} → ${customEndDate.slice(5)}`
                  : selectedYear === 'all'
                  ? 'All Months'
                  : activeMonthObj.name}
              </Text>
            </View>
            <Ionicons
              name={monthDropdownOpen ? 'chevron-up' : 'chevron-down'}
              size={16}
              color={Colors.textSecondary}
            />
          </TouchableOpacity>
        </View>
      </View>

      {/* Date Range Custom Filter Action (Properly Integrated) */}
      <View style={styles.customDateRow}>
        <TouchableOpacity
          style={[styles.customDateBtn, isCustomActive && styles.customDateBtnActive]}
          onPress={() => setCustomModalOpen(true)}
          activeOpacity={0.75}
        >
          <View style={styles.customDateLeft}>
            <Ionicons
              name="calendar-outline"
              size={15}
              color={isCustomActive ? Colors.primaryDark : Colors.textSecondary}
            />
            <Text
              style={[styles.customDateText, isCustomActive && styles.customDateTextActive]}
              numberOfLines={1}
            >
              {isCustomActive
                ? `From: ${customStartDate}   To: ${customEndDate}`
                : 'From Date — To Date'}
            </Text>
          </View>

          {isCustomActive ? (
            <TouchableOpacity
              style={styles.resetBadge}
              onPress={(e) => {
                e.stopPropagation();
                setIsCustomActive(false);
                onFilterChange({
                  year: selectedYear === 'all' ? ('all' as any) : selectedYear,
                  month: selectedMonth ?? undefined,
                });
              }}
              activeOpacity={0.7}
            >
              <Text style={styles.resetBadgeText}>Reset ✕</Text>
            </TouchableOpacity>
          ) : (
            <View style={styles.setDatesBadge}>
              <Text style={styles.setDatesText}>Select</Text>
            </View>
          )}
        </TouchableOpacity>
      </View>

      {/* ------------------------------------------------------------- */}
      {/* YEAR SELECTOR MODAL                                           */}
      {/* ------------------------------------------------------------- */}
      <Modal
        visible={yearDropdownOpen}
        transparent
        animationType="fade"
        onRequestClose={() => setYearDropdownOpen(false)}
      >
        <Pressable
          style={styles.modalOverlay}
          onPress={() => setYearDropdownOpen(false)}
        >
          <Pressable style={styles.modalContentCard} onPress={(e) => e.stopPropagation()}>
            <View style={styles.modalHeader}>
              <View style={styles.modalHeaderTitleGroup}>
                <Ionicons name="calendar-outline" size={20} color={Colors.primary} />
                <Text style={styles.modalTitle}>Select Reporting Year</Text>
              </View>
              <TouchableOpacity
                onPress={() => setYearDropdownOpen(false)}
                style={styles.modalCloseBtn}
              >
                <Ionicons name="close" size={20} color={Colors.textMuted} />
              </TouchableOpacity>
            </View>

            <Text style={styles.modalSubtitle}>
              Filter all departmental analytics and complaint frequency by fiscal year or all time:
            </Text>

            <View style={styles.optionsList}>
              {AVAILABLE_YEARS.map((yr) => {
                const isSelected = !isCustomActive && selectedYear === yr.id;
                const isAll = yr.id === 'all';
                return (
                  <TouchableOpacity
                    key={String(yr.id)}
                    style={[
                      styles.optionItem,
                      isSelected && styles.optionItemActive,
                      isAll && styles.allYearOptionItem,
                    ]}
                    onPress={() => handleSelectYear(yr.id)}
                    activeOpacity={0.7}
                  >
                    <View style={styles.optionLeft}>
                      <View
                        style={[
                          styles.optionRadio,
                          isSelected && styles.optionRadioActive,
                        ]}
                      >
                        {isSelected && <View style={styles.optionRadioInner} />}
                      </View>
                      <View>
                        <Text
                          style={[
                            styles.optionText,
                            isSelected && styles.optionTextActive,
                            isAll && styles.allYearText,
                          ]}
                        >
                          {yr.label}
                        </Text>
                        {yr.desc && (
                          <Text style={styles.optionDescription}>{yr.desc}</Text>
                        )}
                      </View>
                    </View>

                    {isSelected && (
                      <Ionicons name="checkmark-circle" size={20} color={Colors.primary} />
                    )}
                  </TouchableOpacity>
                );
              })}
            </View>
          </Pressable>
        </Pressable>
      </Modal>

      {/* ------------------------------------------------------------- */}
      {/* MONTH / REPORTING PERIOD SELECTOR MODAL                       */}
      {/* ------------------------------------------------------------- */}
      <Modal
        visible={monthDropdownOpen}
        transparent
        animationType="fade"
        onRequestClose={() => setMonthDropdownOpen(false)}
      >
        <Pressable
          style={styles.modalOverlay}
          onPress={() => setMonthDropdownOpen(false)}
        >
          <Pressable style={[styles.modalContentCard, { maxHeight: '82%' }]} onPress={(e) => e.stopPropagation()}>
            <View style={styles.modalHeader}>
              <View style={styles.modalHeaderTitleGroup}>
                <Ionicons name="calendar" size={20} color={Colors.secondary} />
                <Text style={styles.modalTitle}>Select Reporting Month</Text>
              </View>
              <TouchableOpacity
                onPress={() => setMonthDropdownOpen(false)}
                style={styles.modalCloseBtn}
              >
                <Ionicons name="close" size={20} color={Colors.textMuted} />
              </TouchableOpacity>
            </View>

            <Text style={styles.modalSubtitle}>
              Select an individual month or evaluate the full year aggregated:
            </Text>

            <ScrollView showsVerticalScrollIndicator={false} style={styles.modalScroll}>
              {MONTH_OPTIONS.map((m) => {
                const isSelected = !isCustomActive && selectedMonth === m.num;
                const isAllYear = m.num === null;

                return (
                  <TouchableOpacity
                    key={m.name}
                    style={[
                      styles.optionItem,
                      isSelected && styles.optionItemActive,
                      isAllYear && styles.allYearOptionItem,
                    ]}
                    onPress={() => handleSelectMonth(m.num)}
                    activeOpacity={0.7}
                  >
                    <View style={styles.optionLeft}>
                      <View
                        style={[
                          styles.optionRadio,
                          isSelected && styles.optionRadioActive,
                        ]}
                      >
                        {isSelected && <View style={styles.optionRadioInner} />}
                      </View>
                      <View>
                        <Text
                          style={[
                            styles.optionText,
                            isSelected && styles.optionTextActive,
                            isAllYear && styles.allYearText,
                          ]}
                        >
                          {m.name}
                        </Text>
                        {isAllYear && (
                          <Text style={styles.optionDescription}>
                            Aggregated metrics for all 12 months in {selectedYear}
                          </Text>
                        )}
                      </View>
                    </View>

                    {isSelected && (
                      <Ionicons name="checkmark-circle" size={20} color={Colors.primary} />
                    )}
                  </TouchableOpacity>
                );
              })}
            </ScrollView>
          </Pressable>
        </Pressable>
      </Modal>

      {/* ------------------------------------------------------------- */}
      {/* CUSTOM DATE RANGE MODAL                                       */}
      {/* ------------------------------------------------------------- */}
      <Modal
        visible={customModalOpen}
        transparent
        animationType="fade"
        onRequestClose={() => setCustomModalOpen(false)}
      >
        <Pressable
          style={styles.modalOverlay}
          onPress={() => setCustomModalOpen(false)}
        >
          <Pressable style={styles.modalContentCard} onPress={(e) => e.stopPropagation()}>
            <View style={styles.modalHeader}>
              <View style={styles.modalHeaderTitleGroup}>
                <Ionicons name="options" size={20} color={Colors.primary} />
                <Text style={styles.modalTitle}>Custom Date Range</Text>
              </View>
              <TouchableOpacity
                onPress={() => setCustomModalOpen(false)}
                style={styles.modalCloseBtn}
              >
                <Ionicons name="close" size={20} color={Colors.textMuted} />
              </TouchableOpacity>
            </View>

            <View style={[styles.inputGroup, { marginTop: Spacing.md }]}>
              <Text style={styles.inputLabel}>FROM DATE</Text>
              <TextInput
                style={styles.textInput}
                value={customStartDate}
                onChangeText={setCustomStartDate}
                placeholder="2026-01-01"
                placeholderTextColor={Colors.textMuted}
                autoCapitalize="none"
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>TO DATE</Text>
              <TextInput
                style={styles.textInput}
                value={customEndDate}
                onChangeText={setCustomEndDate}
                placeholder="2026-01-31"
                placeholderTextColor={Colors.textMuted}
                autoCapitalize="none"
              />
            </View>

            {/* Modal Actions */}
            <View style={[styles.modalActionRow, { marginTop: Spacing.md }]}>
              <TouchableOpacity
                style={styles.cancelButton}
                onPress={() => setCustomModalOpen(false)}
              >
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.applyButton}
                onPress={handleApplyCustom}
              >
                <Text style={styles.applyButtonText}>Apply Filter</Text>
              </TouchableOpacity>
            </View>
          </Pressable>
        </Pressable>
      </Modal>
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
  customDateRow: {
    marginTop: Spacing.sm,
  },
  customDateBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#E2E8F0',
    borderRadius: BorderRadius.md,
    paddingHorizontal: Spacing.sm + 2,
    paddingVertical: 8,
  },
  customDateBtnActive: {
    backgroundColor: '#EFF6FF',
    borderColor: '#BFDBFE',
  },
  customDateLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    marginRight: Spacing.xs,
  },
  customDateText: {
    fontSize: 11,
    fontWeight: '600',
    color: Colors.textSecondary,
    marginLeft: 6,
  },
  customDateTextActive: {
    color: Colors.primaryDark,
    fontWeight: '700',
  },
  setDatesBadge: {
    backgroundColor: '#F1F5F9',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: BorderRadius.sm,
  },
  setDatesText: {
    fontSize: 10,
    fontWeight: '700',
    color: Colors.textSecondary,
  },
  resetBadge: {
    backgroundColor: Colors.secondary,
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: BorderRadius.sm,
  },
  resetBadgeText: {
    fontSize: 10,
    fontWeight: '800',
    color: '#FFFFFF',
  },
  dropdownRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  dropdownFieldContainer: {
    flex: 1,
  },
  fieldLabel: {
    fontSize: 10,
    fontWeight: '800',
    color: Colors.textMuted,
    letterSpacing: 0.8,
    marginBottom: 5,
    textTransform: 'uppercase',
  },
  dropdownButton: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#F8FAFC',
    borderWidth: 1.2,
    borderColor: '#CBD5E1',
    borderRadius: BorderRadius.md,
    paddingHorizontal: Spacing.sm + 2,
    paddingVertical: 10,
  },
  dropdownButtonActive: {
    borderColor: Colors.primary,
    backgroundColor: '#EFF6FF',
  },
  btnContent: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  dropdownSelectedText: {
    fontSize: Typography.fontSize.sm,
    fontWeight: '700',
    color: Colors.textPrimary,
    marginLeft: Spacing.xs + 2,
  },

  // Modals
  modalOverlay: {
    flex: 1,
    backgroundColor: Colors.overlay,
    justifyContent: 'center',
    alignItems: 'center',
    padding: Spacing.lg,
  },
  modalContentCard: {
    width: '100%',
    maxWidth: 390,
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.xl,
    padding: Spacing.lg,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.2,
    shadowRadius: 16,
    elevation: 10,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.xs,
  },
  modalHeaderTitleGroup: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  modalTitle: {
    fontSize: Typography.fontSize.md,
    fontWeight: '900',
    color: Colors.textPrimary,
    marginLeft: Spacing.xs,
  },
  modalCloseBtn: {
    padding: 4,
  },
  modalSubtitle: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textMuted,
    lineHeight: 18,
    marginBottom: Spacing.md,
  },
  modalScroll: {
    maxHeight: 340,
  },
  optionsList: {
    marginVertical: Spacing.xs,
  },
  optionItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: Spacing.md,
    borderRadius: BorderRadius.md,
    backgroundColor: '#F8FAFC',
    marginBottom: Spacing.xs,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  optionItemActive: {
    backgroundColor: '#EFF6FF',
    borderColor: '#93C5FD',
  },
  allYearOptionItem: {
    borderLeftWidth: 4,
    borderLeftColor: Colors.secondary,
    marginBottom: Spacing.sm,
  },
  allYearText: {
    color: Colors.primaryDark,
    fontWeight: '800',
  },
  optionLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  optionRadio: {
    width: 18,
    height: 18,
    borderRadius: 9,
    borderWidth: 2,
    borderColor: '#94A3B8',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: Spacing.sm,
  },
  optionRadioActive: {
    borderColor: Colors.primary,
  },
  optionRadioInner: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: Colors.primary,
  },
  optionText: {
    fontSize: Typography.fontSize.sm,
    fontWeight: '600',
    color: Colors.textPrimary,
  },
  optionTextActive: {
    fontWeight: '800',
    color: Colors.primaryDark,
  },
  optionDescription: {
    fontSize: 10,
    color: Colors.textMuted,
    marginTop: 2,
  },

  // Custom Range Modal Inputs
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
  textInput: {
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: BorderRadius.md,
    paddingHorizontal: Spacing.md,
    paddingVertical: 9,
    fontSize: Typography.fontSize.sm,
    color: Colors.textPrimary,
  },
  presetRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 4,
    marginBottom: Spacing.md,
  },
  presetChip: {
    backgroundColor: '#F1F5F9',
    paddingHorizontal: Spacing.sm + 2,
    paddingVertical: 6,
    borderRadius: BorderRadius.sm,
    marginRight: Spacing.xs,
    marginTop: 4,
  },
  presetChipText: {
    fontSize: 11,
    fontWeight: '700',
    color: Colors.primary,
  },
  modalActionRow: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    marginTop: Spacing.sm,
  },
  cancelButton: {
    paddingHorizontal: Spacing.md,
    paddingVertical: 10,
    marginRight: Spacing.sm,
  },
  cancelButtonText: {
    fontSize: Typography.fontSize.sm,
    fontWeight: '600',
    color: Colors.textSecondary,
  },
  applyButton: {
    backgroundColor: Colors.primary,
    paddingHorizontal: Spacing.lg,
    paddingVertical: 10,
    borderRadius: BorderRadius.md,
  },
  applyButtonText: {
    fontSize: Typography.fontSize.sm,
    fontWeight: '800',
    color: '#FFFFFF',
  },
});
