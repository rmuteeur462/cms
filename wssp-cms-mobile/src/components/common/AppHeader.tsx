import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  SafeAreaView,
  Platform,
  Image,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../store/AuthContext';
import { useNavigation } from '@react-navigation/native';

interface AppHeaderProps {
  title?: string;
  onNotificationPress?: () => void;
  onProfilePress?: () => void;
}

export const AppHeader: React.FC<AppHeaderProps> = ({
  title = 'WSSP CMS',
  onNotificationPress,
  onProfilePress,
}) => {
  const { user } = useAuth();
  const navigation = useNavigation<any>();

  const handleProfilePress = () => {
    if (onProfilePress) {
      onProfilePress();
    } else {
      try {
        navigation.navigate('Profile');
      } catch (e) {}
    }
  };

  const handleNotificationPress = () => {
    if (onNotificationPress) {
      onNotificationPress();
    } else {
      try {
        navigation.navigate('Complaints');
      } catch (e) {}
    }
  };

  const initial = user?.full_name
    ? user.full_name.charAt(0).toUpperCase()
    : (user?.username ? user.username.charAt(0).toUpperCase() : 'U');

  return (
    <SafeAreaView style={styles.safeArea}>
      {/* Corporate Navy Blue Header */}
      <View style={styles.header}>
        {/* Left Branding: Official WSSP Logo */}
        <View style={styles.leftSection}>
          <View style={styles.logoBadge}>
            <Image
              source={require('../../assets/imgs/wssp_logo.png')}
              style={styles.logoImage}
              resizeMode="contain"
            />
          </View>
          <View style={styles.titleContainer}>
            <View style={styles.titleRow}>
              <Text style={styles.titleText}>{title}</Text>
              <View style={styles.officialPill}>
                <Text style={styles.officialPillText}>OFFICIAL</Text>
              </View>
            </View>
            <Text style={styles.deptText}>Peshawar Municipality</Text>
          </View>
        </View>

        {/* Right Actions: 🔔 Notifications & 👤 Profile */}
        <View style={styles.rightSection}>
          <TouchableOpacity
            style={styles.actionBtn}
            onPress={handleNotificationPress}
            activeOpacity={0.7}
            accessibilityLabel="Notifications"
          >
            <Ionicons name="notifications-outline" size={20} color="#FFFFFF" />
            <View style={styles.notiBadge}>
              <Text style={styles.notiBadgeText}>3</Text>
            </View>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.avatarBtn}
            onPress={handleProfilePress}
            activeOpacity={0.7}
            accessibilityLabel="Officer Profile"
          >
            <Text style={styles.avatarInitial}>{initial}</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Subtle Bottom Accent Line */}
      <View style={styles.bottomBorder} />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    backgroundColor: '#0A3663', // Seamless Corporate Navy Blue
  },
  header: {
    backgroundColor: '#0A3663',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingTop: Platform.OS === 'android' ? 36 : 12,
    paddingBottom: 14,
  },
  leftSection: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  logoBadge: {
    width: 42,
    height: 42,
    borderRadius: 21,
    backgroundColor: '#FFFFFF',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 4,
    padding: 2,
  },
  logoImage: {
    width: '100%',
    height: '100%',
  },
  titleContainer: {
    justifyContent: 'center',
  },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  titleText: {
    fontSize: 17,
    fontWeight: '900',
    color: '#FFFFFF',
    letterSpacing: 0.4,
  },
  officialPill: {
    backgroundColor: 'rgba(255, 122, 0, 0.22)',
    paddingHorizontal: 6,
    paddingVertical: 1.5,
    borderRadius: 4,
    borderWidth: 0.8,
    borderColor: '#FF7A00',
  },
  officialPillText: {
    fontSize: 8.5,
    fontWeight: '800',
    color: '#FFA940',
    letterSpacing: 0.5,
  },
  deptText: {
    fontSize: 11.5,
    color: '#93C5FD', // Soft sky blue
    fontWeight: '600',
    marginTop: 1,
  },
  rightSection: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  actionBtn: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: 'rgba(255, 255, 255, 0.12)',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  notiBadge: {
    position: 'absolute',
    top: 3,
    right: 3,
    backgroundColor: '#FF7A00', // WSSP Orange badge
    width: 14,
    height: 14,
    borderRadius: 7,
    alignItems: 'center',
    justifyContent: 'center',
  },
  notiBadgeText: {
    fontSize: 9,
    fontWeight: '900',
    color: '#FFFFFF',
  },
  avatarBtn: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#FF7A00', // WSSP Orange Avatar
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1.5,
    borderColor: '#FFFFFF',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 3,
    elevation: 3,
  },
  avatarInitial: {
    fontSize: 14,
    fontWeight: '800',
    color: '#FFFFFF',
  },
  bottomBorder: {
    height: 2,
    backgroundColor: '#0080DF', // Clean WSSP Blue baseline
  },
});
