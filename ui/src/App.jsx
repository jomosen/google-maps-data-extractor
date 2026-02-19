import React from 'react';
import { useAppStore } from './store/appStore';
import { DashboardView } from './presentation/views/DashboardView';
import { CreateCampaignView } from './presentation/views/CreateCampaignView';
import { MonitorView } from './presentation/views/MonitorView';
import { CampaignDetailView } from './presentation/views/CampaignDetailView';

function App() {
  const currentView = useAppStore((state) => state.currentView);

  return (
    <div className="app">
      {currentView === 'dashboard' && <DashboardView />}
      {currentView === 'create' && <CreateCampaignView />}
      {currentView === 'monitor' && <MonitorView />}
      {currentView === 'detail' && <CampaignDetailView />}
    </div>
  );
}

export default App;
