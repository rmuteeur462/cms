import React from 'react';
import { View, Text, StyleSheet, ViewStyle } from 'react-native';
import { Colors, Spacing, BorderRadius, Typography } from '../../constants/theme';

interface StatusBadgeProps {
  status: string;
  style?: ViewStyle;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, style }) => {
  const norm = status.toLowerCase().trim();

  let bg = Colors.status.inProgressBg;
  let text = Colors.status.inProgress;
  let label = status;

  if (norm === 'resolved') {
    bg = Colors.status.resolvedBg;
    text = Colors.status.resolved;
    label = 'RESOLVED';
  } else if (norm === 'pending') {
    bg = Colors.status.pendingBg;
    text = Colors.status.pending;
    label = 'PENDING';
  } else if (norm.includes('zone')) {
    bg = '#E0F2FE';
    text = '#0369A1';
    label = status.toUpperCase();
  }

  return (
    <View style={[styles.badge, { backgroundColor: bg }, style]}>
      <View style={[styles.dot, { backgroundColor: text }]} />
      <Text style={[styles.label, { color: text }]}>{label}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 4,
    paddingHorizontal: Spacing.sm,
    borderRadius: BorderRadius.full,
    alignSelf: 'flex-start',
  },
  dot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    marginRight: 6,
  },
  label: {
    fontSize: Typography.fontSize.xs,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
});
