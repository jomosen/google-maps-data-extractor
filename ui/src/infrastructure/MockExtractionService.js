import { CampaignStatus } from '../domain/Campaign';
import { PlaceStatus } from '../domain/Place';
import { BotStatus } from '../domain/Bot';
import { mockPlaceNames, mockStreets } from './mockData';

class MockExtractionService {
    constructor() {
        this.campaigns = [];
        this.activeCampaign = null;
        this.bots = [];
        this.places = [];
        this.intervalId = null;
        this.botIntervalIds = [];
        this.listeners = [];
    }

    subscribe(listener) {
        this.listeners.push(listener);
        return () => {
            this.listeners = this.listeners.filter(l => l !== listener);
        };
    }

    notify() {
        this.listeners.forEach(listener => listener({
            campaign: this.activeCampaign,
            bots: this.bots,
            places: this.places
        }));
    }

    createCampaign(campaignData) {
        const campaign = {
            id: `campaign-${Date.now()}`,
            ...campaignData,
            status: CampaignStatus.PENDING,
            progress: 0,
            totalExtracted: 0,
            createdAt: new Date()
        };

        this.campaigns.push(campaign);
        return campaign;
    }

    async startExtraction(campaignId) {
        const campaign = this.campaigns.find(c => c.id === campaignId);
        if (!campaign) throw new Error('Campaign not found');

        campaign.status = CampaignStatus.RUNNING;
        campaign.startedAt = new Date();
        this.activeCampaign = campaign;

        // Initialize 3 bots
        const botCount = 3;
        this.bots = Array.from({ length: botCount }, (_, i) => ({
            id: `bot-${i + 1}`,
            number: i + 1,
            status: BotStatus.RUNNING,
            currentActivity: campaign.activity,
            currentLocation: campaign.geography.countryName,
            progress: 0,
            extractedCount: 0,
            screenshotUrl: null
        }));

        this.places = [];
        this.startMockExtraction();
        this.notify();

        return { success: true };
    }

    startMockExtraction() {
        let counter = 0;
        const maxPlaces = 50;

        // Main extraction interval
        this.intervalId = setInterval(() => {
            if (counter >= maxPlaces) {
                this.stopExtraction();
                return;
            }

            // Add a new place every 2-3 seconds
            const randomBot = this.bots[Math.floor(Math.random() * this.bots.length)];
            const place = this.generateMockPlace(randomBot);
            this.places.push(place);

            // Update bot progress
            randomBot.extractedCount++;
            randomBot.progress = Math.min((counter / maxPlaces) * 100, 100);

            // Update campaign
            this.activeCampaign.totalExtracted = this.places.length;
            this.activeCampaign.progress = Math.min((counter / maxPlaces) * 100, 100);

            counter++;
            this.notify();
        }, 2500);

        // Update bot screenshots/status every 1 second
        this.bots.forEach((bot, index) => {
            const botInterval = setInterval(() => {
                bot.screenshotUrl = this.generateMockScreenshot(bot);
                this.notify();
            }, 1000 + (index * 300));

            this.botIntervalIds.push(botInterval);
        });
    }

    stopExtraction() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }

        this.botIntervalIds.forEach(id => clearInterval(id));
        this.botIntervalIds = [];

        if (this.activeCampaign) {
            this.activeCampaign.status = CampaignStatus.COMPLETED;
            this.activeCampaign.completedAt = new Date();
            this.activeCampaign.progress = 100;
        }

        this.bots.forEach(bot => {
            bot.status = BotStatus.IDLE;
            bot.progress = 100;
        });

        this.notify();
    }

    generateMockPlace(bot) {
        const name = mockPlaceNames[Math.floor(Math.random() * mockPlaceNames.length)];
        const street = mockStreets[Math.floor(Math.random() * mockStreets.length)];
        const number = Math.floor(Math.random() * 9999) + 1;

        return {
            id: `place-${Date.now()}-${Math.random()}`,
            name: `${name} ${Math.floor(Math.random() * 100)}`,
            address: `${number} ${street}`,
            rating: (Math.random() * 2 + 3).toFixed(1),
            totalReviews: Math.floor(Math.random() * 500) + 10,
            status: PlaceStatus.EXTRACTED,
            extractedAt: new Date(),
            phone: this.generatePhone(),
            website: Math.random() > 0.5 ? `https://${name.toLowerCase().replace(/\s+/g, '')}.com` : null
        };
    }

    generatePhone() {
        return `+1 ${Math.floor(Math.random() * 900 + 100)}-${Math.floor(Math.random() * 900 + 100)}-${Math.floor(Math.random() * 9000 + 1000)}`;
    }

    generateMockScreenshot(bot) {
        // Generate a color based on bot number for visualization
        const colors = ['#6366F1', '#8B5CF6', '#EC4899', '#10B981', '#F59E0B'];
        const color = colors[bot.number - 1] || colors[0];

        // Return a data URL with a colored rectangle (simulating browser view)
        const canvas = document.createElement('canvas');
        canvas.width = 800;
        canvas.height = 600;
        const ctx = canvas.getContext('2d');

        // Background
        ctx.fillStyle = '#1A1A1A';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Colored overlay with opacity
        ctx.fillStyle = color + '40';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Simulate browser elements
        ctx.fillStyle = '#2A2A2A';
        ctx.fillRect(0, 0, canvas.width, 50);

        // URL bar
        ctx.fillStyle = '#1A1A1A';
        ctx.fillRect(50, 10, canvas.width - 100, 30);

        // Text
        ctx.fillStyle = '#E5E5E5';
        ctx.font = '14px Arial';
        ctx.fillText('maps.google.com', 60, 30);

        // Simulate content
        const time = Date.now();
        const y = (time % 3000) / 3000 * 200;
        ctx.fillStyle = color;
        ctx.fillRect(50, 100 + y, canvas.width - 100, 80);

        return canvas.toDataURL();
    }

    getCampaigns() {
        return this.campaigns;
    }

    getActiveCampaign() {
        return this.activeCampaign;
    }

    getBots() {
        return this.bots;
    }

    getPlaces() {
        return this.places;
    }
}

export const mockExtractionService = new MockExtractionService();
