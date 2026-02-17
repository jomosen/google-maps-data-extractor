import { create } from 'zustand';
import { realExtractionService } from '../infrastructure/RealExtractionService';
import { LicenseTier } from '../domain/License';

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

    // Extraction state
    bots: [],
    places: [],

    // Actions
    setView: (view) => set({ currentView: view }),

    addCampaign: (campaign) => {
        set({ campaigns: [campaign, ...get().campaigns] });
    },

    createCampaign: (campaignData) => {
        // For now, just create a simple campaign object
        const campaign = {
            id: `camp-${Date.now()}`,
            name: campaignData.name || 'Test Campaign',
            createdAt: new Date(),
            status: 'pending'
        };
        set({ campaigns: [campaign, ...get().campaigns] });
        return campaign;
    },

    startExtraction: async (campaign) => {
        // Set active campaign with full data and initial progress
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

        // Subscribe to real extraction updates
        realExtractionService.subscribe((state) => {
            const currentCampaign = get().activeCampaign;
            set({
                bots: state.bots,
                places: state.places,
                activeCampaign: {
                    ...currentCampaign,
                    status: state.isRunning ? 'running' : 'idle',
                    progress: state.bots.length > 0 ? 50 : 0 // Mock progress
                }
            });
        });

        // Start real extraction with WebSocket
        try {
            await realExtractionService.startExtraction(campaign.id);
        } catch (error) {
            console.error('Failed to start extraction:', error);
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

    // Mock data generators
    loadMockCampaigns: () => {
        const mockCampaigns = [
            {
                id: 'camp-1',
                title: 'LA Restaurants Q1',
                activity: 'restaurant',
                geography: {
                    countryCode: 'US',
                    countryName: 'United States',
                    admin1Codes: ['CA'],
                    cityIds: ['1']
                },
                status: 'completed',
                progress: 100,
                totalExtracted: 1250,
                createdAt: new Date('2026-02-10'),
                completedAt: new Date('2026-02-11')
            },
            {
                id: 'camp-2',
                title: 'Madrid Hotels',
                activity: 'hotel',
                geography: {
                    countryCode: 'ES',
                    countryName: 'Spain',
                    admin1Codes: ['M'],
                    cityIds: ['8']
                },
                status: 'completed',
                progress: 100,
                totalExtracted: 890,
                createdAt: new Date('2026-02-12'),
                completedAt: new Date('2026-02-13')
            }
        ];
        set({ campaigns: mockCampaigns });
    }
}));
