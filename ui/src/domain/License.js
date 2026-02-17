/**
 * @typedef {Object} License
 * @property {string} id
 * @property {string} tier - 'free' | 'pro' | 'enterprise'
 * @property {number} maxExtractions
 * @property {number} usedExtractions
 * @property {Date} expiresAt
 * @property {boolean} isActive
 */

export const LicenseTier = {
    FREE: 'free',
    PRO: 'pro',
    ENTERPRISE: 'enterprise'
};
