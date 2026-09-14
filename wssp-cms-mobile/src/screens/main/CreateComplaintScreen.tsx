import React, { useState, useEffect, useMemo } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  Image,
  Platform,
  Modal,
  TextInput,
  KeyboardAvoidingView,
} from 'react-native';
import { Colors } from '../../constants/theme';
import {
  ComplaintsApi,
  ComplaintOptionsResponse,
  LocationOption,
  UCOption,
  SourceOption,
  TypeOption,
  SubtypeOption,
} from '../../api/complaints';
import { useAuth } from '../../store/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import * as Location from 'expo-location';

// Format current date as mm/dd/yyyy
const formatTodayDate = (): string => {
  const d = new Date();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  const yyyy = d.getFullYear();
  return `${mm}/${dd}/${yyyy}`;
};

// Generic Select Option
interface SelectOptionItem {
  value: string | number;
  label: string;
}

// Modal Selector Component (renders like an HTML <select> dropdown)
const HtmlSelectField: React.FC<{
  label: string;
  required?: boolean;
  value: string | number | null | undefined;
  options: SelectOptionItem[];
  placeholder?: string;
  onSelect: (val: any) => void;
  disabled?: boolean;
}> = ({ label, required, value, options, placeholder = '---------', onSelect, disabled }) => {
  const [modalVisible, setModalVisible] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const selectedOption = options.find((o) => String(o.value) === String(value));
  const displayText = selectedOption ? selectedOption.label : placeholder;

  const filteredOptions = useMemo(() => {
    if (!searchQuery.trim()) return options;
    const q = searchQuery.toLowerCase();
    return options.filter((o) => o.label.toLowerCase().includes(q));
  }, [options, searchQuery]);

  return (
    <View style={formStyles.formGroup}>
      <Text style={formStyles.label}>
        {label}
        {required && <Text style={formStyles.requiredStar}> *</Text>}
      </Text>
      <TouchableOpacity
        style={[formStyles.selectBox, disabled && formStyles.inputDisabled]}
        onPress={() => {
          if (!disabled) {
            setSearchQuery('');
            setModalVisible(true);
          }
        }}
        activeOpacity={disabled ? 1 : 0.7}
      >
        <Text
          style={[
            formStyles.selectText,
            !selectedOption && formStyles.placeholderText,
            disabled && { color: '#6C757D' },
          ]}
          numberOfLines={1}
        >
          {displayText}
        </Text>
        <Ionicons name="chevron-down" size={14} color="#6C757D" style={{ marginLeft: 4 }} />
      </TouchableOpacity>

      {/* Select Options Modal */}
      <Modal
        visible={modalVisible}
        transparent
        animationType="fade"
        onRequestClose={() => setModalVisible(false)}
      >
        <TouchableOpacity
          style={formStyles.selectModalBackdrop}
          activeOpacity={1}
          onPress={() => setModalVisible(false)}
        >
          <View
            style={formStyles.selectModalCard}
            onStartShouldSetResponder={() => true}
          >
            <View style={formStyles.selectModalHeader}>
              <Text style={formStyles.selectModalTitle}>{label.replace(':', '')}</Text>
              <TouchableOpacity
                onPress={() => setModalVisible(false)}
                style={formStyles.selectModalCloseBtn}
              >
                <Ionicons name="close" size={20} color="#495057" />
              </TouchableOpacity>
            </View>

            {options.length > 5 && (
              <View style={formStyles.searchContainer}>
                <Ionicons name="search" size={16} color="#6C757D" style={{ marginRight: 6 }} />
                <TextInput
                  style={formStyles.searchInput}
                  placeholder="Search options..."
                  placeholderTextColor="#ADB5BD"
                  value={searchQuery}
                  onChangeText={setSearchQuery}
                  autoCapitalize="none"
                />
                {searchQuery.length > 0 && (
                  <TouchableOpacity onPress={() => setSearchQuery('')}>
                    <Ionicons name="close-circle" size={16} color="#ADB5BD" />
                  </TouchableOpacity>
                )}
              </View>
            )}

            <ScrollView style={formStyles.selectListScroll} keyboardShouldPersistTaps="handled">
              {/* Option to clear selection */}
              <TouchableOpacity
                style={[
                  formStyles.selectListItem,
                  value === null || value === '' ? formStyles.selectListItemActive : null,
                ]}
                onPress={() => {
                  onSelect(null);
                  setModalVisible(false);
                }}
              >
                <Text style={formStyles.selectListItemText}>---------</Text>
                {(value === null || value === '') && (
                  <Ionicons name="checkmark" size={16} color={Colors.primary} />
                )}
              </TouchableOpacity>

              {filteredOptions.map((opt) => {
                const isSelected = String(opt.value) === String(value);
                return (
                  <TouchableOpacity
                    key={String(opt.value)}
                    style={[
                      formStyles.selectListItem,
                      isSelected && formStyles.selectListItemActive,
                    ]}
                    onPress={() => {
                      onSelect(opt.value);
                      setModalVisible(false);
                    }}
                  >
                    <Text
                      style={[
                        formStyles.selectListItemText,
                        isSelected && formStyles.selectListItemTextActive,
                      ]}
                    >
                      {opt.label}
                    </Text>
                    {isSelected && (
                      <Ionicons name="checkmark" size={16} color={Colors.primary} />
                    )}
                  </TouchableOpacity>
                );
              })}

              {filteredOptions.length === 0 && (
                <View style={{ padding: 16, alignItems: 'center' }}>
                  <Text style={{ color: '#6C757D', fontSize: 13 }}>No options found</Text>
                </View>
              )}
            </ScrollView>

            <TouchableOpacity
              style={formStyles.selectModalCancelBtn}
              onPress={() => setModalVisible(false)}
            >
              <Text style={formStyles.selectModalCancelText}>Cancel</Text>
            </TouchableOpacity>
          </View>
        </TouchableOpacity>
      </Modal>
    </View>
  );
};

