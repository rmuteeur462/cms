import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors, Spacing, BorderRadius, Typography } from '../../constants/theme';
import { TypeDistributionItem, SubtypeDistributionItem } from '../../api/complaints';

interface CategoryDistributionChartProps {
  isSingleDepartment: boolean;
  typeDistribution: TypeDistributionItem[];
  subtypeDistribution: SubtypeDistributionItem[];
  departmentName?: string;
  onItemPress?: (item: { id?: number | null; name: string; isSubtype: boolean; count: number }) => void;
}

const PALETTE = [
  Colors.primary,
  Colors.secondary,
  '#8B5CF6', // Purple
  '#06B6D4', // Cyan
  '#10B981', // Emerald
  '#F59E0B', // Amber
  '#EC4899', // Pink
];

export const CategoryDistributionChart: React.FC<CategoryDistributionChartProps> = ({
  isSingleDepartment,
  typeDistribution,
  subtypeDistribution,
  departmentName,
  onItemPress,
}) => {
  // If single department, show subtypes; otherwise show types
  const items = isSingleDepartment
    ? subtypeDistribution
    : typeDistribution;

  const title = isSingleDepartment
    ? `${departmentName || 'Departmental'} Subtype Breakdown`
    : 'Complaints by Department';

  const subtitle = isSingleDepartment
    ? 'Distribution of specific issues in your queue'
    : 'Cross-departmental municipal distribution';

  const iconName = isSingleDepartment ? 'list-outline' : 'pie-chart-outline';
  const iconColor = isSingleDepartment ? Colors.secondary : Colors.primary;

  return (
    <View style={styles.card}>
      <View style={styles.cardHeader}>
        <View style={[styles.iconBox, { backgroundColor: isSingleDepartment ? '#FFF4E6' : '#EFF6FF' }]}>
          <Ionicons name={iconName} size={18} color={iconColor} />
        </View>
        <View style={styles.headerText}>
          <Text style={styles.cardTitle}>{title}</Text>
          <Text style={styles.cardSubtitle}>{subtitle}</Text>
        </View>
        <View style={styles.headerBadge}>
          <Ionicons name="hand-left-outline" size={11} color={Colors.textMuted} style={{ marginRight: 3 }} />
          <Text style={styles.headerBadgeText}>Tap to view</Text>
        </View>
      </View>

      {items.length === 0 ? (
        <View style={styles.emptyBox}>
          <Text style={styles.emptyText}>No category data available for this period.</Text>
        </View>
      ) : (
        <View style={styles.listContainer}>
          {items.slice(0, 7).map((item, index) => {
            const barColor = PALETTE[index % PALETTE.length];
            return (
              <TouchableOpacity
                key={item.id ?? index}
                style={styles.itemRow}
                activeOpacity={0.7}
                onPress={() => {
                  if (onItemPress) {
                    onItemPress({
                      id: item.id,
                      name: item.name,
                      isSubtype: isSingleDepartment,
                      count: item.count,
                    });
                  }
                }}
              >
                <View style={styles.itemHeader}>
                  <View style={styles.itemTitleRow}>
                    <View style={[styles.bullet, { backgroundColor: barColor }]} />
                    <Text style={styles.itemName} numberOfLines={1}>
                      {item.name}
                    </Text>
                  </View>
                  <View style={styles.metaRow}>
                    <Text style={styles.itemMeta}>
                      <Text style={styles.itemCount}>{item.count.toLocaleString()}</Text>{' '}
                      <Text style={styles.itemPct}>({item.percentage}%)</Text>
                    </Text>
                    <Ionicons name="chevron-forward" size={14} color={Colors.textMuted} style={styles.chevron} />
                  </View>
                </View>

                {/* Progress bar */}
                <View style={styles.barBg}>
                  <View
                    style={[
                      styles.barFill,
                      {
                        width: `${Math.max(item.percentage, 2)}%`,
                        backgroundColor: barColor,
                      },
                    ]}
                  />
                </View>
              </TouchableOpacity>
            );
          })}
        </View>
      )}
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
    alignItems: 'center',
    marginBottom: Spacing.md,
  },
  iconBox: {
    width: 34,
    height: 34,
    borderRadius: BorderRadius.md,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: Spacing.sm,
  },
  headerText: {
    flex: 1,
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
  listContainer: {
    marginTop: 2,
  },
  itemRow: {
    paddingVertical: 6,
    paddingHorizontal: 8,
    borderRadius: BorderRadius.sm,
    marginBottom: Spacing.xs,
  },
  itemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  itemTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    paddingRight: Spacing.sm,
  },
  bullet: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 6,
  },
  itemName: {
    fontSize: Typography.fontSize.xs,
    fontWeight: '700',
    color: Colors.textPrimary,
    flex: 1,
  },
  itemMeta: {
    fontSize: Typography.fontSize.xs,
  },
  metaRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  chevron: {
    marginLeft: 2,
    opacity: 0.6,
  },
  headerBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F1F5F9',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: BorderRadius.full,
  },
  headerBadgeText: {
    fontSize: Typography.fontSize.xs - 2,
    fontWeight: '700',
    color: Colors.textMuted,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  itemCount: {
    fontWeight: '800',
    color: Colors.textPrimary,
  },
  itemPct: {
    color: Colors.textMuted,
    fontWeight: '600',
  },
  barBg: {
    height: 6,
    backgroundColor: '#F1F5F9',
    borderRadius: 3,
    overflow: 'hidden',
  },
  barFill: {
    height: '100%',
    borderRadius: 3,
  },
  emptyBox: {
    paddingVertical: Spacing.md,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textMuted,
    fontStyle: 'italic',
  },
});
