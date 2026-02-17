import React, { useState, useEffect } from 'react';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { Input } from '../components/Input';
import { Select2 } from '../components/Select2';
import { useAppStore } from '../../store/appStore';
import { ArrowLeft, Play, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';
import { createCampaign } from '../../infrastructure/services/campaignService';
import { getCountries, getRegions, getProvinces, getCities } from '../../infrastructure/services/geonamesService';

// Predefined activities (can be expanded)
const ACTIVITIES = [
    { value: 'restaurants', label: 'Restaurants' },
    { value: 'hotels', label: 'Hotels' },
    { value: 'cafes', label: 'Cafes' },
    { value: 'bars', label: 'Bars' },
    { value: 'gyms', label: 'Gyms' },
    { value: 'pharmacies', label: 'Pharmacies' },
    { value: 'supermarkets', label: 'Supermarkets' },
    { value: 'dentists', label: 'Dentists' },
    { value: 'lawyers', label: 'Lawyers' },
    { value: 'plumbers', label: 'Plumbers' },
].sort((a, b) => a.label.localeCompare(b.label));

// Most common locales (hardcoded fallback)
const COMMON_LOCALES = [
    { value: 'en-US', label: 'English (United States)' },
    { value: 'en-GB', label: 'English (United Kingdom)' },
    { value: 'es-ES', label: 'Spanish (Spain)' },
    { value: 'es-MX', label: 'Spanish (Mexico)' },
    { value: 'fr-FR', label: 'French (France)' },
    { value: 'de-DE', label: 'German (Germany)' },
    { value: 'it-IT', label: 'Italian (Italy)' },
    { value: 'pt-BR', label: 'Portuguese (Brazil)' },
    { value: 'pt-PT', label: 'Portuguese (Portugal)' },
    { value: 'ja-JP', label: 'Japanese (Japan)' },
];

export const CreateCampaignView = () => {
    const { setView, addCampaign, startExtraction } = useAppStore();

    // Form state
    const [formData, setFormData] = useState({
        activity: null,
        country: null,
        region: null,
        province: null,
        city: null,
        min_population: 15000,
        locale: 'en-US',
        max_results: 50,
        min_rating: 4.0
    });

    // Data options loaded from API
    const [countries, setCountries] = useState([]);
    const [regions, setRegions] = useState([]);
    const [provinces, setProvinces] = useState([]);
    const [cities, setCities] = useState([]);
    const [localeOptions, setLocaleOptions] = useState([]);

    // Loading states
    const [loading, setLoading] = useState({
        countries: false,
        regions: false,
        provinces: false,
        cities: false,
        submit: false
    });

    // Error states
    const [errors, setErrors] = useState({});

    // Load countries on mount
    useEffect(() => {
        loadCountries();
    }, []);

    // Load regions and locales when country changes
    useEffect(() => {
        if (formData.country) {
            loadRegions(formData.country.code);

            // Parse languages from country (comma-separated string)
            const languages = formData.country.languages || '';
            const langCodes = languages.split(',').map(l => l.trim()).filter(Boolean);

            // Build country-specific locale options
            const countryLocales = langCodes.map(lang => {
                // Convert language code to locale (e.g., "en" -> "en-US", "es" -> "es-ES")
                const locale = lang.includes('-') ? lang : `${lang}-${formData.country.code}`;
                return {
                    value: locale,
                    label: `${lang.toUpperCase()} (${formData.country.name})`
                };
            });

            // Build grouped options for Select2
            const groupedOptions = [];

            // Group 1: Country-specific locales (if any)
            if (countryLocales.length > 0) {
                groupedOptions.push({
                    label: `${formData.country.name} Languages`,
                    options: countryLocales
                });
            }

            // Group 2: Common locales
            groupedOptions.push({
                label: 'Common Locales',
                options: COMMON_LOCALES
            });

            setLocaleOptions(groupedOptions);

            // Auto-select first available locale
            const firstLocale = countryLocales.length > 0
                ? countryLocales[0].value
                : COMMON_LOCALES[0].value;

            setFormData(prev => ({
                ...prev,
                locale: firstLocale,
                region: null,
                province: null,
                city: null
            }));

            setProvinces([]);
            setCities([]);
        }
    }, [formData.country]);

    // Load provinces when region changes
    useEffect(() => {
        if (formData.country && formData.region) {
            loadProvinces(formData.country.code, formData.region.code);
            // Reset downstream selections
            setFormData(prev => ({
                ...prev,
                province: null,
                city: null
            }));
            setCities([]);
        }
    }, [formData.region]);

    // Load cities when province changes (or when region selected without province)
    useEffect(() => {
        if (formData.country && (formData.province || formData.region)) {
            const filters = {
                min_population: formData.min_population
            };
            if (formData.province) {
                filters.admin2_code = formData.province.code;
            } else if (formData.region) {
                filters.admin1_code = formData.region.code;
            }
            loadCities(formData.country.code, filters);
        }
    }, [formData.province, formData.min_population]);

    const loadCountries = async () => {
        setLoading(prev => ({ ...prev, countries: true }));
        try {
            const data = await getCountries();
            setCountries(data.map(c => ({
                value: c.code,
                label: c.name,
                code: c.code,
                name: c.name,
                languages: c.languages  // Keep languages for locale extraction
            })));
        } catch (error) {
            console.error('Failed to load countries:', error);
            setErrors(prev => ({ ...prev, countries: error.message }));
        } finally {
            setLoading(prev => ({ ...prev, countries: false }));
        }
    };

    const loadRegions = async (countryCode) => {
        setLoading(prev => ({ ...prev, regions: true }));
        try {
            const data = await getRegions(countryCode);
            setRegions(data.map(r => ({
                value: r.geoname_id,
                label: r.name,
                code: r.code,
                name: r.name
            })));
        } catch (error) {
            console.error('Failed to load regions:', error);
            setErrors(prev => ({ ...prev, regions: error.message }));
        } finally {
            setLoading(prev => ({ ...prev, regions: false }));
        }
    };

    const loadProvinces = async (countryCode, admin1Code) => {
        setLoading(prev => ({ ...prev, provinces: true }));
        try {
            const data = await getProvinces(countryCode, admin1Code);
            setProvinces(data.map(p => ({
                value: p.geoname_id,
                label: p.name,
                code: p.code,
                name: p.name
            })));
        } catch (error) {
            console.error('Failed to load provinces:', error);
            setErrors(prev => ({ ...prev, provinces: error.message }));
        } finally {
            setLoading(prev => ({ ...prev, provinces: false }));
        }
    };

    const loadCities = async (countryCode, filters) => {
        setLoading(prev => ({ ...prev, cities: true }));
        try {
            const data = await getCities(countryCode, filters);
            setCities(data.map(c => ({
                value: c.geoname_id,
                label: c.name,
                code: c.code,
                name: c.name,
                population: c.population
            })));
        } catch (error) {
            console.error('Failed to load cities:', error);
            setErrors(prev => ({ ...prev, cities: error.message }));
        } finally {
            setLoading(prev => ({ ...prev, cities: false }));
        }
    };

    const isValid = () => {
        return formData.activity && formData.country;
        // Geographic scope is optional - can be country-wide or narrowed down
    };

    const handleSubmit = async () => {
        if (!isValid()) return;

        setLoading(prev => ({ ...prev, submit: true }));

        try {
            // Determine scope and geoname_id based on selection
            let scope = 'country';
            let scopeGeonameId = null;
            let scopeGeonameName = null;

            if (formData.city) {
                scope = 'city';
                scopeGeonameId = formData.city.value; // geoname_id
                scopeGeonameName = formData.city.name;
            } else if (formData.province) {
                scope = 'admin2';
                scopeGeonameId = formData.province.value;
                scopeGeonameName = formData.province.name;
            } else if (formData.region) {
                scope = 'admin1';
                scopeGeonameId = formData.region.value;
                scopeGeonameName = formData.region.name;
            }

            // Build API request payload
            const payload = {
                activity: formData.activity.value,
                country_code: formData.country.code,
                scope: scope,
                scope_geoname_id: scopeGeonameId,
                scope_geoname_name: scopeGeonameName,
                min_population: formData.min_population,
                locale: formData.locale,
                max_results: formData.max_results,
                min_rating: formData.min_rating
            };

            // Create campaign via API
            const campaign = await createCampaign(payload);

            // Add to store
            addCampaign({
                id: campaign.campaign_id,
                title: campaign.title,
                status: campaign.status,
                totalTasks: campaign.total_tasks,
                createdAt: campaign.created_at
            });

            // Start extraction via WebSocket
            await startExtraction(campaign.campaign_id);

            // Navigate to dashboard
            setView('dashboard');

        } catch (error) {
            console.error('Failed to create campaign:', error);
            alert(`Failed to create campaign: ${error.message}`);
        } finally {
            setLoading(prev => ({ ...prev, submit: false }));
        }
    };

    return (
        <div className="min-h-screen bg-dark-bg">
            {/* Header */}
            <header className="border-b border-dark-border bg-dark-surface">
                <div className="max-w-4xl mx-auto px-6 py-4">
                    <button
                        onClick={() => setView('dashboard')}
                        className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-4"
                    >
                        <ArrowLeft size={20} />
                        <span>Back to Dashboard</span>
                    </button>
                    <h1 className="text-2xl font-bold text-white">Create Campaign</h1>
                    <p className="text-sm text-gray-400 mt-1">
                        Select activity and geographic scope (title auto-generated)
                    </p>
                </div>
            </header>

            {/* Form */}
            <main className="max-w-4xl mx-auto px-6 py-8">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    <Card>
                        <div className="space-y-6">
                            {/* Activity Selection */}
                            <Select2
                                label="Activity / Business Type *"
                                placeholder="Select activity..."
                                options={ACTIVITIES}
                                value={formData.activity}
                                onChange={(selected) => setFormData({ ...formData, activity: selected })}
                                isSearchable
                            />

                            {/* Geographic Selection */}
                            <div className="space-y-4 pt-4 border-t border-dark-border">
                                <h3 className="text-lg font-semibold text-white">Geographic Scope</h3>
                                <p className="text-sm text-gray-400 -mt-2">
                                    Required: Country. Optional: narrow down to region, province, or city
                                </p>

                                {/* Country */}
                                <Select2
                                    label="Country *"
                                    placeholder={loading.countries ? "Loading countries..." : "Select country..."}
                                    options={countries}
                                    value={formData.country}
                                    onChange={(selected) => setFormData({ ...formData, country: selected })}
                                    isDisabled={loading.countries}
                                />

                                {/* Region (Admin1) */}
                                {formData.country && (
                                    <motion.div
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                    >
                                        <Select2
                                            label="Region / State (optional)"
                                            placeholder={loading.regions ? "Loading regions..." : "Select region..."}
                                            options={regions}
                                            value={formData.region}
                                            onChange={(selected) => setFormData({ ...formData, region: selected })}
                                            isDisabled={loading.regions}
                                            isClearable
                                        />
                                    </motion.div>
                                )}

                                {/* Province (Admin2) */}
                                {formData.region && (
                                    <motion.div
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                    >
                                        <Select2
                                            label="Province (optional)"
                                            placeholder={loading.provinces ? "Loading provinces..." : "Select province..."}
                                            options={provinces}
                                            value={formData.province}
                                            onChange={(selected) => setFormData({ ...formData, province: selected })}
                                            isDisabled={loading.provinces}
                                            isClearable
                                        />
                                    </motion.div>
                                )}

                                {/* City */}
                                {(formData.region || formData.province) && (
                                    <motion.div
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                    >
                                        <Select2
                                            label="City (optional)"
                                            placeholder={loading.cities ? "Loading cities..." : "Select city..."}
                                            options={cities}
                                            value={formData.city}
                                            onChange={(selected) => setFormData({ ...formData, city: selected })}
                                            isDisabled={loading.cities}
                                            isClearable
                                        />
                                    </motion.div>
                                )}
                            </div>

                            {/* Advanced Options */}
                            <div className="space-y-4 pt-4 border-t border-dark-border">
                                <h3 className="text-lg font-semibold text-white">Advanced Options</h3>

                                <div className="grid grid-cols-2 gap-4">
                                    <Input
                                        label="Min Population"
                                        type="number"
                                        value={formData.min_population}
                                        onChange={(e) => setFormData({ ...formData, min_population: parseInt(e.target.value) || 0 })}
                                    />
                                    <Input
                                        label="Max Results per Task"
                                        type="number"
                                        value={formData.max_results}
                                        onChange={(e) => setFormData({ ...formData, max_results: parseInt(e.target.value) || 50 })}
                                    />
                                    <Input
                                        label="Min Rating"
                                        type="number"
                                        step="0.1"
                                        value={formData.min_rating}
                                        onChange={(e) => setFormData({ ...formData, min_rating: parseFloat(e.target.value) || 0 })}
                                    />
                                    {formData.country && localeOptions.length > 0 ? (
                                        <Select2
                                            label="Locale"
                                            placeholder="Select locale..."
                                            options={localeOptions}
                                            value={
                                                // Find selected value in grouped options
                                                localeOptions.flatMap(group => group.options).find(l => l.value === formData.locale)
                                            }
                                            onChange={(selected) => setFormData({ ...formData, locale: selected.value })}
                                        />
                                    ) : (
                                        <Input
                                            label="Locale"
                                            value={formData.locale}
                                            onChange={(e) => setFormData({ ...formData, locale: e.target.value })}
                                            placeholder="e.g., en-US"
                                        />
                                    )}
                                </div>
                            </div>

                            {/* Preview */}
                            {isValid() && (
                                <motion.div
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="bg-dark-hover rounded-lg p-4 border border-dark-border"
                                >
                                    <h4 className="text-sm font-medium text-gray-400 mb-2">Campaign Preview</h4>
                                    <div className="text-sm text-gray-300 space-y-1">
                                        <p><span className="text-gray-500">Activity:</span> {formData.activity.label}</p>
                                        <p><span className="text-gray-500">Scope:</span> {
                                            formData.city ? `${formData.city.name}, ${formData.country.name}` :
                                                formData.province ? `${formData.province.name}, ${formData.country.name}` :
                                                    formData.region ? `${formData.region.name}, ${formData.country.name}` :
                                                        formData.country.name
                                        }</p>
                                        <p className="text-xs text-gray-500 italic mt-2">Title will be auto-generated</p>
                                    </div>
                                </motion.div>
                            )}

                            {/* Submit Button */}
                            <div className="flex justify-end gap-4 pt-4">
                                <Button
                                    variant="secondary"
                                    onClick={() => setView('dashboard')}
                                    disabled={loading.submit}
                                >
                                    Cancel
                                </Button>
                                <Button
                                    onClick={handleSubmit}
                                    disabled={!isValid() || loading.submit}
                                >
                                    {loading.submit ? (
                                        <>
                                            <Loader2 size={18} className="animate-spin" />
                                            Creating...
                                        </>
                                    ) : (
                                        <>
                                            <Play size={18} />
                                            Create and Start Extraction
                                        </>
                                    )}
                                </Button>
                            </div>
                        </div>
                    </Card>
                </motion.div>
            </main>
        </div>
    );
};