// HTML-like Text Input Component
const HtmlInputField: React.FC<{
  label: string;
  required?: boolean;
  value: string;
  placeholder?: string;
  onChangeText: (text: string) => void;
  keyboardType?: any;
  editable?: boolean;
  multiline?: boolean;
  numberOfLines?: number;
  rightElement?: React.ReactNode;
}> = ({
  label,
  required,
  value,
  placeholder,
  onChangeText,
  keyboardType = 'default',
  editable = true,
  multiline = false,
  numberOfLines = 1,
  rightElement,
}) => {
  const [isFocused, setIsFocused] = useState(false);

  return (
    <View style={formStyles.formGroup}>
      <Text style={formStyles.label}>
        {label}
        {required && <Text style={formStyles.requiredStar}> *</Text>}
      </Text>
      <View
        style={[
          formStyles.inputWrapper,
          multiline && { height: numberOfLines * 28 + 20, alignItems: 'flex-start' },
          !editable && formStyles.inputDisabled,
          isFocused && formStyles.inputFocused,
        ]}
      >
        <TextInput
          style={[
            formStyles.inputControl,
            multiline && { textAlignVertical: 'top', height: '100%', paddingTop: 6 },
            !editable && { color: '#495057' },
          ]}
          placeholder={placeholder}
          placeholderTextColor="#ADB5BD"
          value={value}
          onChangeText={onChangeText}
          keyboardType={keyboardType}
          editable={editable}
          multiline={multiline}
          numberOfLines={numberOfLines}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
        />
        {rightElement}
      </View>
    </View>
  );
};

interface CreateComplaintScreenProps {
  navigation?: any;
  onSuccessNavigate?: () => void;
}

