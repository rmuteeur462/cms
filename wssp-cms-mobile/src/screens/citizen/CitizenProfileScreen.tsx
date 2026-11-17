import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  ActivityIndicator,
  Alert,
  Linking,
} from 'react-native';
import { useAuth } from '../../store/AuthContext';
import { AuthApi } from '../../api/auth';
import { Colors, Typography, Spacing, BorderRadius } from '../../constants/theme';
import { Ionicons } from '@expo/vector-icons';

interface CitizenProfileScreenProps {
  navigation: any;
}

export const CitizenProfileScreen: React.FC<CitizenProfileScreenProps> = ({ navigation }) => {
  const { user, logout, refreshProfile } = useAuth();

  const [isEditing, setIsEditing] = useState(false);
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [address, setAddress] = useState(user?.address || '');
  const [isSaving, setIsSaving] = useState(false);

  const handleSaveProfile = async () => {
    setIsSaving(true);
    try {
      await AuthApi.updateCitizenProfile({
        full_name: fullName.trim(),
        email: email.trim(),
        address: address.trim(),
      });
      await refreshProfile();
      setIsEditing(false);
      Alert.alert('Profile Updated', 'Your profile information has been successfully updated.');
    } catch (err: any) {
      Alert.alert('Update Failed', err.response?.data?.message || 'Failed to update profile.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleLogout = () => {
    Alert.alert('Sign Out', 'Are you sure you want to sign out from the WSSP Citizen Portal?', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Sign Out',
        style: 'destructive',
        onPress: async () => {
          await logout();
        },
      },
    ]);
  };

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.contentContainer}
      showsVerticalScrollIndicator={false}
    >
      {/* Top Banner */}
      <View style={styles.headerBox}>
        <View style={styles.avatarCircle}>
          <Ionicons name="person" size={36} color="#1E40AF" />
        </View>
        <Text style={styles.userName}>{user?.full_name || 'Citizen'}</Text>
        <Text style={styles.userRole}>Registered Citizen Account</Text>
        <Text style={styles.userMobile}>{user?.mobile_number || user?.username}</Text>
      </View>

      {/* Profile Details Card */}
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Text style={styles.cardTitle}>Personal Information</Text>
          <TouchableOpacity onPress={() => setIsEditing(!isEditing)}>
            <Text style={styles.editLink}>{isEditing ? 'Cancel' : 'Edit'}</Text>
          </TouchableOpacity>
        </View>

        {isEditing ? (
          <View style={styles.editForm}>
            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Full Name</Text>
              <TextInput
                style={styles.textInput}
                value={fullName}
                onChangeText={setFullName}
                placeholder="Full Name"
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Email Address</Text>
              <TextInput
                style={styles.textInput}
                value={email}
                onChangeText={setEmail}
                placeholder="email@example.com"
                keyboardType="email-address"
                autoCapitalize="none"
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Residential Address</Text>
              <TextInput
                style={styles.textInput}
                value={address}
                onChangeText={setAddress}
                placeholder="House #, Street #, Area"
              />
            </View>

            <TouchableOpacity
              style={[styles.saveButton, isSaving && styles.saveButtonDisabled]}
              onPress={handleSaveProfile}
              disabled={isSaving}
            >
              {isSaving ? (
                <ActivityIndicator color="#FFFFFF" size="small" />
              ) : (
                <Text style={styles.saveButtonText}>Save Changes</Text>
              )}
            </TouchableOpacity>
          </View>
        ) : (
          <View style={styles.infoList}>
            <View style={styles.infoRow}>
              <Ionicons name="call-outline" size={18} color="#64748B" />
              <View style={styles.infoTextGroup}>
                <Text style={styles.infoLabel}>Mobile Number (Login ID)</Text>
                <Text style={styles.infoValue}>{user?.mobile_number || user?.username}</Text>
              </View>
            </View>

            <View style={styles.infoRow}>
              <Ionicons name="mail-outline" size={18} color="#64748B" />
              <View style={styles.infoTextGroup}>
                <Text style={styles.infoLabel}>Email</Text>
                <Text style={styles.infoValue}>{user?.email || 'Not provided'}</Text>
              </View>
            </View>

            <View style={styles.infoRow}>
              <Ionicons name="location-outline" size={18} color="#64748B" />
              <View style={styles.infoTextGroup}>
                <Text style={styles.infoLabel}>Residential Address</Text>
                <Text style={styles.infoValue}>{user?.address || 'Not specified'}</Text>
              </View>
            </View>
          </View>
        )}
      </View>

      {/* Department Contacts Card */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>WSSP Peshawar Contacts</Text>
        <Text style={styles.contactSubtitle}>
          For emergency municipal interventions and helpline support
        </Text>

        <TouchableOpacity
          style={styles.contactRow}
          onPress={() => Linking.openURL('tel:1334')}
        >
          <View style={[styles.contactIconCircle, { backgroundColor: '#EFF6FF' }]}>
            <Ionicons name="call" size={18} color="#2563EB" />
          </View>
          <View style={styles.contactTextGroup}>
            <Text style={styles.contactTitle}>Citizen Helpline (Toll-Free)</Text>
            <Text style={styles.contactDetail}>1334</Text>
          </View>
          <Ionicons name="chevron-forward" size={16} color="#94A3B8" />
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.contactRow}
          onPress={() => Linking.openURL('tel:0919213456')}
        >
          <View style={[styles.contactIconCircle, { backgroundColor: '#F0FDF4' }]}>
            <Ionicons name="business" size={18} color="#16A34A" />
          </View>
          <View style={styles.contactTextGroup}>
            <Text style={styles.contactTitle}>WSSP Head Office</Text>
            <Text style={styles.contactDetail}>091-9213456</Text>
          </View>
          <Ionicons name="chevron-forward" size={16} color="#94A3B8" />
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.contactRow}
          onPress={() => Linking.openURL('https://wssp.org.pk')}
        >
          <View style={[styles.contactIconCircle, { backgroundColor: '#FAF5FF' }]}>
            <Ionicons name="globe-outline" size={18} color="#9333EA" />
          </View>
          <View style={styles.contactTextGroup}>
            <Text style={styles.contactTitle}>Official Website</Text>
            <Text style={styles.contactDetail}>https://wssp.org.pk</Text>
          </View>
          <Ionicons name="open-outline" size={16} color="#94A3B8" />
        </TouchableOpacity>
      </View>

      {/* Logout Action */}
      <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
        <Ionicons name="log-out-outline" size={18} color="#DC2626" />
        <Text style={styles.logoutText}>Sign Out</Text>
      </TouchableOpacity>

      <Text style={styles.versionText}>WSSP CMS Citizen Portal v1.0 • Peshawar</Text>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  contentContainer: {
    paddingBottom: Spacing.xxl + 30,
  },
  headerBox: {
    backgroundColor: '#0F2744',
    paddingTop: 20,
    paddingBottom: 28,
    alignItems: 'center',
    borderBottomLeftRadius: 24,
    borderBottomRightRadius: 24,
  },
  avatarCircle: {
    width: 68,
    height: 68,
    borderRadius: 34,
    backgroundColor: '#EFF6FF',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 10,
    borderWidth: 2,
    borderColor: '#3B82F6',
  },
  userName: {
    fontSize: Typography.fontSize.lg,
    fontWeight: '800',
    color: '#FFFFFF',
  },
  userRole: {
    fontSize: 11,
    color: '#93C5FD',
    marginTop: 2,
    fontWeight: '600',
  },
  userMobile: {
    fontSize: Typography.fontSize.xs,
    color: 'rgba(255, 255, 255, 0.7)',
    marginTop: 2,
  },
  card: {
    backgroundColor: '#FFFFFF',
    marginHorizontal: Spacing.md,
    marginTop: 14,
    borderRadius: BorderRadius.md,
    padding: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  cardTitle: {
    fontSize: Typography.fontSize.sm,
    fontWeight: '700',
    color: '#1E293B',
  },
  editLink: {
    fontSize: Typography.fontSize.xs,
    color: '#1E40AF',
    fontWeight: '700',
  },
  infoList: {
    gap: 12,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  infoTextGroup: {
    flex: 1,
  },
  infoLabel: {
    fontSize: 10,
    color: '#64748B',
    fontWeight: '600',
    textTransform: 'uppercase',
  },
  infoValue: {
    fontSize: Typography.fontSize.xs,
    color: '#1E293B',
    fontWeight: '600',
    marginTop: 2,
  },
  editForm: {
    gap: 10,
  },
  inputGroup: {
    marginBottom: 6,
  },
  inputLabel: {
    fontSize: 11,
    fontWeight: '600',
    color: '#475569',
    marginBottom: 4,
  },
  textInput: {
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#CBD5E1',
    borderRadius: BorderRadius.sm,
    paddingHorizontal: 10,
    paddingVertical: 7,
    fontSize: Typography.fontSize.xs,
    color: '#1E293B',
  },
  saveButton: {
    backgroundColor: '#1E40AF',
    borderRadius: BorderRadius.sm,
    paddingVertical: 10,
    alignItems: 'center',
    marginTop: 6,
  },
  saveButtonDisabled: {
    opacity: 0.6,
  },
  saveButtonText: {
    color: '#FFFFFF',
    fontSize: Typography.fontSize.xs,
    fontWeight: '700',
  },
  contactSubtitle: {
    fontSize: Typography.fontSize.xs,
    color: '#64748B',
    marginTop: 2,
    marginBottom: 12,
  },
  contactRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#F1F5F9',
  },
  contactIconCircle: {
    width: 34,
    height: 34,
    borderRadius: 17,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 10,
  },
  contactTextGroup: {
    flex: 1,
  },
  contactTitle: {
    fontSize: Typography.fontSize.xs,
    fontWeight: '600',
    color: '#1E293B',
  },
  contactDetail: {
    fontSize: 11,
    color: '#64748B',
    marginTop: 1,
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
    marginHorizontal: Spacing.md,
    marginTop: 20,
    backgroundColor: '#FEF2F2',
    borderColor: '#FCA5A5',
    borderWidth: 1,
    paddingVertical: 12,
    borderRadius: BorderRadius.md,
  },
  logoutText: {
    color: '#DC2626',
    fontSize: Typography.fontSize.xs,
    fontWeight: '700',
  },
  versionText: {
    textAlign: 'center',
    fontSize: 10,
    color: '#94A3B8',
    marginTop: 16,
  },
});

