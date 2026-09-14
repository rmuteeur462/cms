import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Modal,
  Platform,
} from 'react-native';
import { Colors, Spacing, BorderRadius, Typography } from '../../constants/theme';
import { useAuth } from '../../store/AuthContext';
import { Ionicons } from '@expo/vector-icons';

export const ProfileScreen: React.FC = () => {
  const { user, logout } = useAuth();
  const [showConfirmModal, setShowConfirmModal] = useState<boolean>(false);
  const [isSigningOut, setIsSigningOut] = useState<boolean>(false);

  const handleSignOutPress = () => {
    setShowConfirmModal(true);
  };

  const handleConfirmSignOut = async () => {
    setIsSigningOut(true);
    try {
      await logout();
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      setIsSigningOut(false);
      setShowConfirmModal(false);
    }
  };

  if (!user) return null;

  const initial = user.full_name
    ? user.full_name.charAt(0).toUpperCase()
    : (user.username ? user.username.charAt(0).toUpperCase() : 'U');

  return (
    <View style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
      >
        {/* Simple Profile Header Card */}
        <View style={styles.profileCard}>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>{initial}</Text>
          </View>
          <Text style={styles.userName}>{user.full_name || user.username}</Text>
          <Text style={styles.userUsername}>@{user.username}</Text>
          <View style={styles.roleBadge}>
            <Ionicons name="shield-checkmark" size={13} color="#007BFF" style={{ marginRight: 4 }} />
            <Text style={styles.roleBadgeText}>{user.role || 'Officer'}</Text>
          </View>
        </View>

        {/* Simple Details Card */}
        <View style={styles.detailsCard}>
          <Text style={styles.sectionTitle}>Account Details</Text>

          <View style={styles.infoRow}>
            <View style={styles.infoLabelGroup}>
              <Ionicons name="mail-outline" size={16} color="#6C757D" style={styles.infoIcon} />
              <Text style={styles.infoLabel}>Email</Text>
            </View>
            <Text style={styles.infoValue}>{user.email || 'officer@wssp.gov.pk'}</Text>
          </View>

          <View style={styles.infoRow}>
            <View style={styles.infoLabelGroup}>
              <Ionicons name="location-outline" size={16} color="#6C757D" style={styles.infoIcon} />
              <Text style={styles.infoLabel}>Assigned Zone</Text>
            </View>
            <Text style={styles.infoValue}>
              {user.allowed_locations && user.allowed_locations.length > 0
                ? user.allowed_locations.map((l) => l.name).join(', ')
                : 'All Zones'}
            </Text>
          </View>

          <View style={styles.infoRow}>
            <View style={styles.infoLabelGroup}>
              <Ionicons name="business-outline" size={16} color="#6C757D" style={styles.infoIcon} />
              <Text style={styles.infoLabel}>Department</Text>
            </View>
            <Text style={styles.infoValue}>WSSP Peshawar</Text>
          </View>

          <View style={[styles.infoRow, { borderBottomWidth: 0 }]}>
            <View style={styles.infoLabelGroup}>
              <Ionicons name="call-outline" size={16} color="#6C757D" style={styles.infoIcon} />
              <Text style={styles.infoLabel}>Helpline</Text>
            </View>
            <Text style={[styles.infoValue, { color: Colors.primary, fontWeight: '700' }]}>1334</Text>
          </View>
        </View>

        {/* Simple Sign Out Button */}
        <TouchableOpacity
          style={styles.signOutButton}
          onPress={handleSignOutPress}
          activeOpacity={0.8}
          accessibilityLabel="Sign out"
        >
          <Ionicons name="log-out-outline" size={18} color="#DC3545" style={{ marginRight: 8 }} />
          <Text style={styles.signOutButtonText}>Sign Out</Text>
        </TouchableOpacity>
      </ScrollView>

      {/* Cross-platform Sign Out Confirmation Modal */}
      <Modal
        visible={showConfirmModal}
        transparent
        animationType="fade"
        onRequestClose={() => {
          if (!isSigningOut) setShowConfirmModal(false);
        }}
      >
        <View style={styles.modalBackdrop}>
          <View style={styles.modalCard}>
            <View style={styles.modalIconBox}>
              <Ionicons name="log-out-outline" size={32} color="#DC3545" />
            </View>
            <Text style={styles.modalTitle}>Sign Out</Text>
            <Text style={styles.modalSubtitle}>
              Are you sure you want to sign out of your account?
            </Text>

            <View style={styles.modalActions}>
              <TouchableOpacity
                style={styles.cancelBtn}
                onPress={() => setShowConfirmModal(false)}
                disabled={isSigningOut}
              >
                <Text style={styles.cancelBtnText}>Cancel</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.confirmSignOutBtn}
                onPress={handleConfirmSignOut}
                disabled={isSigningOut}
              >
                {isSigningOut ? (
                  <ActivityIndicator size="small" color="#FFFFFF" />
                ) : (
                  <Text style={styles.confirmSignOutBtnText}>Sign Out</Text>
                )}
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
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  scrollView: {
    flex: 1,
  },
  content: {
    padding: 16,
    paddingBottom: 36,
  },

  // Profile Header Card
  profileCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    paddingVertical: 24,
    paddingHorizontal: 16,
    alignItems: 'center',
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#E9ECEF',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  avatar: {
    width: 68,
    height: 68,
    borderRadius: 34,
    backgroundColor: Colors.primaryDark || '#064E3B',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
  },
  avatarText: {
    fontSize: 26,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  userName: {
    fontSize: 18,
    fontWeight: '700',
    color: '#212529',
    marginBottom: 2,
  },
  userUsername: {
    fontSize: 13,
    color: '#6C757D',
    marginBottom: 10,
  },
  roleBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#E7F1FF',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#B8DAFF',
  },
  roleBadgeText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#007BFF',
    textTransform: 'capitalize',
  },

  // Details Card
  detailsCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#E9ECEF',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#343A40',
    marginBottom: 12,
    letterSpacing: 0.2,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F1F3F5',
  },
  infoLabelGroup: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  infoIcon: {
    marginRight: 8,
  },
  infoLabel: {
    fontSize: 13.5,
    color: '#6C757D',
    fontWeight: '500',
  },
  infoValue: {
    fontSize: 13.5,
    color: '#212529',
    fontWeight: '600',
    maxWidth: '55%',
    textAlign: 'right',
  },

  // Simple Sign Out Button
  signOutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#FFF5F5',
    borderWidth: 1,
    borderColor: '#FFC9C9',
    borderRadius: 8,
    paddingVertical: 13,
    paddingHorizontal: 20,
    shadowColor: '#DC3545',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  signOutButtonText: {
    fontSize: 14.5,
    fontWeight: '700',
    color: '#DC3545',
  },

  // Confirmation Modal
  modalBackdrop: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.45)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  modalCard: {
    width: '100%',
    maxWidth: 340,
    backgroundColor: '#FFFFFF',
    borderRadius: 14,
    padding: 22,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 10,
    elevation: 8,
  },
  modalIconBox: {
    width: 54,
    height: 54,
    borderRadius: 27,
    backgroundColor: '#FFF5F5',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#212529',
    marginBottom: 6,
  },
  modalSubtitle: {
    fontSize: 13,
    color: '#6C757D',
    textAlign: 'center',
    marginBottom: 20,
    lineHeight: 18,
  },
  modalActions: {
    flexDirection: 'row',
    gap: 10,
    width: '100%',
  },
  cancelBtn: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#CED4DA',
    backgroundColor: '#FFFFFF',
    alignItems: 'center',
  },
  cancelBtnText: {
    fontSize: 13.5,
    fontWeight: '600',
    color: '#495057',
  },
  confirmSignOutBtn: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 6,
    backgroundColor: '#DC3545',
    alignItems: 'center',
    justifyContent: 'center',
  },
  confirmSignOutBtnText: {
    fontSize: 13.5,
    fontWeight: '700',
    color: '#FFFFFF',
  },
});
