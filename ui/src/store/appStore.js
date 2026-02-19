import { create } from 'zustand';
import { realExtractionService } from '../infrastructure/RealExtractionService';
import { LicenseTier } from '../domain/License';
import { getCampaigns, getCampaignById, getCampaignPlaces, getCampaignTasks, startCampaign, resumeCampaign, archiveCampaign } from '../infrastructure/services/campaignService';

export const useAppStore = create((set, get) => ({
    // Navigation
    currentView: 'dashboard', // 'dashboard' | 'create' | 'monitor'

    // License (Mock)
    license: {
        id: 'lic-001',
        tier: LicenseTier.PRO,
        maxExtractions: 10000,
        usedExtractions: 3450,
        expiresAt: new Date('2026-12-31'),
        isActive: true
    },

    // Campaigns
    campaigns: [],
    activeCampaign: null,
    selectedCampaign: null,
    campaignPlaces: [],
    campaignTasks: [],

    // Extraction state
    bots: [],
    places: [],

    // Actions
    setView: (view) => set({ currentView: view }),

    addCampaign: (campaign) => {
        set({ campaigns: [campaign, ...get().campaigns] });
    },

    loadCampaigns: async () => {
        try {
            const campaigns = await getCampaigns();
            set({ campaigns });
        } catch (error) {
            console.error("Failed to load campaigns:", error);
        }
    },

    selectCampaign: async (campaign) => {
        set({ selectedCampaign: campaign, campaignPlaces: [], campaignTasks: [], currentView: 'detail' });
        try {
            const [detail, places, tasks] = await Promise.all([
                getCampaignById(campaign.campaign_id),
                getCampaignPlaces(campaign.campaign_id),
                getCampaignTasks(campaign.campaign_id),
            ]);
            set({ selectedCampaign: detail, campaignPlaces: places, campaignTasks: tasks });
        } catch (error) {
            console.error("Failed to load campaign detail:", error);
        }
    },

    campaignAction: async (action, campaignId) => {
        try {
            if (action === 'start') await startCampaign(campaignId);
            else if (action === 'resume') await resumeCampaign(campaignId);
            else if (action === 'archive') await archiveCampaign(campaignId);
            // Refresh detail after action
            const detail = await getCampaignById(campaignId);
            set({ selectedCampaign: detail });
            // Refresh list in background
            getCampaigns().then(campaigns => set({ campaigns }));
        } catch (error) {
            console.error(`Failed to ${action} campaign:`, error);
        }
    },

    startExtraction: async (campaign) => {
        set({
            activeCampaign: {
                ...campaign,
                status: 'running',
                progress: 0
            },
            currentView: 'monitor',
            bots: [],
            places: []
        });

        realExtractionService.subscribe((state) => {
            const currentCampaign = get().activeCampaign;
            set({
                bots: state.bots,
                places: state.places,
                activeCampaign: {
                    ...currentCampaign,
                    status: state.isRunning ? 'running' : 'idle',
                    progress: state.bots.length > 0 ? 50 : 0
                }
            });
        });

        try {
            await realExtractionService.startExtraction(campaign.id);
        } catch (error) {
            console.error("Failed to start extraction:", error);
            set({
                activeCampaign: {
                    ...get().activeCampaign,
                    status: 'error'
                }
            });
        }
    },

    updateExtractionState: ({ campaign, bots, places }) => {
        set({
            activeCampaign: campaign,
            bots: bots,
            places: places
        });
    },
}));
