/**
 * Real Extraction Service - WebSocket client for backend integration
 */

export class RealExtractionService {
    constructor() {
        this.ws = null;
        this.subscribers = [];
        this.botsState = new Map(); // bot_id -> bot state
    }

    /**
     * Start extraction by connecting to backend WebSocket
     */
    async startExtraction(campaignId) {
        const wsUrl = `ws://localhost:8000/ws/extraction/stream`;

        console.log('🔌 Connecting to WebSocket:', wsUrl);

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('✅ WebSocket connected');
        };

        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            console.log('📨 WebSocket message:', message.type, message);

            this._handleMessage(message);
        };

        this.ws.onerror = (error) => {
            console.error('❌ WebSocket error:', error);
        };

        this.ws.onclose = () => {
            console.log('🔌 WebSocket closed');
        };
    }

    /**
     * Handle incoming WebSocket messages
     */
    _handleMessage(message) {
        switch (message.type) {
            case 'connection':
                console.log('Connected:', message.message);
                break;

            case 'bot_status':
                this._updateBotStatus(message);
                break;

            case 'bot_snapshot':
                this._updateBotSnapshot(message);
                break;

            case 'bot_error':
                console.error('Bot error:', message);
                this._updateBotError(message);
                break;

            default:
                console.warn('Unknown message type:', message.type);
        }
    }

    /**
     * Update bot status (initializing, idle, processing)
     */
    _updateBotStatus(message) {
        const { bot_id, status, task_id, message: statusMessage } = message.data;

        const botState = this.botsState.get(bot_id) || {
            id: bot_id,
            status: status,
            screenshot: null,
            currentUrl: null,
            taskId: task_id
        };

        botState.status = status;
        botState.taskId = task_id;

        this.botsState.set(bot_id, botState);

        this._notifySubscribers();
    }

    /**
     * Update bot screenshot
     */
    _updateBotSnapshot(message) {
        const { bot_id, screenshot, current_url, task_id } = message.data;

        const botState = this.botsState.get(bot_id) || {
            id: bot_id,
            status: 'processing',
            screenshot: null,
            currentUrl: null,
            taskId: task_id
        };

        botState.screenshot = screenshot;
        botState.currentUrl = current_url;
        botState.status = 'processing';

        this.botsState.set(bot_id, botState);

        this._notifySubscribers();
    }

    /**
     * Update bot error state
     */
    _updateBotError(message) {
        const { bot_id, error } = message.data;

        const botState = this.botsState.get(bot_id);
        if (botState) {
            botState.status = 'error';
            botState.error = error;
            this.botsState.set(bot_id, botState);
        }

        this._notifySubscribers();
    }

    /**
     * Subscribe to extraction updates
     */
    subscribe(callback) {
        this.subscribers.push(callback);
        return () => {
            this.subscribers = this.subscribers.filter(cb => cb !== callback);
        };
    }

    /**
     * Notify all subscribers with current state
     */
    _notifySubscribers() {
        const bots = Array.from(this.botsState.values()).map((bot, index) => ({
            id: bot.id,
            number: index + 1,
            status: bot.status,
            screenshotUrl: bot.screenshot ? `data:image/png;base64,${bot.screenshot}` : null,
            currentUrl: bot.currentUrl || '',
            currentActivity: 'restaurants',
            currentLocation: bot.currentUrl ? this._extractLocationFromUrl(bot.currentUrl) : 'Loading...',
            progress: bot.status === 'processing' ? 50 : bot.status === 'idle' ? 100 : 0,
            extractedCount: 0,
            taskId: bot.taskId
        }));

        const state = {
            bots: bots,
            places: [], // Empty for now
            progress: 0, // Calculate based on tasks later
            isRunning: bots.some(bot => bot.status === 'processing')
        };

        this.subscribers.forEach(callback => callback(state));
    }

    /**
     * Extract location name from Google Maps URL
     */
    _extractLocationFromUrl(url) {
        try {
            if (url.includes('maps/search/')) {
                const match = url.match(/search\/([^/]+)/);
                if (match) {
                    const query = decodeURIComponent(match[1].replace(/\+/g, ' '));
                    // Extract city name (after "in")
                    const inMatch = query.match(/in\s+([^,]+)/);
                    return inMatch ? inMatch[1] : query;
                }
            }
            return 'Unknown';
        } catch (e) {
            return 'Unknown';
        }
    }

    /**
     * Stop extraction
     */
    stopExtraction() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.botsState.clear();
    }
}

// Export singleton instance
export const realExtractionService = new RealExtractionService();
