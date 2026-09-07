import AsyncStorage from '@react-native-async-storage/async-storage';

/**
 * Type-safe persistent storage service.
 * Supports web and native Expo Go storage seamlessly.
 */
export const StorageService = {
  async setItem<T>(key: string, value: T): Promise<boolean> {
    try {
      const serialized = typeof value === 'string' ? value : JSON.stringify(value);
      await AsyncStorage.setItem(key, serialized);
      return true;
    } catch (e) {
      console.error(`[StorageService] Failed to set ${key}:`, e);
      return false;
    }
  },

  async getItem<T>(key: string): Promise<T | null> {
    try {
      const item = await AsyncStorage.getItem(key);
      if (!item) return null;
      try {
        return JSON.parse(item) as T;
      } catch {
        return item as unknown as T;
      }
    } catch (e) {
      console.error(`[StorageService] Failed to get ${key}:`, e);
      return null;
    }
  },

  async removeItem(key: string): Promise<boolean> {
    try {
      await AsyncStorage.removeItem(key);
      return true;
    } catch (e) {
      console.error(`[StorageService] Failed to remove ${key}:`, e);
      return false;
    }
  },

  async clearAll(): Promise<boolean> {
    try {
      await AsyncStorage.clear();
      return true;
    } catch (e) {
      console.error('[StorageService] Failed to clear storage:', e);
      return false;
    }
  }
};
