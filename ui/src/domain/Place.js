/**
 * @typedef {Object} Place
 * @property {string} id
 * @property {string} name
 * @property {string} address
 * @property {number} [rating]
 * @property {number} [totalReviews]
 * @property {string} status - 'extracted' | 'processing' | 'error'
 * @property {Date} extractedAt
 * @property {string} [phone]
 * @property {string} [website]
 */

export const PlaceStatus = {
    EXTRACTED: 'extracted',
    PROCESSING: 'processing',
    ERROR: 'error'
};
