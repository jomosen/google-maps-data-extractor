import React, { useState } from 'react';
import { useAppStore } from '../../store/appStore';
import { Button } from '../components/Button';
import {
    ArrowLeft,
    ChevronLeft,
    ChevronRight,
    CheckCircle2,
    Clock,
    MapPin,
    Star,
    Phone,
    Globe
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const MonitorView = () => {
    const { activeCampaign, bots, places, setView } = useAppStore();
    const [selectedBotId, setSelectedBotId] = useState(null);
    const [leftPanelCollapsed, setLeftPanelCollapsed] = useState(false);

    React.useEffect(() => {
        if (bots.length > 0 && !selectedBotId) {
            setSelectedBotId(bots[0].id);
        }
    }, [bots, selectedBotId]);

    if (!activeCampaign) {
        return (
            <div className="min-h-screen bg-dark-bg flex items-center justify-center">
                <div className="text-center">
                    <p className="text-gray-400 mb-4">No active campaign</p>
                    <Button onClick={() => setView('dashboard')}>
                        Go to Dashboard
                    </Button>
                </div>
            </div>
        );
    }

    const selectedBot = bots.find(b => b.id === selectedBotId);

    return (
        <div className="h-screen bg-dark-bg flex flex-col overflow-hidden">
            {/* Header */}
            <header className="border-b border-dark-border bg-dark-surface px-6 py-4 flex-shrink-0">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => setView('dashboard')}
                            className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
                        >
                            <ArrowLeft size={20} />
                        </button>
                        <div>
                            <h1 className="text-xl font-bold text-white">{activeCampaign.title}</h1>
                            <p className="text-sm text-gray-400">
                                {activeCampaign.activity} in {activeCampaign.geography.countryName}
                            </p>
                        </div>
                    </div>

                    {/* Progress Circle */}
                    <div className="flex items-center gap-6">
                        <div className="text-right">
                            <div className="text-2xl font-bold text-white">
                                {places.length}
                            </div>
                            <div className="text-xs text-gray-400">Places Extracted</div>
                        </div>

                        <div className="relative w-20 h-20">
                            <svg className="transform -rotate-90 w-20 h-20">
                                <circle
                                    cx="40"
                                    cy="40"
                                    r="34"
                                    stroke="#1E1E1E"
                                    strokeWidth="6"
                                    fill="none"
                                />
                                <circle
                                    cx="40"
                                    cy="40"
                                    r="34"
                                    stroke="#6366F1"
                                    strokeWidth="6"
                                    fill="none"
                                    strokeDasharray={`${2 * Math.PI * 34}`}
                                    strokeDashoffset={`${2 * Math.PI * 34 * (1 - activeCampaign.progress / 100)}`}
                                    strokeLinecap="round"
                                    className="transition-all duration-500"
                                />
                            </svg>
                            <div className="absolute inset-0 flex items-center justify-center">
                                <span className="text-lg font-bold text-white">
                                    {Math.round(activeCampaign.progress)}%
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content - Split View */}
            <div className="flex-1 flex overflow-hidden">
                {/* Left Panel - Data & Logs */}
                <AnimatePresence mode="wait">
                    {!leftPanelCollapsed && (
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: '40%' }}
                            exit={{ width: 0 }}
                            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                            className="border-r border-dark-border bg-dark-surface flex flex-col overflow-hidden"
                        >
                            {/* Places Table */}
                            <div className="flex-1 overflow-y-auto">
                                <div className="p-4">
                                    <h2 className="text-lg font-semibold text-white mb-4">
                                        Extracted Places ({places.length})
                                    </h2>

                                    <div className="space-y-2">
                                        {places.map((place, index) => (
                                            <motion.div
                                                key={place.id}
                                                initial={{ opacity: 0, x: -20 }}
                                                animate={{ opacity: 1, x: 0 }}
                                                transition={{ delay: index * 0.02 }}
                                                className="bg-dark-hover border border-dark-border rounded-lg p-3 hover:border-primary transition-colors"
                                            >
                                                <div className="flex items-start justify-between gap-2">
                                                    <div className="flex-1 min-w-0">
                                                        <h3 className="font-medium text-white truncate">
                                                            {place.name}
                                                        </h3>
                                                        <div className="flex items-center gap-2 text-xs text-gray-400 mt-1">
                                                            <MapPin size={12} />
                                                            <span className="truncate">{place.address}</span>
                                                        </div>
                                                        {place.rating && (
                                                            <div className="flex items-center gap-2 mt-1">
                                                                <div className="flex items-center gap-1 text-yellow-400 text-xs">
                                                                    <Star size={12} fill="currentColor" />
                                                                    <span>{place.rating}</span>
                                                                </div>
                                                                <span className="text-xs text-gray-500">
                                                                    ({place.totalReviews} reviews)
                                                                </span>
                                                            </div>
                                                        )}
                                                        <div className="flex items-center gap-3 mt-2 text-xs">
                                                            {place.phone && (
                                                                <div className="flex items-center gap-1 text-gray-400">
                                                                    <Phone size={12} />
                                                                    <span>{place.phone}</span>
                                                                </div>
                                                            )}
                                                            {place.website && (
                                                                <div className="flex items-center gap-1 text-gray-400">
                                                                    <Globe size={12} />
                                                                    <span className="truncate">Website</span>
                                                                </div>
                                                            )}
                                                        </div>
                                                    </div>
                                                    <CheckCircle2 size={16} className="text-green-400 flex-shrink-0" />
                                                </div>
                                            </motion.div>
                                        ))}
                                    </div>

                                    {places.length === 0 && (
                                        <div className="text-center py-12 text-gray-500">
                                            <Clock size={32} className="mx-auto mb-2 opacity-50" />
                                            <p>Waiting for extraction to start...</p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Toggle Button */}
                <button
                    onClick={() => setLeftPanelCollapsed(!leftPanelCollapsed)}
                    className="absolute left-[40%] top-1/2 -translate-y-1/2 -translate-x-1/2 z-10
                     bg-dark-surface border border-dark-border rounded-full p-2
                     hover:bg-dark-hover transition-colors shadow-lg"
                    style={{ left: leftPanelCollapsed ? '0' : '40%' }}
                >
                    {leftPanelCollapsed ? (
                        <ChevronRight size={20} className="text-gray-400" />
                    ) : (
                        <ChevronLeft size={20} className="text-gray-400" />
                    )}
                </button>

                {/* Right Panel - Browser Viewports */}
                <div className="flex-1 bg-dark-bg flex flex-col overflow-hidden">
                    {/* Bot Tabs */}
                    <div className="border-b border-dark-border bg-dark-surface flex gap-1 px-4 overflow-x-auto">
                        {bots.map((bot) => (
                            <button
                                key={bot.id}
                                onClick={() => setSelectedBotId(bot.id)}
                                className={`px-4 py-3 text-sm font-medium transition-colors whitespace-nowrap
                  ${selectedBotId === bot.id
                                        ? 'text-white border-b-2 border-primary'
                                        : 'text-gray-400 hover:text-white'
                                    }`}
                            >
                                Bot #{bot.number}
                                {bot.status === 'running' && (
                                    <span className="ml-2 inline-block w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                                )}
                            </button>
                        ))}
                    </div>

                    {/* Browser Viewport */}
                    <div className="flex-1 p-6 overflow-hidden">
                        {selectedBot && (
                            <div className="h-full bg-dark-surface border border-dark-border rounded-lg overflow-hidden flex flex-col">
                                {/* Browser Info Bar */}
                                <div className="bg-dark-hover px-4 py-3 border-b border-dark-border">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <div className="text-sm font-medium text-white">
                                                Bot #{selectedBot.number}
                                            </div>
                                            <div className="text-xs text-gray-400 mt-0.5">
                                                Extracting {selectedBot.currentActivity} in {selectedBot.currentLocation} - {Math.round(selectedBot.progress)}%
                                            </div>
                                        </div>
                                        <div className="text-xs text-gray-400">
                                            {selectedBot.extractedCount} places extracted
                                        </div>
                                    </div>
                                </div>

                                {/* Browser Content */}
                                <div className="flex-1 bg-dark-bg flex items-center justify-center p-4">
                                    {selectedBot.screenshotUrl ? (
                                        <img
                                            src={selectedBot.screenshotUrl}
                                            alt={`Bot ${selectedBot.number} viewport`}
                                            className="max-w-full max-h-full object-contain rounded border border-dark-border"
                                        />
                                    ) : (
                                        <div className="text-center text-gray-500">
                                            <Clock size={48} className="mx-auto mb-4 opacity-30" />
                                            <p>Initializing browser...</p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};
