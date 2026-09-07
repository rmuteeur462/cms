import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Colors, Spacing, BorderRadius, Typography } from '../../constants/theme';
import { Ionicons } from '@expo/vector-icons';

interface StatCardProps {
  title: string;
  value: number | string;
  icon: keyof typeof Ionicons.glyphMap;
  color?: string;
  bgColor?: string;
  onPress?: () => void;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  icon,
  color = Colors.primary,
  bgColor = '#F1F5F9',
  onPress,
}) => {
  return (
    <TouchableOpacity
      activeOpacity={onPress ? 0.75 : 1}
      onPress={onPress}
      style={[styles.card, { borderTopColor: color }]}
    >
      <View style={styles.topRow}>
        <View style={[styles.iconBox, { backgroundColor: bgColor }]}>
          <Ionicons name={icon} size={20} color={color} />
        </View>
        <Text style={styles.valueText}>{typeof value === 'number' ? value.toLocaleString() : value}</Text>
      </View>
      <Text style={styles.titleText}>{title}</Text>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  card: {
    flex: 1,
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.lg,
    padding: Spacing.md,
    borderWidth: 1,
    borderColor: Colors.border,
    borderTopWidth: 3.5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04,
    shadowRadius: 6,
    elevation: 2,
    minHeight: 100,
    justifyContent: 'space-between',
  },
  topRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  iconBox: {
    width: 36,
    height: 36,
    borderRadius: 18,
    alignItems: 'center',
    justifyContent: 'center',
  },
  valueText: {
    fontSize: Typography.fontSize.xxl,
    fontWeight: '900',
    color: Colors.textPrimary,
    letterSpacing: 0.5,
  },
  titleText: {
    fontSize: Typography.fontSize.xs,
    fontWeight: '700',
    color: Colors.textSecondary,
    textTransform: 'uppercase',
    letterSpacing: 0.8,
    marginTop: Spacing.xs,
  },
});