export const CreateComplaintScreen: React.FC<CreateComplaintScreenProps> = ({
  navigation,
  onSuccessNavigate,
}) => {
  const { user } = useAuth();

  const [loadingOptions, setLoadingOptions] = useState<boolean>(true);
  const [options, setOptions] = useState<ComplaintOptionsResponse | null>(null);

  // Applicant Information fields
  const [firstName, setFirstName] = useState<string>('');
  const [lastName, setLastName] = useState<string>('');
  const [cnic, setCnic] = useState<string>('');
  const [cellNumber, setCellNumber] = useState<string>('');
  const [phoneNumber, setPhoneNumber] = useState<string>('');
  const [billNumber, setBillNumber] = useState<string>('');
  const [gender, setGender] = useState<string>('male');
  const [consumerType, setConsumerType] = useState<string>('domestic');
  const [area, setArea] = useState<string>('');
  const [tehsil, setTehsil] = useState<string>('');
  const [address, setAddress] = useState<string>('');

  // Complaint Details fields
  const [selectedLocationId, setSelectedLocationId] = useState<number | null>(null);
  const [selectedUcId, setSelectedUcId] = useState<number | null>(null);
  const [selectedSourceId, setSelectedSourceId] = useState<number | null>(null);
  const [selectedTypeId, setSelectedTypeId] = useState<number | null>(null);
  const [selectedSubtypeId, setSelectedSubtypeId] = useState<number | null>(null);
  const [title, setTitle] = useState<string>('');
  const [complaintCategoryType, setComplaintCategoryType] = useState<string>('');
  const [complaintDetail, setComplaintDetail] = useState<string>('');
  const [complaintDate, setComplaintDate] = useState<string>(formatTodayDate());
  const [statusText, setStatusText] = useState<string>('Pending');

  // Before Image
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [imageFileName, setImageFileName] = useState<string>('');

  // GPS (optional extra)
  const [gpsCoords, setGpsCoords] = useState<{ latitude: number; longitude: number } | null>(null);
  const [isLocating, setIsLocating] = useState<boolean>(false);

  // State
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [registeredComplaint, setRegisteredComplaint] = useState<any | null>(null);
  const [successModalVisible, setSuccessModalVisible] = useState<boolean>(false);

  useEffect(() => {
    loadMetadata();
  }, []);

  const loadMetadata = async () => {
    setLoadingOptions(true);
    try {
      const data = await ComplaintsApi.getComplaintOptions();
      setOptions(data);
      // Pre-select first source if available
      if (data.sources && data.sources.length > 0) {
        setSelectedSourceId(data.sources[0].id);
      }
    } catch (err: any) {
      Alert.alert('Connection Error', 'Could not load form options. Check server connection.');
    } finally {
      setLoadingOptions(false);
    }
  };

  // Filter UCs based on selected location
  const filteredUcs: UCOption[] = useMemo(() => {
    if (!options?.ucs) return [];
    if (!selectedLocationId) return options.ucs;
    return options.ucs.filter((uc) => uc.location_id === selectedLocationId);
  }, [options, selectedLocationId]);

  // Filter Subtypes based on selected category type
  const filteredSubtypes: SubtypeOption[] = useMemo(() => {
    if (!options?.subtypes) return [];
    if (!selectedTypeId) return options.subtypes;
    return options.subtypes.filter((st) => st.type_id === selectedTypeId);
  }, [options, selectedTypeId]);

  // Image Selection Handlers
  const handleChooseImage = () => {
    Alert.alert(
      'Attach Before Image',
      'Select source for complaint photo:',
      [
        {
          text: 'Camera',
          onPress: async () => {
            try {
              const { status } = await ImagePicker.requestCameraPermissionsAsync();
              if (status !== 'granted') {
                Alert.alert('Permission Needed', 'Camera permission is required.');
                return;
              }
              const result = await ImagePicker.launchCameraAsync({
                allowsEditing: true,
                aspect: [4, 3],
                quality: 0.8,
              });
              if (!result.canceled && result.assets?.[0]?.uri) {
                setImageUri(result.assets[0].uri);
                setImageFileName(`camera_${Date.now()}.jpg`);
              }
            } catch (err: any) {
              Alert.alert('Error', err.message);
            }
          },
        },
        {
          text: 'Photo Gallery / Files',
          onPress: async () => {
            try {
              const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
              if (status !== 'granted') {
                Alert.alert('Permission Needed', 'Photo gallery permission is required.');
                return;
              }
              const result = await ImagePicker.launchImageLibraryAsync({
                mediaTypes: ['images'],
                allowsEditing: true,
                aspect: [4, 3],
                quality: 0.8,
              });
              if (!result.canceled && result.assets?.[0]?.uri) {
                setImageUri(result.assets[0].uri);
                const name = result.assets[0].fileName || `photo_${Date.now()}.jpg`;
                setImageFileName(name);
              }
            } catch (err: any) {
              Alert.alert('Error', err.message);
            }
          },
        },
        { text: 'Cancel', style: 'cancel' },
      ],
      { cancelable: true }
    );
  };

  const handleCaptureGps = async () => {
    setIsLocating(true);
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission Needed', 'Location permission is required.');
        return;
      }
      const loc = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Balanced });
      setGpsCoords({ latitude: loc.coords.latitude, longitude: loc.coords.longitude });
    } catch (err: any) {
      Alert.alert('GPS Error', 'Could not get location. Make sure GPS is enabled.');
    } finally {
      setIsLocating(false);
    }
  };

  const validateForm = (): boolean => {
    if (!firstName.trim()) {
      setValidationError('First Name is required.');
      return false;
    }
    if (!cellNumber.trim()) {
      setValidationError('Cell# is required.');
      return false;
    }
    if (cellNumber.trim().replace(/\D/g, '').length < 10) {
      setValidationError('Please enter a valid mobile number (e.g. 03001234567).');
      return false;
    }
    if (!selectedLocationId) {
      setValidationError('Location (Zone) is required.');
      return false;
    }
    if (!selectedTypeId) {
      setValidationError('Category is required.');
      return false;
    }
    if (!complaintDetail.trim()) {
      setValidationError('Complaint Detail is required.');
      return false;
    }
    setValidationError(null);
    return true;
  };

  const handleResetForm = () => {
    setFirstName('');
    setLastName('');
    setCnic('');
    setCellNumber('');
    setPhoneNumber('');
    setBillNumber('');
    setGender('male');
    setConsumerType('domestic');
    setArea('');
    setTehsil('');
    setAddress('');
    setSelectedLocationId(null);
    setSelectedUcId(null);
    setSelectedSourceId(options?.sources?.[0]?.id || null);
    setSelectedTypeId(null);
    setSelectedSubtypeId(null);
    setTitle('');
    setComplaintCategoryType('');
    setComplaintDetail('');
    setImageUri(null);
    setImageFileName('');
    setGpsCoords(null);
    setValidationError(null);
    setRegisteredComplaint(null);
    setSuccessModalVisible(false);
  };

  const handleClose = () => {
    Alert.alert('Close Form', 'Are you sure you want to close and clear the form?', [
      { text: 'No', style: 'cancel' },
      {
        text: 'Yes, Close',
        style: 'destructive',
        onPress: () => {
          handleResetForm();
          if (navigation?.goBack) navigation.goBack();
          else if (navigation?.navigate) navigation.navigate('Home');
        },
      },
    ]);
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;
    setIsSubmitting(true);
    setValidationError(null);

    try {
      const formData = new FormData();
      formData.append('first_name', firstName.trim());
      formData.append('last_name', lastName.trim());
      formData.append('cnic', cnic.trim());
      formData.append('cell_number', cellNumber.trim());
      formData.append('phone_number', phoneNumber.trim());
      formData.append('bill_number', billNumber.trim());
      formData.append('gender', gender);
      formData.append('consumer_type', consumerType);
      formData.append('area', area.trim());
      formData.append('tehsil', tehsil.trim() || 'Peshawar');
      formData.append('address', address.trim());

      if (selectedLocationId) formData.append('location_id', selectedLocationId.toString());
      if (selectedUcId) formData.append('uc_id', selectedUcId.toString());
      if (selectedSourceId) formData.append('complaint_source_id', selectedSourceId.toString());
      if (selectedTypeId) formData.append('complaint_type_id', selectedTypeId.toString());
      if (selectedSubtypeId) formData.append('subtype_id', selectedSubtypeId.toString());
      formData.append('title', title.trim() || 'Complaint via Mobile App');
      if (complaintCategoryType) formData.append('type', complaintCategoryType);
      formData.append('complaint_detail', complaintDetail.trim());

      if (gpsCoords) {
        formData.append('latitude', gpsCoords.latitude.toFixed(6));
        formData.append('longitude', gpsCoords.longitude.toFixed(6));
      }

      if (imageUri) {
        if (Platform.OS === 'web') {
          const res = await fetch(imageUri);
          const blob = await res.blob();
          formData.append('before_image', blob, imageFileName || `before_${Date.now()}.jpg`);
        } else {
          const uriParts = imageUri.split('.');
          const fileType = uriParts[uriParts.length - 1] || 'jpg';
          formData.append('before_image', {
            uri: imageUri,
            name: imageFileName || `before_${Date.now()}.${fileType}`,
            type: `image/${fileType === 'png' ? 'png' : 'jpeg'}`,
          } as any);
        }
      }

      const res = await ComplaintsApi.createComplaint(formData);
      if (res.success && res.complaint) {
        setRegisteredComplaint(res.complaint);
        setSuccessModalVisible(true);
      } else {
        Alert.alert('Submission Failed', res.message || 'Could not register complaint.');
      }
    } catch (err: any) {
      const detail =
        err.response?.data?.detail ||
        (err.response?.data?.errors && Object.values(err.response.data.errors).join('\n')) ||
        err.message ||
        'Something went wrong. Please check your connection.';
      setValidationError(detail);
      Alert.alert('Validation Error', detail);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Prepare select options lists
  const locationOptions: SelectOptionItem[] = (options?.locations || []).map((l) => ({
    value: l.id,
    label: l.name,
  }));

  const ucOptions: SelectOptionItem[] = filteredUcs.map((u) => ({
    value: u.id,
    label: u.name,
  }));

  const sourceOptions: SelectOptionItem[] = (options?.sources || []).map((s) => ({
    value: s.id,
    label: s.name,
  }));

  const typeOptions: SelectOptionItem[] = (options?.types || []).map((t) => ({
    value: t.id,
    label: t.name,
  }));

  const subtypeOptions: SelectOptionItem[] = filteredSubtypes.map((st) => ({
    value: st.id,
    label: st.name,
  }));

  const genderOptions: SelectOptionItem[] = [
    { value: 'male', label: 'Male' },
    { value: 'female', label: 'Female' },
  ];

  const consumerTypeOptions: SelectOptionItem[] = [
    { value: 'domestic', label: 'Domestic' },
    { value: 'commercial', label: 'Commercial' },
    { value: 'industrial', label: 'Industrial' },
  ];

  const complaintTypeCategoryOptions: SelectOptionItem[] = [
    { value: 'Short Term', label: 'Short Term' },
    { value: 'Long Term', label: 'Long Term' },
  ];

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      style={formStyles.screenContainer}
    >
      <ScrollView
        style={formStyles.scrollArea}
        contentContainerStyle={formStyles.scrollContent}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={true}
      >
        {/* Main Modal Card Container */}
        <View style={formStyles.modalCard}>
          {/* Modal Header */}
          <View style={formStyles.modalHeader}>
            <Text style={formStyles.modalTitle}>Add New Complaint</Text>
            <TouchableOpacity
              onPress={handleClose}
              style={formStyles.modalCloseButton}
              accessibilityLabel="Close form"
            >
              <Ionicons name="close" size={22} color="#6C757D" />
            </TouchableOpacity>
          </View>

          {/* Error Banner */}
          {validationError && (
            <View style={formStyles.errorBanner}>
              <Ionicons name="alert-circle" size={18} color="#721C24" style={{ marginRight: 8 }} />
              <Text style={formStyles.errorBannerText}>{validationError}</Text>
            </View>
          )}

          {loadingOptions ? (
            <View style={formStyles.loadingBox}>
              <ActivityIndicator size="large" color={Colors.primary} />
              <Text style={formStyles.loadingText}>Loading form fields...</Text>
            </View>
          ) : (
            <View style={formStyles.modalBody}>
              {/* ═══════════════════════════════════════════════ */}
              {/* SECTION 1: APPLICANT INFORMATION               */}
              {/* ═══════════════════════════════════════════════ */}
              <View style={formStyles.sectionHeaderContainer}>
                <View style={formStyles.sectionAccentBar} />
                <Text style={formStyles.sectionHeading}>Applicant Information</Text>
              </View>

              {/* Row 1: First Name & Last Name */}
              <View style={formStyles.formRow}>
                <View style={formStyles.colHalf}>
                  <HtmlInputField
                    label="First Name:"
                    required
                    placeholder="e.g. Ali"
                    value={firstName}
                    onChangeText={setFirstName}
                  />
                </View>
                <View style={formStyles.colHalf}>
                  <HtmlInputField
                    label="Last Name:"
                    placeholder="e.g. Khan"
                    value={lastName}
                    onChangeText={setLastName}
                  />
                </View>
              </View>

              {/* Row 2: CNIC & Cell# */}
              <View style={formStyles.formRow}>
                <View style={formStyles.colHalf}>
                  <HtmlInputField
                    label="CNIC:"
                    placeholder="17301-0000000-0"
                    value={cnic}
                    onChangeText={setCnic}
                    keyboardType="numeric"
                  />
                </View>
                <View style={formStyles.colHalf}>
                  <HtmlInputField
                    label="Cell#:"
                    required
                    placeholder="03001234567"
                    value={cellNumber}
                    onChangeText={setCellNumber}
                    keyboardType="phone-pad"
                  />
                </View>
              </View>

              {/* Row 3: Phone# & Bill# */}
              <View style={formStyles.formRow}>
                <View style={formStyles.colHalf}>
                  <HtmlInputField
                    label="Phone#:"
                    placeholder="091-1234567"
                    value={phoneNumber}
                    onChangeText={setPhoneNumber}
                    keyboardType="phone-pad"
                  />
                </View>
                <View style={formStyles.colHalf}>
                  <HtmlInputField
                    label="Bill#:"
                    placeholder="e.g. WSSP-12345"
                    value={billNumber}
                    onChangeText={setBillNumber}
                  />
                </View>
              </View>

              {/* Row 4: Gender & Consumer Type */}
              <View style={formStyles.formRow}>
                <View style={formStyles.colHalf}>
                  <HtmlSelectField
                    label="Gender:"
                    value={gender}
                    options={genderOptions}
                    onSelect={(val) => setGender(val || 'male')}
                  />
                </View>
                <View style={formStyles.colHalf}>
                  <HtmlSelectField
                    label="Consumer Type:"
                    value={consumerType}
                    options={consumerTypeOptions}
                    onSelect={(val) => setConsumerType(val || 'domestic')}
                  />
                </View>
              </View>

              {/* Row 5: Area & Tehsil */}
              <View style={formStyles.formRow}>
                <View style={formStyles.colHalf}>
                  <HtmlInputField
                    label="Area:"
                    placeholder="e.g. Hayatabad"
                    value={area}
                    onChangeText={setArea}
                  />
                </View>
                <View style={formStyles.colHalf}>
                  <HtmlInputField
                    label="Tehsil:"
                    placeholder="e.g. Peshawar"
                    value={tehsil}
                    onChangeText={setTehsil}
                  />
                </View>
              </View>

              {/* Row 6: Address (full width) */}
              <View style={formStyles.formRowSingle}>
                <HtmlInputField
                  label="Address:"
                  placeholder="Street, House/Shop number, Landmark or Mohallah"
                  value={address}
                  onChangeText={setAddress}
                  multiline
                  numberOfLines={2}
                />
              </View>

              {/* Divider between sections */}
              <View style={formStyles.sectionDivider} />

              {/* ═══════════════════════════════════════════════ */}
              {/* SECTION 2: COMPLAINT DETAILS                   */}
              {/* ═══════════════════════════════════════════════ */}
              <View style={formStyles.sectionHeaderContainer}>
                <View style={formStyles.sectionAccentBar} />
                <Text style={formStyles.sectionHeading}>Complaint Details</Text>
              </View>

              {/* Row 1: Location & UC */}
              <View style={formStyles.formRow}>
                <View style={formStyles.colHalf}>
                  <HtmlSelectField
                    label="Location:"
                    required
                    value={selectedLocationId}
                    options={locationOptions}
                    placeholder="---------"
                    onSelect={(val) => {
                      setSelectedLocationId(val);
                      setSelectedUcId(null);
                    }}
                  />
                </View>
                <View style={formStyles.colHalf}>
                  <HtmlSelectField
                    label="UC:"
                    value={selectedUcId}
                    options={ucOptions}
                    placeholder="---------"
                    onSelect={setSelectedUcId}
                    disabled={!selectedLocationId}
                  />
                </View>
              </View>

              {/* Row 2: Complaint Source (full width) */}
              <View style={formStyles.formRowSingle}>
                <HtmlSelectField
                  label="Complaint Source:"
                  value={selectedSourceId}
                  options={sourceOptions}
                  placeholder="---------"
                  onSelect={setSelectedSourceId}
                />
              </View>

              {/* Row 3: Category & Sub Category */}
              <View style={formStyles.formRow}>
                <View style={formStyles.colHalf}>
                  <HtmlSelectField
                    label="Category:"
                    required
                    value={selectedTypeId}
                    options={typeOptions}
                    placeholder="---------"
                    onSelect={(val) => {
                      setSelectedTypeId(val);
                      setSelectedSubtypeId(null);
                    }}
                  />
                </View>
                <View style={formStyles.colHalf}>
                  <HtmlSelectField
                    label="Sub Category:"
                    value={selectedSubtypeId}
                    options={subtypeOptions}
                    placeholder="---------"
                    onSelect={setSelectedSubtypeId}
                    disabled={!selectedTypeId}
                  />
                </View>
              </View>

              {/* Row 4: Complaint Title */}
              <View style={formStyles.formRowSingle}>
                <HtmlInputField
                  label="Complaint Title:"
                  placeholder="e.g. Water Contamination, Pipeline Leakage"
                  value={title}
                  onChangeText={setTitle}
                />
              </View>

              {/* Row 5: Complaint Category (Type) */}
              <View style={formStyles.formRowSingle}>
                <HtmlSelectField
                  label="Complaint Category (Type):"
                  value={complaintCategoryType}
                  options={complaintTypeCategoryOptions}
                  placeholder="---------"
                  onSelect={setComplaintCategoryType}
                />
              </View>

              {/* Row 6: Complaint Detail */}
              <View style={formStyles.formRowSingle}>
                <HtmlInputField
                  label="Complaint Detail:"
                  required
                  placeholder="Provide complete details and location landmark of the issue..."
                  value={complaintDetail}
                  onChangeText={setComplaintDetail}
                  multiline
                  numberOfLines={4}
                />
              </View>

              {/* Row 7: Before Image (HTML File Input Style) */}
              <View style={formStyles.formRowSingle}>
                <Text style={formStyles.label}>Before Image:</Text>
                <View style={formStyles.fileInputRow}>
                  <TouchableOpacity
                    style={formStyles.fileChooseBtn}
                    onPress={handleChooseImage}
                    activeOpacity={0.8}
                  >
                    <Ionicons name="folder-open-outline" size={14} color="#333" style={{ marginRight: 5 }} />
                    <Text style={formStyles.fileChooseBtnText}>Choose File</Text>
                  </TouchableOpacity>

                  <Text style={formStyles.fileStatusText} numberOfLines={1}>
                    {imageFileName || 'No file chosen'}
                  </Text>
                </View>

                {/* Selected Image Preview Thumbnail */}
                {imageUri && (
                  <View style={formStyles.imageThumbnailCard}>
                    <Image source={{ uri: imageUri }} style={formStyles.imageThumbnail} />
                    <View style={formStyles.imageThumbnailMeta}>
                      <Text style={formStyles.imageThumbnailName} numberOfLines={1}>
                        {imageFileName || 'Selected photo'}
                      </Text>
                      <TouchableOpacity
                        onPress={() => {
                          setImageUri(null);
                          setImageFileName('');
                        }}
                        style={formStyles.imageRemoveBtn}
                      >
                        <Ionicons name="trash-outline" size={14} color="#DC3545" />
                        <Text style={formStyles.imageRemoveText}>Remove</Text>
                      </TouchableOpacity>
                    </View>
                  </View>
                )}
              </View>

              {/* Row 8: Date */}
              <View style={formStyles.formRowSingle}>
                <HtmlInputField
                  label="Date:"
                  value={complaintDate}
                  onChangeText={setComplaintDate}
                  placeholder="mm/dd/yyyy"
                  rightElement={
                    <Ionicons name="calendar-outline" size={18} color="#6C757D" style={{ marginLeft: 6 }} />
                  }
                />
              </View>

              {/* Row 9: Status (Readonly) */}
              <View style={formStyles.formRowSingle}>
                <HtmlInputField
                  label="Status:"
                  value={statusText}
                  onChangeText={setStatusText}
                  editable={false}
                />
              </View>

              {/* Optional GPS capture bar */}
              <View style={formStyles.gpsBar}>
                <View style={formStyles.gpsInfo}>
                  <Ionicons
                    name={gpsCoords ? 'location' : 'location-outline'}
                    size={16}
                    color={gpsCoords ? '#28A745' : '#6C757D'}
                  />
                  <Text style={formStyles.gpsText}>
                    {gpsCoords
                      ? `GPS: ${gpsCoords.latitude.toFixed(5)}, ${gpsCoords.longitude.toFixed(5)}`
                      : 'Attach Geo-coordinates (Optional)'}
                  </Text>
                </View>
                <TouchableOpacity
                  style={formStyles.gpsBtn}
                  onPress={handleCaptureGps}
                  disabled={isLocating}
                >
                  {isLocating ? (
                    <ActivityIndicator size="small" color={Colors.primary} />
                  ) : (
                    <Text style={formStyles.gpsBtnText}>
                      {gpsCoords ? 'Update GPS' : 'Tag GPS'}
                    </Text>
                  )}
                </TouchableOpacity>
              </View>

              {/* ═══════════════════════════════════════════════ */}
              {/* MODAL FOOTER BUTTONS                           */}
              {/* ═══════════════════════════════════════════════ */}
              <View style={formStyles.modalFooter}>
                <TouchableOpacity
                  style={formStyles.btnCancel}
                  onPress={handleClose}
                  activeOpacity={0.8}
                >
                  <Text style={formStyles.btnCancelText}>Cancel</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={[formStyles.btnAddComplaint, isSubmitting && { opacity: 0.7 }]}
                  onPress={handleSubmit}
                  disabled={isSubmitting}
                  activeOpacity={0.85}
                >
                  {isSubmitting && (
                    <ActivityIndicator size="small" color="#FFFFFF" style={{ marginRight: 8 }} />
                  )}
                  <Text style={formStyles.btnAddComplaintText}>
                    {isSubmitting ? 'Submitting...' : 'Add Complaint'}
                  </Text>
                </TouchableOpacity>
              </View>
            </View>
          )}
        </View>
      </ScrollView>

      {/* ═══════════════════════════════════════════════ */}
      {/* SUCCESS CONFIRMATION MODAL                      */}
      {/* ═══════════════════════════════════════════════ */}
      <Modal
        visible={successModalVisible}
        transparent
        animationType="fade"
        onRequestClose={() => setSuccessModalVisible(false)}
      >
        <View style={formStyles.successBackdrop}>
          <View style={formStyles.successCard}>
            <View style={formStyles.successIconBox}>
              <Ionicons name="checkmark-circle" size={48} color="#28A745" />
            </View>
            <Text style={formStyles.successHeader}>Complaint Added!</Text>
            <Text style={formStyles.successSub}>
              Complaint has been successfully registered in WSSP CMS.
            </Text>

            <View style={formStyles.successBadge}>
              <Text style={formStyles.successBadgeLabel}>COMPLAINT NO</Text>
              <Text style={formStyles.successBadgeNo}>
                {registeredComplaint?.complaint_no || 'CMS-PENDING'}
              </Text>
            </View>

            <View style={formStyles.successDetailsTable}>
              <View style={formStyles.successTableRow}>
                <Text style={formStyles.successTableKey}>Applicant:</Text>
                <Text style={formStyles.successTableVal}>
                  {registeredComplaint?.citizen_name || `${firstName} ${lastName}`}
                </Text>
              </View>
              <View style={formStyles.successTableRow}>
                <Text style={formStyles.successTableKey}>Contact:</Text>
                <Text style={formStyles.successTableVal}>{cellNumber}</Text>
              </View>
              <View style={formStyles.successTableRow}>
                <Text style={formStyles.successTableKey}>Location:</Text>
                <Text style={formStyles.successTableVal}>
                  {registeredComplaint?.location || 'Zone Selected'}
                </Text>
              </View>
              <View style={formStyles.successTableRow}>
                <Text style={formStyles.successTableKey}>Status:</Text>
                <Text style={[formStyles.successTableVal, { color: '#E0A800', fontWeight: '700' }]}>
                  Pending
                </Text>
              </View>
            </View>

            <View style={formStyles.successActionsRow}>
              <TouchableOpacity
                style={formStyles.successBtnSecondary}
                onPress={handleResetForm}
              >
                <Text style={formStyles.successBtnSecondaryText}>Add Another</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={formStyles.successBtnPrimary}
                onPress={() => {
                  setSuccessModalVisible(false);
                  if (onSuccessNavigate) onSuccessNavigate();
                  else if (navigation?.navigate) navigation.navigate('Complaints');
                }}
              >
                <Text style={formStyles.successBtnPrimaryText}>View Complaints</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </KeyboardAvoidingView>
  );
};

