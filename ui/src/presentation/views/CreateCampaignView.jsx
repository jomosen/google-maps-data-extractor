import React, { useState, useEffect } from 'react';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
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

export const CreateCampaignView = () => {
    const { setView, addCampaign } = useAppStore();

    // Form state
    const [formData, setFormData] = useState({
        activity: null,
        country: null,
        region: null,
        province: null,
        city: null,
    });

    // Data options loaded from API
    const [countries, setCountries] = useState([]);
    const [regions, setRegions] = useState([]);
    const [provinces, setProvinces] = useState([]);
    const [cities, setCities] = useState([]);

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

    // Load regions when country changes
    useEffect(() => {
        if (formData.country) {
            loadRegions(formData.country.code);
            setFormData(prev => ({ ...prev, region: null, province: null, city: null }));
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
            const filters = {};
            if (formData.province) {
                filters.admin2_code = formData.province.code;
            } else if (formData.region) {
                filters.admin1_code = formData.region.code;
            }
            loadCities(formData.country.code, filters);
        }
    }, [formData.province]);

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
            // Derive iso_language from the country's first language code
            const languages = formData.country.languages || '';
            const firstLang = languages.split(',').map(l => l.trim()).filter(Boolean)[0] || null;
            const isoLanguage = firstLang ? firstLang.split('-')[0] : null;

            // Build location snapshot: most specific → least specific
            const locationParts = [];
            if (formData.city) locationParts.push(formData.city.name);
            if (formData.province) locationParts.push(formData.province.name);
            if (formData.region) locationParts.push(formData.region.name);
            locationParts.push(formData.country.name);
            const locationName = locationParts.join(', ');

            // Build API request payload
            const payload = {
                activity: formData.activity.value,
                country_code: formData.country.code,
                admin1_code: formData.region?.code ?? null,
                admin2_code: formData.province?.code ?? null,
                city_geoname_id: formData.city?.value ?? null,
                iso_language: isoLanguage,
                location_name: locationName,
            };

            // Create campaign via API
            const campaign = await createCampaign(payload);

            // Add to store and navigate to dashboard
            addCampaign({
                id: campaign.campaign_id,
                title: campaign.title,
                status: campaign.status,
                totalTasks: campaign.total_tasks,
                createdAt: campaign.created_at
            });
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
