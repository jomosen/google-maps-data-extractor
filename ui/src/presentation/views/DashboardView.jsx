import { useEffect } from 'react';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { useAppStore } from '../../store/appStore';
import { Activity, TrendingUp, Bot, Wifi } from 'lucide-react';
import { motion } from 'framer-motion';

export const DashboardView = () => {
    const { license, campaigns, setView, loadCampaigns, selectCampaign } = useAppStore();

    useEffect(() => {
        loadCampaigns();
    }, []);

    const completedCampaigns = campaigns.filter(c => c.status === 'completed').length;
    const successRate = campaigns.length > 0
        ? ((completedCampaigns / campaigns.length) * 100).toFixed(0)
        : 0;

    const kpis = [
        {
            icon: TrendingUp,
            label: 'Total Extracted',
            value: '0',
            color: 'text-green-400'
        },
        {
            icon: Activity,
            label: 'Success Rate',
            value: `${successRate}%`,
            color: 'text-blue-400'
        },
        {
            icon: Bot,
            label: 'Active Bots',
            value: '0',
            color: 'text-purple-400'
        },
        {
            icon: Wifi,
            label: 'Proxy Health',
            value: '100%',
            color: 'text-emerald-400'
        }
    ];

    return (
        <div className="min-h-screen bg-dark-bg">
            {/* Header */}
            <header className="border-b border-dark-border bg-dark-surface">
                <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
                        <p className="text-sm text-gray-400 mt-1">
                            Monitor your extraction campaigns
                        </p>
                    </div>

                    {/* License Badge */}
                    <div className="flex items-center gap-4">
                        <div className="bg-dark-hover border border-dark-border rounded-lg px-4 py-2">
                            <div className="text-xs text-gray-400">License: {license.tier.toUpperCase()}</div>
                            <div className="text-sm font-medium text-white">
                                {license.usedExtractions.toLocaleString()} / {license.maxExtractions.toLocaleString()}
                            </div>
                            <div className="w-full bg-dark-border rounded-full h-1.5 mt-2">
                                <div
                                    className="bg-primary h-1.5 rounded-full transition-all"
                                    style={{ width: `${(license.usedExtractions / license.maxExtractions) * 100}%` }}
                                />
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-6 py-8">
                {/* KPI Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    {kpis.map((kpi, index) => (
                        <motion.div
                            key={kpi.label}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1 }}
                        >
                            <Card hover className="h-full">
                                <div className="flex items-center gap-4">
                                    <div className={`p-3 bg-dark-hover rounded-lg ${kpi.color}`}>
                                        <kpi.icon size={24} />
                                    </div>
                                    <div>
                                        <div className="text-sm text-gray-400">{kpi.label}</div>
                                        <div className="text-2xl font-bold text-white">{kpi.value}</div>
                                    </div>
                                </div>
                            </Card>
                        </motion.div>
                    ))}
                </div>

                {/* Recent Campaigns */}
                <Card>
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-xl font-semibold text-white">Recent Campaigns</h2>
                        <Button onClick={() => setView('create')}>
                            Create Campaign
                        </Button>
                    </div>

                    {campaigns.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-16">
                            <div className="inline-flex items-center justify-center w-16 h-16 bg-dark-hover rounded-full mb-4">
                                <Activity size={32} className="text-gray-500" />
                            </div>
                            <h3 className="text-lg font-medium text-white mb-2">
                                No campaigns yet
                            </h3>
                            <p className="text-gray-400 mb-6">
                                Create your first campaign to start extracting data
                            </p>
                            <Button onClick={() => setView('create')}>
                                Create First Campaign
                            </Button>
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead>
                                    <tr className="border-b border-dark-border">
                                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Title</th>
                                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Activity</th>
                                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Location</th>
                                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Status</th>
                                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Tasks</th>
                                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Date</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {campaigns.map((campaign, index) => (
                                        <motion.tr
                                            key={campaign.campaign_id}
                                            initial={{ opacity: 0, x: -20 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: index * 0.05 }}
                                            className="border-b border-dark-border hover:bg-dark-hover transition-colors cursor-pointer"
                                            onClick={() => selectCampaign(campaign)}
                                        >
                                            <td className="py-3 px-4 text-white font-medium">{campaign.title}</td>
                                            <td className="py-3 px-4 text-gray-300 capitalize">{campaign.activity}</td>
                                            <td className="py-3 px-4 text-gray-300">{campaign.location_name}</td>
                                            <td className="py-3 px-4">
                                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                                    campaign.status === 'completed'   ? 'bg-green-500/20 text-green-400' :
                                                    campaign.status === 'in_progress' ? 'bg-blue-500/20 text-blue-400' :
                                                    campaign.status === 'failed'      ? 'bg-red-500/20 text-red-400' :
                                                    campaign.status === 'archived'    ? 'bg-yellow-500/20 text-yellow-400' :
                                                                                        'bg-gray-500/20 text-gray-400'
                                                }`}>
                                                    {campaign.status.replace('_', ' ')}
                                                </span>
                                            </td>
                                            <td className="py-3 px-4 text-gray-300">{campaign.total_tasks}</td>
                                            <td className="py-3 px-4 text-gray-400 text-sm">
                                                {new Date(campaign.created_at).toLocaleDateString()}
                                            </td>
                                        </motion.tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </Card>
            </main>
        </div>
    );
};
