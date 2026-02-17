/**
 * Campaign API service
 * 
 * Handles HTTP communication with backend /api/campaigns endpoints
 */

const API_BASE_URL = 'http://localhost:8000/api';

/**
 * Create a new campaign
 * 
 * @param {Object} campaignData - Campaign configuration
 * @param {string} campaignData.activity - Activity to search (e.g., 'restaurants')
 * @param {string} campaignData.country_code - ISO 3166-1 alpha-2 country code (e.g., 'ES')
 * @param {string} [campaignData.region] - Region/state name (optional)
 * @param {string} [campaignData.province] - Province name (optional)
 * @param {string} [campaignData.city] - City name (optional)
 * @param {number} [campaignData.min_population=15000] - Minimum population filter
 * @param {string} [campaignData.locale='en-US'] - Locale for extraction
 * @param {number} [campaignData.max_results=50] - Maximum results per task
 * @param {number} [campaignData.min_rating=4.0] - Minimum rating filter
 * @returns {Promise<Object>} Created campaign with campaign_id, title, status
 */
export async function createCampaign(campaignData) {
    const response = await fetch(`${API_BASE_URL}/campaigns`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(campaignData),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || `Failed to create campaign: ${response.status}`);
    }

    return response.json();
}

/**
 * Get all campaigns
 * 
 * @returns {Promise<Array>} List of campaigns
 */
export async function getCampaigns() {
    const response = await fetch(`${API_BASE_URL}/campaigns`);

    if (!response.ok) {
        throw new Error(`Failed to fetch campaigns: ${response.status}`);
    }

    return response.json();
}

/**
 * Get campaign by ID
 * 
 * @param {string} campaignId - Campaign ULID
 * @returns {Promise<Object>} Campaign details
 */
export async function getCampaign(campaignId) {
    const response = await fetch(`${API_BASE_URL}/campaigns/${campaignId}`);

    if (!response.ok) {
        throw new Error(`Failed to fetch campaign: ${response.status}`);
    }

    return response.json();
}
