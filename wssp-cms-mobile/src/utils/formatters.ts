/**
 * Utility Formatters for WSSP CMS
 */

export const Formatters = {
  /**
   * Formats 13-digit Pakistani CNIC: XXXXX-XXXXXXX-X
   */
  formatCNIC(cnic?: string | null): string {
    if (!cnic) return 'N/A';
    const cleaned = cnic.replace(/\D/g, '');
    if (cleaned.length === 13) {
      return `${cleaned.slice(0, 5)}-${cleaned.slice(5, 12)}-${cleaned.slice(12)}`;
    }
    return cnic;
  },

  /**
   * Formats Pakistani phone number: 03XX-XXXXXXX
   */
  formatPhone(phone?: string | null): string {
    if (!phone) return 'N/A';
    const cleaned = phone.replace(/\D/g, '');
    if (cleaned.length === 11 && cleaned.startsWith('03')) {
      return `${cleaned.slice(0, 4)}-${cleaned.slice(4)}`;
    }
    return phone;
  },

  /**
   * Formats ISO Date to readable Pakistani standard: DD MMM YYYY
   */
  formatDate(dateStr?: string | null): string {
    if (!dateStr) return 'N/A';
    try {
      const d = new Date(dateStr);
      if (isNaN(d.getTime())) return dateStr;
      return d.toLocaleDateString('en-GB', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
      });
    } catch {
      return dateStr;
    }
  }
};
