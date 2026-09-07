import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Colors, Spacing, Typography } from '../../constants/theme';
import { Ionicons } from '@expo/vector-icons';
import { WSSPButton } from './WSSPButton';

interface EmptyStateProps {
  icon?: keyof typeof Ionicons.glyphMap;
  title: string;
  description: string;
  actionTitle?: string;
  onAction?: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon = 'file-tray-outline',
  title,
  description,
  actionTitle,
  onAction,
}) => {
  return (
    <View style={styles.container}>
      <View style={styles.iconCircle}>
        <Ionicons name={icon} size={36} color={Colors.textMuted} />
      </View>
      <Text style={styles.title}>{title}</Text>
      <Text style={styles.description}>{description}</Text>
      {actionTitle && onAction && (
        <WSSPButton
          title={actionTitle}
          onPress={onAction}
          variant="secondary"
          style={styles.btn}
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: Spacing.xl,
    marginVertical: Spacing.lg,
  },
  iconCircle: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: '#F1F5F9',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: Spacing.md,
  },
  title: {
    fontSize: Typography.fontSize.md,
    fontWeight: '800',
    color: Colors.textPrimary,
    textAlign: 'center',
    marginBottom: 4,
  },
  description: {
    fontSize: Typography.fontSize.sm,
    color: Colors.textMuted,
    textAlign: 'center',
    lineHeight: 20,
    maxWidth: 280,
  },
  btn: {
    marginTop: Spacing.md,
    height: 40,
    paddingHorizontal: Spacing.md,
  },
});
