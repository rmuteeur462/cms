import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  SafeAreaView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  Image,
  TextInput,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import * as LocationGeocoding from 'expo-location';
import {
  CitizenComplaintsApi,
  CitizenTypeItem,
  CitizenSubtypeItem,
  CitizenLocationItem,
  CitizenUCItem,
} from '../../api/complaints';
import { useAuth } from '../../store/AuthContext';
import { Colors, Typography, Spacing, BorderRadius } from '../../constants/theme';
import { Ionicons } from '@expo/vector-icons';

interface CitizenCreateComplaintScreenProps {
  navigation: any;
}

export const CitizenCreateComplaintScreen: React.FC<CitizenCreateComplaintScreenProps> = ({
  navigation,
}) => {
  const { user } = useAuth();

  // Reference Dropdown Data
  const [types, setTypes] = useState<CitizenTypeItem[]>([]);
  const [subtypes, setSubtypes] = useState<CitizenSubtypeItem[]>([]);
  const [locations, setLocations] = useState<CitizenLocationItem[]>([]);
  const [ucs, setUcs] = useState<CitizenUCItem[]>([]);

  // Selected State
  const [selectedTypeId, setSelectedTypeId] = useState<number | null>(null);
  const [selectedSubtypeId, setSelectedSubtypeId] = useState<number | null>(null);
  const [selectedLocationId, setSelectedLocationId] = useState<number | null>(null);
  const [selectedUcId, setSelectedUcId] = useState<number | null>(null);

  // Form Fields
  const [title, setTitle] = useState('');
  const [area, setArea] = useState('');
  const [address, setAddress] = useState(user?.address || '');
  const [complaintDetail, setComplaintDetail] = useState('');
  const [latitude, setLatitude] = useState<string | null>(null);
  const [longitude, setLongitude] = useState<string | null>(null);
  const [isGettingLocation, setIsGettingLocation] = useState(false);

  // Attachment
  const [selectedImage, setSelectedImage] = useState<ImagePicker.ImagePickerAsset | null>(null);

  // Status & Validation
  const [isLoadingMetadata, setIsLoadingMetadata] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Load Initial Metadata
  useEffect(() => {
    const loadInitialMetadata = async () => {
      try {
        const [typesData, locationsData] = await Promise.all([
          CitizenComplaintsApi.getComplaintTypes(),
          CitizenComplaintsApi.getLocations(),
        ]);
        setTypes(typesData);
        setLocations(locationsData);
      } catch (err) {
        console.warn('[CreateComplaint] Failed to load metadata:', err);
      } finally {
        setIsLoadingMetadata(false);
      }
    };
    loadInitialMetadata();
  }, []);

  // Cascading: Load Subtypes when Type changes
  useEffect(() => {
    if (!selectedTypeId) {
      setSubtypes([]);
      setSelectedSubtypeId(null);
      return;
    }
    const loadSubtypes = async () => {
      try {
        const data = await CitizenComplaintsApi.getSubtypes(selectedTypeId);
        setSubtypes(data);
        setSelectedSubtypeId(null);
      } catch (err) {
        console.warn('[CreateComplaint] Failed to load subtypes:', err);
      }
    };
    loadSubtypes();
  }, [selectedTypeId]);

  // Cascading: Load UCs when Location changes
  useEffect(() => {
    if (!selectedLocationId) {
      setUcs([]);
      setSelectedUcId(null);
      return;
    }
    const loadUcs = async () => {
      try {
        const data = await CitizenComplaintsApi.getUCs(selectedLocationId);
        setUcs(data);
        setSelectedUcId(null);
      } catch (err) {
        console.warn('[CreateComplaint] Failed to load UCs:', err);
      }
    };
    loadUcs();
  }, [selectedLocationId]);

  // GPS Location Handler
  const handleGetLocation = async () => {
    setIsGettingLocation(true);
    setErrorMessage(null);
    try {
      const { status } = await LocationGeocoding.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert(
          'Permission Denied',
          'Permission to access location was denied. You can manually enter the address.'
        );
        return;
      }

      const loc = await LocationGeocoding.getCurrentPositionAsync({
        accuracy: LocationGeocoding.Accuracy.Balanced,
      });

      const lat = loc.coords.latitude.toFixed(6);
      const lng = loc.coords.longitude.toFixed(6);
      setLatitude(lat);
      setLongitude(lng);

      // Attempt reverse geocoding to suggest address if empty
      try {
        const [geo] = await LocationGeocoding.reverseGeocodeAsync({
          latitude: loc.coords.latitude,
          longitude: loc.coords.longitude,
        });
        if (geo) {
          const suggested = [geo.street, geo.district || geo.subregion, geo.city]
            .filter(Boolean)
            .join(', ');
          if (suggested && !address) {
            setAddress(suggested);
          }
          if (geo.subregion && !area) {
            setArea(geo.subregion);
          }
        }
      } catch {
        // Fallback silently if reverse geocoding fails
      }
    } catch (err: any) {
      Alert.alert('Location Error', 'Unable to fetch current GPS coordinates. Please enter manually.');
    } finally {
      setIsGettingLocation(false);
    }
  };

  // Image Picker Options
  const handlePickImage = async () => {
    Alert.alert('Attach Complaint Photograph', 'Choose an option to attach evidence:', [
      {
        text: 'Take Photo with Camera',
        onPress: async () => {
          const { status } = await ImagePicker.requestCameraPermissionsAsync();
          if (status !== 'granted') {
            Alert.alert('Camera Permission', 'Camera permission is required to capture a photograph.');
            return;
          }
          const result = await ImagePicker.launchCameraAsync({
            allowsEditing: true,
            quality: 0.7,
          });
          if (!result.canceled && result.assets && result.assets.length > 0) {
            setSelectedImage(result.assets[0]);
          }
        },
      },
      {
        text: 'Choose from Gallery',
        onPress: async () => {
          const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
          if (status !== 'granted') {
            Alert.alert('Gallery Permission', 'Gallery access is required to choose a photograph.');
            return;
          }
          const result = await ImagePicker.launchImageLibraryAsync({
            allowsEditing: true,
            quality: 0.7,
          });
          if (!result.canceled && result.assets && result.assets.length > 0) {
            setSelectedImage(result.assets[0]);
          }
        },
      },
      { text: 'Cancel', style: 'cancel' },
    ]);
  };

  // Submission Handler
  const handleSubmit = async () => {
    setErrorMessage(null);

    // Validations
    if (!selectedTypeId) {
      setErrorMessage('Please select a complaint category.');
      return;
    }
    if (!selectedUcId) {
      setErrorMessage('Please select your Union Council (UC).');
      return;
    }
    if (!complaintDetail.trim() || complaintDetail.trim().length < 10) {
      setErrorMessage('Please provide a detailed description (at least 10 characters).');
      return;
    }

    setIsSubmitting(true);
    try {
      const formData = new FormData();
      formData.append('complaint_type_id', selectedTypeId.toString());
      if (selectedSubtypeId) {
        formData.append('subtype_id', selectedSubtypeId.toString());
      }
      formData.append('uc_id', selectedUcId.toString());
      formData.append('complaint_detail', complaintDetail.trim());

      if (title.trim()) {
        formData.append('title', title.trim());
      }
      if (area.trim()) {
        formData.append('area', area.trim());
      }
      if (address.trim()) {
        formData.append('address', address.trim());
      }
      if (latitude && longitude) {
        formData.append('latitude', latitude);
        formData.append('longitude', longitude);
      }

      if (selectedImage) {
        const uri = selectedImage.uri;
        const uriParts = uri.split('.');
        const fileType = uriParts[uriParts.length - 1] || 'jpg';

        formData.append('before_image', {
          uri: Platform.OS === 'ios' ? uri.replace('file://', '') : uri,
          name: `complaint_photo_${Date.now()}.${fileType}`,
          type: `image/${fileType === 'jpg' ? 'jpeg' : fileType}`,
        } as any);
      }

      const res = await CitizenComplaintsApi.submitComplaint(formData);

      if (res.success) {
        const ticketNo = res.data?.complaint_no || `CMS-${res.data?.id}`;
        Alert.alert(
          'Complaint Registered Successfully',
          `Your complaint has been submitted to WSSP Peshawar.\n\nTicket Reference Number:\n${ticketNo}\n\nYou can track the progress of your complaint anytime.`,
          [
            {
              text: 'Track Complaint',
              onPress: () => {
                navigation.navigate('Tracking', { complaintId: res.data?.id });
              },
            },
            {
              text: 'Done',
              onPress: () => navigation.navigate('Home'),
            },
          ]
        );
      } else {
        setErrorMessage(res.message || 'Failed to submit complaint. Please try again.');
      }
    } catch (err: any) {
      console.warn('[SubmitComplaint Error]:', err);
      let msg = 'Failed to submit complaint. Please check your network connection.';
      if (err.response?.data?.message) {
        msg = err.response.data.message;
      } else if (err.response?.data?.errors) {
        const errs = err.response.data.errors;
        const firstKey = Object.keys(errs)[0];
        msg = Array.isArray(errs[firstKey]) ? errs[firstKey][0] : errs[firstKey];
      }
      setErrorMessage(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoadingMetadata) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color={Colors.primary} />
        <Text style={styles.loadingText}>Loading WSSP categories & locations...</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        style={styles.keyboardView}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          {/* Header */}
          <View style={styles.headerBox}>
            <Text style={styles.headerTitle}>Register Complaint</Text>
            <Text style={styles.headerSubtitle}>
              Submit municipal issues directly to WSSP field operations team
            </Text>
          </View>

          <View style={styles.formCard}>
            {errorMessage && (
              <View style={styles.errorBox}>
                <Ionicons name="alert-circle" size={18} color={Colors.error} />
                <Text style={styles.errorText}>{errorMessage}</Text>
              </View>
            )}

            {/* 1. Category Selection */}
            <Text style={styles.sectionLabel}>1. Complaint Category *</Text>
            <View style={styles.chipGrid}>
              {types.map((type) => {
                const isSelected = selectedTypeId === type.id;
                return (
                  <TouchableOpacity
                    key={type.id}
                    style={[styles.categoryChip, isSelected && styles.categoryChipSelected]}
                    onPress={() => setSelectedTypeId(type.id)}
                    activeOpacity={0.8}
                  >
                    <Ionicons
                      name={isSelected ? 'checkmark-circle' : 'ellipse-outline'}
                      size={16}
                      color={isSelected ? '#1E40AF' : '#64748B'}
                    />
                    <Text style={[styles.categoryChipText, isSelected && styles.categoryChipTextSelected]}>
                      {type.type_name}
                    </Text>
                  </TouchableOpacity>
                );
              })}
            </View>

            {/* 2. Subcategory Selection */}
            {subtypes.length > 0 && (
              <>
                <Text style={styles.sectionLabel}>2. Subcategory (Optional)</Text>
                <View style={styles.chipGrid}>
                  {subtypes.map((sub) => {
                    const isSelected = selectedSubtypeId === sub.id;
                    return (
                      <TouchableOpacity
                        key={sub.id}
                        style={[styles.subChip, isSelected && styles.subChipSelected]}
                        onPress={() => setSelectedSubtypeId(isSelected ? null : sub.id)}
                        activeOpacity={0.8}
                      >
                        <Text style={[styles.subChipText, isSelected && styles.subChipTextSelected]}>
                          {sub.type_name}
                        </Text>
                      </TouchableOpacity>
                    );
                  })}
                </View>
              </>
            )}

            {/* 3. Operational Zone & UC Selection */}
            <Text style={styles.sectionLabel}>3. Operational Zone *</Text>
            <View style={styles.chipGrid}>
              {locations.map((loc) => {
                const isSelected = selectedLocationId === loc.id;
                return (
                  <TouchableOpacity
                    key={loc.id}
                    style={[styles.zoneChip, isSelected && styles.zoneChipSelected]}
                    onPress={() => setSelectedLocationId(loc.id)}
                    activeOpacity={0.8}
                  >
                    <Text style={[styles.zoneChipText, isSelected && styles.zoneChipTextSelected]}>
                      {loc.location_name}
                    </Text>
                  </TouchableOpacity>
                );
              })}
            </View>

            {selectedLocationId && ucs.length > 0 && (
              <>
                <Text style={styles.sectionLabel}>4. Union Council (UC) *</Text>
                <View style={styles.chipGrid}>
                  {ucs.map((uc) => {
                    const isSelected = selectedUcId === uc.id;
                    return (
                      <TouchableOpacity
                        key={uc.id}
                        style={[styles.ucChip, isSelected && styles.ucChipSelected]}
                        onPress={() => setSelectedUcId(uc.id)}
                        activeOpacity={0.8}
                      >
                        <Text style={[styles.ucChipText, isSelected && styles.ucChipTextSelected]}>
                          {uc.uc_name}
                        </Text>
                      </TouchableOpacity>
                    );
                  })}
                </View>
              </>
            )}

            {/* 5. Location / Address & GPS */}
            <Text style={styles.sectionLabel}>5. Location Details & Address</Text>
            <View style={styles.gpsRow}>
              <TouchableOpacity
                style={styles.gpsButton}
                onPress={handleGetLocation}
                disabled={isGettingLocation}
                activeOpacity={0.8}
              >
                {isGettingLocation ? (
                  <ActivityIndicator size="small" color="#1E40AF" />
                ) : (
                  <>
                    <Ionicons name="navigate" size={16} color="#1E40AF" />
                    <Text style={styles.gpsButtonText}>
                      {latitude ? 'Update GPS Location' : 'Use Current GPS Location'}
                    </Text>
                  </>
                )}
              </TouchableOpacity>
              {latitude && (
                <View style={styles.gpsBadge}>
                  <Ionicons name="checkmark-circle" size={14} color="#059669" />
                  <Text style={styles.gpsBadgeText}>GPS Tagged</Text>
                </View>
              )}
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Area / Mohallah / Neighborhood</Text>
              <TextInput
                style={styles.textInput}
                placeholder="e.g. Sector F1, Street 4, Gulbahar"
                value={area}
                onChangeText={setArea}
                placeholderTextColor={Colors.textMuted}
              />
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Complete Address / Landmarks</Text>
              <TextInput
                style={styles.textInput}
                placeholder="House #, Near Mosque / School / Water Tank"
                value={address}
                onChangeText={setAddress}
                placeholderTextColor={Colors.textMuted}
              />
            </View>

            {/* 6. Complaint Description */}
            <Text style={styles.sectionLabel}>6. Issue Description *</Text>
            <View style={styles.inputGroup}>
              <TextInput
                style={[styles.textInput, styles.textArea]}
                placeholder="Describe the issue clearly (e.g. Sewerage overflow since yesterday, garbage pile not collected for 3 days...)"
                value={complaintDetail}
                onChangeText={setComplaintDetail}
                multiline
                numberOfLines={4}
                textAlignVertical="top"
                placeholderTextColor={Colors.textMuted}
              />
            </View>

            {/* 7. Photo Evidence */}
            <Text style={styles.sectionLabel}>7. Photo Evidence (Optional)</Text>
            {selectedImage ? (
              <View style={styles.imagePreviewWrap}>
                <Image source={{ uri: selectedImage.uri }} style={styles.imagePreview} />
                <TouchableOpacity
                  style={styles.removeImageButton}
                  onPress={() => setSelectedImage(null)}
                >
                  <Ionicons name="close" size={16} color="#FFFFFF" />
                </TouchableOpacity>
              </View>
            ) : (
              <TouchableOpacity
                style={styles.attachButton}
                onPress={handlePickImage}
                activeOpacity={0.8}
              >
                <Ionicons name="camera-outline" size={24} color="#1E40AF" />
                <Text style={styles.attachButtonText}>Attach Photo Evidence</Text>
                <Text style={styles.attachHint}>Camera or Gallery (JPG, PNG)</Text>
              </TouchableOpacity>
            )}

            {/* Submit Action */}
            <TouchableOpacity
              style={[styles.submitButton, isSubmitting && styles.submitButtonDisabled]}
              onPress={handleSubmit}
              disabled={isSubmitting}
              activeOpacity={0.85}
            >
              {isSubmitting ? (
                <ActivityIndicator color="#FFFFFF" size="small" />
              ) : (
                <>
                  <Text style={styles.submitButtonText}>Submit Complaint</Text>
                  <Ionicons name="send" size={16} color="#FFFFFF" style={{ marginLeft: 8 }} />
                </>
              )}
            </TouchableOpacity>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#0F2744',
  },
  keyboardView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    backgroundColor: '#F8FAFC',
    paddingBottom: Spacing.xxl + 30,
  },
  centerContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 30,
    backgroundColor: '#F8FAFC',
  },
  loadingText: {
    marginTop: 12,
    fontSize: Typography.fontSize.sm,
    color: '#64748B',
  },
  headerBox: {
    backgroundColor: '#0F2744',
    paddingHorizontal: Spacing.lg,
    paddingTop: 16,
    paddingBottom: 22,
  },
  headerTitle: {
    fontSize: Typography.fontSize.xl,
    fontWeight: '800',
    color: '#FFFFFF',
  },
  headerSubtitle: {
    fontSize: Typography.fontSize.xs,
    color: '#93C5FD',
    marginTop: 2,
    lineHeight: 18,
  },
  formCard: {
    backgroundColor: '#FFFFFF',
    marginHorizontal: Spacing.md,
    marginTop: -10,
    borderRadius: BorderRadius.md,
    padding: Spacing.lg,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 6,
    elevation: 2,
  },
  errorBox: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FEF2F2',
    borderColor: '#FCA5A5',
    borderWidth: 1,
    borderRadius: BorderRadius.md,
    padding: 10,
    marginBottom: 14,
    gap: 8,
  },
  errorText: {
    flex: 1,
    color: Colors.error,
    fontSize: Typography.fontSize.xs,
    fontWeight: '600',
  },
  sectionLabel: {
    fontSize: Typography.fontSize.sm,
    fontWeight: '700',
    color: '#1E293B',
    marginTop: 14,
    marginBottom: 8,
  },
  chipGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  categoryChip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: BorderRadius.md,
    backgroundColor: '#F1F5F9',
    borderWidth: 1,
    borderColor: '#CBD5E1',
  },
  categoryChipSelected: {
    backgroundColor: '#EFF6FF',
    borderColor: '#1E40AF',
  },
  categoryChipText: {
    fontSize: Typography.fontSize.xs,
    color: '#475569',
    fontWeight: '600',
  },
  categoryChipTextSelected: {
    color: '#1E40AF',
    fontWeight: '700',
  },
  subChip: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  subChipSelected: {
    backgroundColor: '#1E40AF',
    borderColor: '#1E40AF',
  },
  subChipText: {
    fontSize: 11,
    color: '#475569',
    fontWeight: '500',
  },
  subChipTextSelected: {
    color: '#FFFFFF',
    fontWeight: '700',
  },
  zoneChip: {
    paddingHorizontal: 14,
    paddingVertical: 7,
    borderRadius: BorderRadius.md,
    backgroundColor: '#F1F5F9',
    borderWidth: 1,
    borderColor: '#CBD5E1',
  },
  zoneChipSelected: {
    backgroundColor: '#1E40AF',
    borderColor: '#1E40AF',
  },
  zoneChipText: {
    fontSize: Typography.fontSize.xs,
    color: '#475569',
    fontWeight: '600',
  },
  zoneChipTextSelected: {
    color: '#FFFFFF',
    fontWeight: '700',
  },
  ucChip: {
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 14,
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  ucChipSelected: {
    backgroundColor: '#2563EB',
    borderColor: '#2563EB',
  },
  ucChipText: {
    fontSize: 11,
    color: '#475569',
  },
  ucChipTextSelected: {
    color: '#FFFFFF',
    fontWeight: '700',
  },
  gpsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    marginBottom: 10,
  },
  gpsButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    backgroundColor: '#EFF6FF',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: BorderRadius.md,
    borderWidth: 1,
    borderColor: '#BFDBFE',
  },
  gpsButtonText: {
    fontSize: Typography.fontSize.xs,
    fontWeight: '700',
    color: '#1E40AF',
  },
  gpsBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    backgroundColor: '#ECFDF5',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 10,
  },
  gpsBadgeText: {
    fontSize: 11,
    fontWeight: '700',
    color: '#059669',
  },
  inputGroup: {
    marginBottom: 10,
  },
  inputLabel: {
    fontSize: Typography.fontSize.xs,
    fontWeight: '600',
    color: '#475569',
    marginBottom: 4,
  },
  textInput: {
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#CBD5E1',
    borderRadius: BorderRadius.md,
    paddingHorizontal: 12,
    paddingVertical: 9,
    fontSize: Typography.fontSize.sm,
    color: '#1E293B',
  },
  textArea: {
    minHeight: 85,
    paddingTop: 10,
  },
  attachButton: {
    borderWidth: 2,
    borderColor: '#BFDBFE',
    borderStyle: 'dashed',
    borderRadius: BorderRadius.md,
    backgroundColor: '#EFF6FF',
    padding: 16,
    alignItems: 'center',
    justifyContent: 'center',
  },
  attachButtonText: {
    fontSize: Typography.fontSize.sm,
    fontWeight: '700',
    color: '#1E40AF',
    marginTop: 4,
  },
  attachHint: {
    fontSize: 11,
    color: '#64748B',
    marginTop: 2,
  },
  imagePreviewWrap: {
    position: 'relative',
    alignSelf: 'flex-start',
  },
  imagePreview: {
    width: 110,
    height: 110,
    borderRadius: BorderRadius.md,
  },
  removeImageButton: {
    position: 'absolute',
    top: -6,
    right: -6,
    backgroundColor: '#EF4444',
    width: 22,
    height: 22,
    borderRadius: 11,
    alignItems: 'center',
    justifyContent: 'center',
  },
  submitButton: {
    backgroundColor: '#1E40AF',
    borderRadius: BorderRadius.md,
    paddingVertical: 14,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 18,
    shadowColor: '#1E40AF',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 6,
    elevation: 3,
  },
  submitButtonDisabled: {
    opacity: 0.6,
  },
  submitButtonText: {
    color: '#FFFFFF',
    fontSize: Typography.fontSize.md,
    fontWeight: '700',
  },
});