const formStyles = StyleSheet.create({
  screenContainer: {
    flex: 1,
    backgroundColor: '#F4F6F9',
  },
  scrollArea: {
    flex: 1,
  },
  scrollContent: {
    padding: 12,
    paddingBottom: 40,
  },

  // Modal Container styled like Bootstrap HTML modal-content
  modalCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#DEE2E6',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 6,
    elevation: 3,
    overflow: 'hidden',
  },
  modalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderBottomWidth: 1,
    borderBottomColor: '#E9ECEF',
    backgroundColor: '#FFFFFF',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: Colors.primaryDark,
    letterSpacing: 0.2,
  },
  modalCloseButton: {
    width: 28,
    height: 28,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 4,
  },
  modalBody: {
    padding: 16,
  },

  // Section Headers (WSSP Blue text with Orange Accent Indicator)
  sectionHeaderContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    marginTop: 6,
  },
  sectionAccentBar: {
    width: 3.5,
    height: 18,
    backgroundColor: Colors.accent, // #FF7A00 WSSP Brand Orange
    borderRadius: 2,
    marginRight: 8,
  },
  sectionHeading: {
    fontSize: 15.5,
    fontWeight: '700',
    color: Colors.primary, // #0080DF WSSP Municipal Blue
    letterSpacing: 0.2,
  },
  sectionDivider: {
    height: 1,
    backgroundColor: '#E2E8F0',
    marginVertical: 16,
  },

  // Form Rows & Grid Layout (2-columns matching form-row / col-md-6)
  formRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 12,
  },
  formRowSingle: {
    marginBottom: 12,
  },
  colHalf: {
    flex: 1,
  },

  // Form Group & Label
  formGroup: {
    marginBottom: 0,
  },
  label: {
    fontSize: 13,
    fontWeight: '600',
    color: '#212529',
    marginBottom: 5,
  },
  requiredStar: {
    color: '#DC3545',
    fontWeight: '700',
  },

  // Input Control (form-control style)
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#CED4DA',
    borderRadius: 5,
    paddingHorizontal: 10,
    height: 38,
  },
  inputFocused: {
    borderColor: '#80BDFF',
    shadowColor: '#007BFF',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.25,
    shadowRadius: 3,
    elevation: 1,
  },
  inputDisabled: {
    backgroundColor: '#E9ECEF',
    borderColor: '#CED4DA',
  },
  inputControl: {
    flex: 1,
    fontSize: 13.5,
    color: '#495057',
    padding: 0,
    margin: 0,
  },

  // Select Box (form-select style)
  selectBox: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#CED4DA',
    borderRadius: 5,
    paddingHorizontal: 10,
    height: 38,
  },
  selectText: {
    flex: 1,
    fontSize: 13.5,
    color: '#212529',
  },
  placeholderText: {
    color: '#6C757D',
  },

  // File Input (HTML style: [ Choose File ] No file chosen)
  fileInputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#CED4DA',
    borderRadius: 5,
    padding: 4,
  },
  fileChooseBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#E9ECEF',
    borderWidth: 1,
    borderColor: '#CED4DA',
    borderRadius: 4,
    paddingVertical: 5,
    paddingHorizontal: 10,
    marginRight: 10,
  },
  fileChooseBtnText: {
    fontSize: 12.5,
    fontWeight: '600',
    color: '#212529',
  },
  fileStatusText: {
    flex: 1,
    fontSize: 12.5,
    color: '#6C757D',
  },
  imageThumbnailCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F8F9FA',
    borderWidth: 1,
    borderColor: '#E9ECEF',
    borderRadius: 6,
    padding: 8,
    marginTop: 8,
  },
  imageThumbnail: {
    width: 48,
    height: 48,
    borderRadius: 4,
    backgroundColor: '#E9ECEF',
    marginRight: 10,
  },
  imageThumbnailMeta: {
    flex: 1,
  },
  imageThumbnailName: {
    fontSize: 12,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  imageRemoveBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  imageRemoveText: {
    fontSize: 12,
    color: '#DC3545',
    fontWeight: '600',
  },

  // GPS Bar
  gpsBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#F8F9FA',
    borderWidth: 1,
    borderColor: '#E9ECEF',
    borderRadius: 6,
    paddingHorizontal: 12,
    paddingVertical: 8,
    marginTop: 4,
    marginBottom: 16,
  },
  gpsInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    flex: 1,
  },
  gpsText: {
    fontSize: 12,
    color: '#495057',
  },
  gpsBtn: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 4,
    backgroundColor: '#E7F1FF',
  },
  gpsBtnText: {
    fontSize: 12,
    fontWeight: '600',
    color: Colors.primary,
  },

  // Modal Footer (Cancel & Add Complaint buttons)
  modalFooter: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    alignItems: 'center',
    gap: 12,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#E2E8F0',
    marginTop: 8,
  },
  btnCancel: {
    paddingVertical: 9,
    paddingHorizontal: 18,
    borderRadius: 6,
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#CBD5E1',
    alignItems: 'center',
    justifyContent: 'center',
    minWidth: 85,
  },
  btnCancelText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#475569',
  },
  btnClose: {
    paddingVertical: 9,
    paddingHorizontal: 18,
    borderRadius: 6,
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#CBD5E1',
    alignItems: 'center',
    justifyContent: 'center',
    minWidth: 85,
  },
  btnCloseText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#475569',
  },
  btnAddComplaint: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 9,
    paddingHorizontal: 22,
    borderRadius: 6,
    backgroundColor: Colors.primary, // #0080DF WSSP Municipal Blue
    minWidth: 140,
    elevation: 2,
    boxShadow: '0px 2px 6px rgba(0, 128, 223, 0.35)',
  },
  btnAddComplaintText: {
    fontSize: 14,
    fontWeight: '700',
    color: '#FFFFFF',
    letterSpacing: 0.2,
  },

  // Loading & Error Banner
  loadingBox: {
    padding: 36,
    alignItems: 'center',
    justifyContent: 'center',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 13,
    color: '#6C757D',
  },
  errorBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F8D7DA',
    borderColor: '#F5C6CB',
    borderWidth: 1,
    padding: 10,
    marginHorizontal: 16,
    marginTop: 12,
    borderRadius: 5,
  },
  errorBannerText: {
    flex: 1,
    fontSize: 12.5,
    color: '#721C24',
    fontWeight: '500',
  },

  // Select Dropdown Modal
  selectModalBackdrop: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.45)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  selectModalCard: {
    width: '100%',
    maxWidth: 380,
    maxHeight: '75%',
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 10,
    elevation: 8,
  },
  selectModalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#E9ECEF',
    backgroundColor: '#F8F9FA',
  },
  selectModalTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: '#212529',
  },
  selectModalCloseBtn: {
    padding: 4,
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#E9ECEF',
    backgroundColor: '#FFFFFF',
  },
  searchInput: {
    flex: 1,
    fontSize: 13,
    color: '#212529',
    padding: 0,
  },
  selectListScroll: {
    maxHeight: 320,
  },
  selectListItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F1F3F5',
  },
  selectListItemActive: {
    backgroundColor: '#EBF5FF',
  },
  selectListItemText: {
    fontSize: 13.5,
    color: '#212529',
    flex: 1,
  },
  selectListItemTextActive: {
    color: Colors.primary,
    fontWeight: '700',
  },
  selectModalCancelBtn: {
    paddingVertical: 12,
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#E9ECEF',
    backgroundColor: '#F8F9FA',
  },
  selectModalCancelText: {
    fontSize: 13.5,
    fontWeight: '600',
    color: '#6C757D',
  },

  // Success Modal
  successBackdrop: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  successCard: {
    width: '100%',
    maxWidth: 380,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 24,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.15,
    shadowRadius: 12,
    elevation: 8,
  },
  successIconBox: {
    marginBottom: 10,
  },
  successHeader: {
    fontSize: 20,
    fontWeight: '800',
    color: '#212529',
    marginBottom: 4,
    textAlign: 'center',
  },
  successSub: {
    fontSize: 12.5,
    color: '#6C757D',
    textAlign: 'center',
    marginBottom: 16,
  },
  successBadge: {
    backgroundColor: '#E7F1FF',
    borderWidth: 1,
    borderColor: '#B8DAFF',
    borderRadius: 8,
    paddingVertical: 10,
    paddingHorizontal: 20,
    alignItems: 'center',
    width: '100%',
    marginBottom: 16,
  },
  successBadgeLabel: {
    fontSize: 10,
    fontWeight: '700',
    color: Colors.primary,
    letterSpacing: 0.5,
  },
  successBadgeNo: {
    fontSize: 22,
    fontWeight: '800',
    color: Colors.primaryDark,
    letterSpacing: 1,
  },
  successDetailsTable: {
    width: '100%',
    backgroundColor: '#F8F9FA',
    borderRadius: 6,
    padding: 12,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#E9ECEF',
  },
  successTableRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 3,
  },
  successTableKey: {
    fontSize: 12.5,
    color: '#6C757D',
  },
  successTableVal: {
    fontSize: 12.5,
    fontWeight: '600',
    color: '#212529',
  },
  successActionsRow: {
    flexDirection: 'row',
    gap: 10,
    width: '100%',
  },
  successBtnSecondary: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 5,
    borderWidth: 1,
    borderColor: '#CED4DA',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
  },
  successBtnSecondaryText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#495057',
  },
  successBtnPrimary: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 5,
    backgroundColor: Colors.primary,
    alignItems: 'center',
  },
  successBtnPrimaryText: {
    fontSize: 13,
    fontWeight: '700',
    color: '#FFFFFF',
  },
});
