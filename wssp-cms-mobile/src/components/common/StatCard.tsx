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
  const formattedValue = typeof value === 'number' ? value.toLocaleString() : String(value);

  // Dynamic font sizing depending on text length to guarantee it always fits comfortably
  const isLargeNumber = formattedValue.length > 5;
  const isMediumNumber = formattedValue.length > 4;

  return (
    <TouchableOpacity
      activeOpacity={onPress ? 0.75 : 1}
      onPress={onPress}
      style={[styles.card, { borderTopColor: color }]}
    >
      <View style={styles.topRow}>
        <View style={[styles.iconBox, { backgroundColor: bgColor }]}>
          <Ionicons name={icon} size={14} color={color} />
        </View>
        <Text
          style={[
            styles.valueText,
            { color },
            isMediumNumber && styles.valueTextMedium,
            isLargeNumber && styles.valueTextLarge,
          ]}
          numberOfLines={1}
          adjustsFontSizeToFit
          minimumFontScale={0.65}
        >
          {formattedValue}
        </Text>
      </View>
      <Text style={styles.titleText} numberOfLines={1}>{title}</Text>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  card: {
    flex: 1,
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.md,
    paddingHorizontal: 8,
    paddingVertical: 10,
    borderWidth: 1,
    borderColor: Colors.border,
    borderTopWidth: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.04,
    shadowRadius: 4,
    elevation: 1,
    minHeight: 76,
    justifyContent: 'space-between',
    overflow: 'hidden',
  },
  topRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 6,
    gap: 4,
  },
  iconBox: {
    width: 24,
    height: 24,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
  },
  valueText: {
    fontSize: 18,
    fontWeight: '900',
    letterSpacing: -0.3,
    flexShrink: 1,
    textAlign: 'right',
  },
  valueTextMedium: {
    fontSize: 16,
  },
  valueTextLarge: {
    fontSize: 14,
  },
  titleText: {
    fontSize: 10,
    fontWeight: '800',
    color: Colors.textSecondary,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
});
