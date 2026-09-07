import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { Colors, Spacing, BorderRadius, Typography } from '../../constants/theme';
import { ComplaintsApi, DashboardData } from '../../api/complaints';
import { Ionicons } from '@expo/vector-icons';

export const ReportsScreen: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);

  const fetchReports = async () => {
    try {
      const resp = await ComplaintsApi.getDashboard();
      setData(resp);
    } catch (err) {
      console.warn('[ReportsScreen] Load error:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    fetchReports();
  };

  const resolutionRate = data?.metrics.total && data.metrics.total > 0
    ? Math.round((data.metrics.resolved / data.metrics.total) * 100)
    : 0;

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={[Colors.primary]} />}
    >
      <View style={styles.headerBox}>
        <Text style={styles.title}>CMS Performance Analytics</Text>
        <Text style={styles.subtitle}>Departmental Resolution & Breakdown Metrics</Text>
      </View>

      {loading ? (
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color={Colors.primary} />
          <Text style={styles.loadingText}>Compiling departmental metrics...</Text>
        </View>
      ) : data ? (
        <>
          {/* Resolution Rate Card */}
          <View style={styles.rateCard}>
            <View style={styles.rateRow}>
              <View>
                <Text style={styles.rateLabel}>Resolution Efficiency</Text>
                <Text style={styles.ratePercent}>{resolutionRate}%</Text>
                <Text style={styles.rateSubtext}>
                  {data.metrics.resolved.toLocaleString()} resolved of {data.metrics.total.toLocaleString()} total
                </Text>
              </View>
              <View style={styles.rateIconBox}>
                <Ionicons name="trending-up-outline" size={36} color={Colors.primary} />
              </View>
            </View>
            <View style={styles.progressBarBg}>
              <View style={[styles.progressBarFill, { width: `${resolutionRate}%` }]} />
            </View>
          </View>

          {/* Category Distribution Card */}
          <View style={styles.card}>
            <View style={styles.cardHeader}>
              <Ionicons name="pie-chart-outline" size={20} color={Colors.primary} />
              <Text style={styles.cardTitle}>Complaints by Category</Text>
            </View>

            {data.type_distribution.map((cat, idx) => {
              const catPercent = data.metrics.total > 0 ? Math.round((cat.count / data.metrics.total) * 100) : 0;
              return (
                <View key={idx} style={styles.catItem}>
                  <View style={styles.catHeader}>
                    <Text style={styles.catName}>{cat.category}</Text>
                    <Text style={styles.catCount}>{cat.count.toLocaleString()} ({catPercent}%)</Text>
                  </View>
                  <View style={styles.catBarBg}>
                    <View style={[styles.catBarFill, { width: `${catPercent}%` }]} />
                  </View>
                </View>
              );
            })}
          </View>

          {/* Zone Distribution Card */}
          <View style={styles.card}>
            <View style={styles.cardHeader}>
              <Ionicons name="map-outline" size={20} color={Colors.secondary} />
              <Text style={styles.cardTitle}>Complaints by Zone</Text>
            </View>

            {data.zone_distribution.map((z, idx) => {
              const zonePercent = data.metrics.total > 0 ? Math.round((z.count / data.metrics.total) * 100) : 0;
              return (
                <View key={idx} style={styles.catItem}>
                  <View style={styles.catHeader}>
                    <Text style={styles.catName}>{z.zone}</Text>
                    <Text style={styles.catCount}>{z.count.toLocaleString()} ({zonePercent}%)</Text>
                  </View>
                  <View style={styles.catBarBg}>
                    <View style={[styles.catBarFill, { width: `${zonePercent}%`, backgroundColor: Colors.secondary }]} />
                  </View>
                </View>
              );
            })}
          </View>
        </>
      ) : null}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  content: {
    padding: Spacing.md,
    paddingBottom: Spacing.xxl,
  },
  headerBox: {
    marginBottom: Spacing.md,
  },
  title: {
    fontSize: Typography.fontSize.xl,
    fontWeight: '900',
    color: Colors.textPrimary,
  },
  subtitle: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textMuted,
    fontWeight: '600',
    marginTop: 2,
  },
  rateCard: {
    backgroundColor: Colors.surface,
    padding: Spacing.lg,
    borderRadius: BorderRadius.lg,
    marginBottom: Spacing.md,
    borderWidth: 1,
    borderColor: Colors.border,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  rateRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: Spacing.md,
  },
  rateLabel: {
    fontSize: Typography.fontSize.xs,
    fontWeight: '800',
    color: Colors.textSecondary,
    textTransform: 'uppercase',
    letterSpacing: 0.8,
  },
  ratePercent: {
    fontSize: 42,
    fontWeight: '900',
    color: Colors.primary,
    letterSpacing: -1,
  },
  rateSubtext: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textMuted,
    fontWeight: '600',
  },
  rateIconBox: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#DCFCE7',
    alignItems: 'center',
    justifyContent: 'center',
  },
  progressBarBg: {
    height: 8,
    backgroundColor: '#F1F5F9',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    backgroundColor: Colors.primary,
    borderRadius: 4,
  },
  card: {
    backgroundColor: Colors.surface,
    padding: Spacing.md,
    borderRadius: BorderRadius.lg,
    marginBottom: Spacing.md,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: Spacing.md,
  },
  cardTitle: {
    fontSize: Typography.fontSize.md,
    fontWeight: '800',
    color: Colors.textPrimary,
    marginLeft: Spacing.xs,
  },
  catItem: {
    marginBottom: Spacing.sm,
  },
  catHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  catName: {
    fontSize: Typography.fontSize.sm,
    fontWeight: '600',
    color: Colors.textPrimary,
  },
  catCount: {
    fontSize: Typography.fontSize.xs,
    fontWeight: '700',
    color: Colors.textSecondary,
  },
  catBarBg: {
    height: 6,
    backgroundColor: '#F1F5F9',
    borderRadius: 3,
    overflow: 'hidden',
  },
  catBarFill: {
    height: '100%',
    backgroundColor: Colors.primary,
    borderRadius: 3,
  },
  centerContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: Spacing.xxl,
  },
  loadingText: {
    fontSize: Typography.fontSize.xs,
    color: Colors.textMuted,
    marginTop: Spacing.sm,
  },
});
