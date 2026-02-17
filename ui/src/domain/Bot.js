/**
 * @typedef {Object} Bot
 * @property {string} id
 * @property {number} number
 * @property {string} status - 'idle' | 'running' | 'paused' | 'error'
 * @property {string} currentActivity
 * @property {string} currentLocation
 * @property {number} progress
 * @property {number} extractedCount
 * @property {string} [screenshotUrl]
 */

export const BotStatus = {
    IDLE: 'idle',
    RUNNING: 'running',
    PAUSED: 'paused',
    ERROR: 'error'
};
