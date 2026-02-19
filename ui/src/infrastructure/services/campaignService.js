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
 * @param {string|null} [campaignData.admin1_code] - Admin1 region code (e.g., 'MD')
 * @param {string|null} [campaignData.admin2_code] - Admin2 province code (e.g., '28')
 * @param {number|null} [campaignData.city_geoname_id] - Geoname ID of a specific city
 * @param {string|null} [campaignData.iso_language] - ISO language code (e.g., 'es')
 * @param {string} [campaignData.location_name] - Display snapshot (e.g., 'Madrid, ES')
 * @param {number} [campaignData.min_population=15000] - Minimum city population
 * @param {string} [campaignData.locale='en-US'] - Locale for extraction results
 * @param {number} [campaignData.max_results=50] - Maximum results per task
 * @param {number} [campaignData.min_rating=4.0] - Minimum rating filter
 * @returns {Promise<Object>} Created campaign with campaign_id, title, status, total_tasks
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

export async function getCampaignById(campaignId) {
    const response = await fetch(`${API_BASE_URL}/campaigns/${campaignId}`);
    if (!response.ok) throw new Error(`Failed to fetch campaign: ${response.status}`);
    return response.json();
}

export async function getCampaignPlaces(campaignId) {
    const response = await fetch(`${API_BASE_URL}/campaigns/${campaignId}/places`);
    if (!response.ok) throw new Error(`Failed to fetch places: ${response.status}`);
    return response.json();
}

export async function getCampaignTasks(campaignId) {
    const response = await fetch(`${API_BASE_URL}/campaigns/${campaignId}/tasks`);
    if (!response.ok) throw new Error(`Failed to fetch tasks: ${response.status}`);
    return response.json();
}

async function _campaignAction(campaignId, action) {
    const response = await fetch(`${API_BASE_URL}/campaigns/${campaignId}/${action}`, { method: 'POST' });
    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || `Failed to ${action} campaign: ${response.status}`);
    }
}

export const startCampaign   = (id) => _campaignAction(id, 'start');
export const resumeCampaign  = (id) => _campaignAction(id, 'resume');
export const archiveCampaign = (id) => _campaignAction(id, 'archive');
