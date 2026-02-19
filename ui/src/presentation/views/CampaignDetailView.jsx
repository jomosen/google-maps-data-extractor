import { useState } from 'react';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { useAppStore } from '../../store/appStore';
import { ArrowLeft, Play, RotateCcw, Archive, MapPin, CheckCircle, XCircle, Clock } from 'lucide-react';
import { motion } from 'framer-motion';

const STATUS_BADGE = {
    pending:     'bg-gray-500/20 text-gray-400',
    in_progress: 'bg-blue-500/20 text-blue-400',
    completed:   'bg-green-500/20 text-green-400',
    failed:      'bg-red-500/20 text-red-400',
    archived:    'bg-yellow-500/20 text-yellow-400',
    skipped:     'bg-orange-500/20 text-orange-400',
};

function StatusBadge({ status }) {
    return (
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${STATUS_BADGE[status] ?? STATUS_BADGE.pending}`}>
            {status.replace('_', ' ')}
        </span>
    );
}

function ProgressBar({ value }) {
    return (
        <div className="w-full bg-dark-border rounded-full h-2">
            <div
                className="bg-primary h-2 rounded-full transition-all duration-500"
                style={{ width: `${Math.min(value, 100)}%` }}
            />
        </div>
    );
}

export const CampaignDetailView = () => {
    const { selectedCampaign, campaignPlaces, campaignTasks, setView, campaignAction } = useAppStore();
    const [activeTab, setActiveTab] = useState('places');
    const [loading, setLoading] = useState(false);

    if (!selectedCampaign) return null;

    const c = selectedCampaign;
    const status = c.status;

    const handleAction = async (action) => {
        setLoading(true);
        await campaignAction(action, c.campaign_id);
        setLoading(false);
    };

    return (
        <div className="min-h-screen bg-dark-bg">
            {/* Header */}
            <header className="border-b border-dark-border bg-dark-surface">
                <div className="max-w-7xl mx-auto px-6 py-4 flex items-center gap-4">
                    <button
                        onClick={() => setView('dashboard')}
                        className="text-gray-400 hover:text-white transition-colors"
                    >
                        <ArrowLeft size={20} />
                    </button>
                    <div className="flex-1">
                        <h1 className="text-xl font-bold text-white">{c.title}</h1>
                        <p className="text-sm text-gray-400 mt-0.5 capitalize">
                            {c.activity} · {c.location_name}
                        </p>
                    </div>
                    <StatusBadge status={status} />
                </div>
            </header>

            <main className="max-w-7xl mx-auto px-6 py-8 space-y-6">
                {/* Master: campaign info */}
                <Card>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-6">
                        <Stat label="Total Tasks"     value={c.total_tasks} />
                        <Stat label="Completed"       value={c.completed_tasks ?? 0} icon={<CheckCircle size={16} className="text-green-400" />} />
                        <Stat label="Failed"          value={c.failed_tasks ?? 0}    icon={<XCircle size={16} className="text-red-400" />} />
                        <Stat label="Max Bots"        value={c.max_bots} />
                    </div>

                    {c.total_tasks > 0 && (
                        <div className="mb-6">
                            <div className="flex justify-between text-sm text-gray-400 mb-1">
                                <span>Progress</span>
                                <span>{c.completion_percentage ?? 0}%</span>
                            </div>
                            <ProgressBar value={c.completion_percentage ?? 0} />
                        </div>
                    )}

                    <div className="flex items-center gap-2 text-xs text-gray-500 mb-6">
                        <Clock size={12} />
                        <span>Created {new Date(c.created_at).toLocaleString()}</span>
                        {c.started_at && <><span>·</span><span>Started {new Date(c.started_at).toLocaleString()}</span></>}
                        {c.completed_at && <><span>·</span><span>Ended {new Date(c.completed_at).toLocaleString()}</span></>}
                    </div>

                    {/* Action buttons */}
                    <div className="flex items-center gap-3">
                        {status === 'pending' && (
                            <Button onClick={() => handleAction('start')} disabled={loading}>
                                <Play size={16} className="mr-2" /> Start
                            </Button>
                        )}
                        {status === 'failed' && (
                            <Button onClick={() => handleAction('resume')} disabled={loading}>
                                <RotateCcw size={16} className="mr-2" /> Resume
                            </Button>
                        )}
                        {(status === 'completed' || status === 'failed') && (
                            <Button
                                variant="secondary"
                                onClick={() => handleAction('archive')}
                                disabled={loading}
                            >
                                <Archive size={16} className="mr-2" /> Archive
                            </Button>
                        )}
                    </div>
                </Card>

                {/* Detail: tabs */}
                <div>
                    <div className="flex border-b border-dark-border mb-4">
                        {['places', 'tasks'].map(tab => (
                            <button
                                key={tab}
                                onClick={() => setActiveTab(tab)}
                                className={`px-6 py-3 text-sm font-medium transition-colors capitalize ${
                                    activeTab === tab
                                        ? 'text-white border-b-2 border-primary'
                                        : 'text-gray-400 hover:text-white'
                                }`}
                            >
                                {tab === 'places'
                                    ? `Places (${campaignPlaces.length})`
                                    : `Tasks (${campaignTasks.length})`}
                            </button>
                        ))}
                    </div>

                    {activeTab === 'places' && (
                        <Card>
                            {campaignPlaces.length === 0 ? (
                                <EmptyState icon={<MapPin size={32} />} message="No places extracted yet" />
                            ) : (
                                <div className="overflow-x-auto">
                                    <table className="w-full">
                                        <thead>
                                            <tr className="border-b border-dark-border">
                                                <Th>Name</Th>
                                                <Th>Category</Th>
                                                <Th>City</Th>
                                                <Th>Rating</Th>
                                                <Th>Phone</Th>
                                                <Th>Website</Th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {campaignPlaces.map((place, i) => (
                                                <motion.tr
                                                    key={place.place_id}
                                                    initial={{ opacity: 0 }}
                                                    animate={{ opacity: 1 }}
                                                    transition={{ delay: i * 0.02 }}
                                                    className="border-b border-dark-border hover:bg-dark-hover"
                                                >
                                                    <td className="py-2 px-4 text-white text-sm">{place.name ?? '—'}</td>
                                                    <td className="py-2 px-4 text-gray-400 text-sm">{place.category ?? '—'}</td>
                                                    <td className="py-2 px-4 text-gray-400 text-sm">{place.city ?? '—'}</td>
                                                    <td className="py-2 px-4 text-gray-400 text-sm">{place.rating != null ? `${place.rating} ★` : '—'}</td>
                                                    <td className="py-2 px-4 text-gray-400 text-sm">{place.phone ?? '—'}</td>
                                                    <td className="py-2 px-4 text-sm">
                                                        {place.website_link
                                                            ? <a href={place.website_link} target="_blank" rel="noreferrer" className="text-primary hover:underline truncate block max-w-[160px]">{place.website_link}</a>
                                                            : <span className="text-gray-600">—</span>}
                                                    </td>
                                                </motion.tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </Card>
                    )}

                    {activeTab === 'tasks' && (
                        <Card>
                            {campaignTasks.length === 0 ? (
                                <EmptyState icon={<Clock size={32} />} message="No tasks found" />
                            ) : (
                                <div className="overflow-x-auto">
                                    <table className="w-full">
                                        <thead>
                                            <tr className="border-b border-dark-border">
                                                <Th>Location</Th>
                                                <Th>Seed</Th>
                                                <Th>Status</Th>
                                                <Th>Attempts</Th>
                                                <Th>Last Error</Th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {campaignTasks.map((task, i) => (
                                                <motion.tr
                                                    key={task.task_id}
                                                    initial={{ opacity: 0 }}
                                                    animate={{ opacity: 1 }}
                                                    transition={{ delay: i * 0.02 }}
                                                    className="border-b border-dark-border hover:bg-dark-hover"
                                                >
                                                    <td className="py-2 px-4 text-white text-sm">{task.geoname_name}</td>
                                                    <td className="py-2 px-4 text-gray-400 text-sm capitalize">{task.search_seed}</td>
                                                    <td className="py-2 px-4"><StatusBadge status={task.status} /></td>
                                                    <td className="py-2 px-4 text-gray-400 text-sm">{task.attempts}</td>
                                                    <td className="py-2 px-4 text-red-400 text-xs max-w-[200px] truncate">{task.last_error ?? '—'}</td>
                                                </motion.tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </Card>
                    )}
                </div>
            </main>
        </div>
    );
};

function Stat({ label, value, icon }) {
    return (
        <div>
            <div className="text-xs text-gray-400 mb-1 flex items-center gap-1">{icon}{label}</div>
            <div className="text-2xl font-bold text-white">{value}</div>
        </div>
    );
}

function Th({ children }) {
    return <th className="text-left py-3 px-4 text-xs font-medium text-gray-400">{children}</th>;
}

function EmptyState({ icon, message }) {
    return (
        <div className="flex flex-col items-center justify-center py-12 text-gray-500">
            <div className="mb-3">{icon}</div>
            <p className="text-sm">{message}</p>
        </div>
    );
}
