/**
 * Geonames API service
 * 
 * Handles HTTP communication with backend /api/geonames endpoints
 * for loading geographic data (countries, regions, provinces, cities)
 */

const API_BASE_URL = 'http://localhost:8000/api/geonames';

/**
 * Get all available countries
 * 
 * @returns {Promise<Array>} List of countries with code, name, continent, capital, population
 */
export async function getCountries() {
    const response = await fetch(`${API_BASE_URL}/countries`);

    if (!response.ok) {
        throw new Error(`Failed to fetch countries: ${response.status}`);
    }

    return response.json();
}

/**
 * Get regions (Admin1 divisions) for a country
 * 
 * @param {string} countryCode - ISO 3166-1 alpha-2 country code (e.g., 'ES')
 * @returns {Promise<Array>} List of regions with geoname_id, name, code, population
 */
export async function getRegions(countryCode) {
    const response = await fetch(`${API_BASE_URL}/countries/${countryCode}/regions`);

    if (!response.ok) {
        throw new Error(`Failed to fetch regions: ${response.status}`);
    }

    return response.json();
}

/**
 * Get provinces (Admin2 divisions) for a country and region
 * 
 * @param {string} countryCode - ISO 3166-1 alpha-2 country code
 * @param {string} admin1Code - Admin1 code from getRegions()
 * @returns {Promise<Array>} List of provinces with geoname_id, name, code, population
 */
export async function getProvinces(countryCode, admin1Code) {
    const url = new URL(`${API_BASE_URL}/countries/${countryCode}/provinces`);
    url.searchParams.append('admin1_code', admin1Code);

    const response = await fetch(url);

    if (!response.ok) {
        throw new Error(`Failed to fetch provinces: ${response.status}`);
    }

    return response.json();
}

/**
 * Get cities for a country, optionally filtered by region/province
 * 
 * @param {string} countryCode - ISO 3166-1 alpha-2 country code
 * @param {Object} [filters={}] - Optional filters
 * @param {string} [filters.admin1_code] - Region code to filter by
 * @param {string} [filters.admin2_code] - Province code to filter by
 * @param {number} [filters.min_population=0] - Minimum population threshold
 * @returns {Promise<Array>} List of cities with geoname_id, name, code, population
 */
export async function getCities(countryCode, filters = {}) {
    const url = new URL(`${API_BASE_URL}/countries/${countryCode}/cities`);

    if (filters.admin1_code) {
        url.searchParams.append('admin1_code', filters.admin1_code);
    }
    if (filters.admin2_code) {
        url.searchParams.append('admin2_code', filters.admin2_code);
    }
    if (filters.min_population !== undefined) {
        url.searchParams.append('min_population', filters.min_population);
    }

    const response = await fetch(url);

    if (!response.ok) {
        throw new Error(`Failed to fetch cities: ${response.status}`);
    }

    return response.json();
}
