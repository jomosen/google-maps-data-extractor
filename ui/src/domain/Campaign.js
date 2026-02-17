/**
 * @typedef {Object} Campaign
 * @property {string} id
 * @property {string} title
 * @property {string} activity
 * @property {GeographicScope} geography
 * @property {string} status - 'pending' | 'running' | 'completed' | 'failed'
 * @property {number} progress - 0-100
 * @property {number} totalExtracted
 * @property {Date} createdAt
 * @property {Date} [startedAt]
 * @property {Date} [completedAt]
 */

/**
 * @typedef {Object} GeographicScope
 * @property {string} countryCode
 * @property {string} countryName
 * @property {string[]} admin1Codes
 * @property {string[]} cityIds
 */

export const CampaignStatus = {
    PENDING: 'pending',
    RUNNING: 'running',
    COMPLETED: 'completed',
    FAILED: 'failed'
};
