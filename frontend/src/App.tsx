import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Activity, LineChart, BrainCircuit } from 'lucide-react';
import { ForecastExplorer } from './views/ForecastExplorer';
import { ForecastAccuracy } from './views/ForecastAccuracy';
import { DecisionInsights } from './views/DecisionInsights';

const queryClient = new QueryClient();

type View = 'explorer' | 'accuracy' | 'insights';

function App() {
  // Default date changed to January 2026 as per assignment requirements
  const [date, setDate] = useState('2026-01-15');
  const [cutoff, setCutoff] = useState('2026-01-14T11:00');
  const [currentView, setCurrentView] = useState<View>('accuracy');

  const navItems = [
    { id: 'explorer', label: 'Forecast Explorer', icon: LineChart },
    { id: 'accuracy', label: 'Forecast Accuracy', icon: Activity },
    { id: 'insights', label: 'Decision Insights', icon: BrainCircuit },
  ] as const;

  return (
    <QueryClientProvider client={queryClient}>
      <div className="flex h-screen bg-slate-950 text-slate-50 font-sans">
        {/* Sidebar */}
        <aside className="w-64 border-r border-slate-800 bg-slate-900 flex flex-col">
          <div className="p-6 border-b border-slate-800 flex items-center gap-3">
            <div className="w-8 h-8 bg-brand-500 rounded-lg flex items-center justify-center font-bold text-white">W</div>
            <span className="text-xl font-bold tracking-tight">WindSight</span>
          </div >
          
          <nav className="flex-1 p-4 space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentView === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setCurrentView(item.id)}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-md transition-all ${
                    isActive 
                      ? 'bg-brand-600 text-white shadow-lg shadow-brand-600/20' 
                      : 'text-slate-400 hover:bg-slate-800 hover:text-slate-100'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="text-sm font-medium">{item.label}</span>
                </button>
              );
            })}
          </nav>

          <div className="p-4 border-t border-slate-800 text-xs text-slate-500 text-center">
            WindSight Pilot v1.0 <br/> UK Energy Utility
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto">
          <header className="h-16 border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm flex items-center justify-between px-8 sticky top-0 z-10">
            <h1 className="text-lg font-medium text-slate-100">
              {navItems.find(i => i.id === currentView)?.label}
            </h1>
            <div className="flex items-center gap-4">
              <div className="text-xs text-slate-400 bg-slate-800 px-2 py-1 rounded border border-slate-700">
                Environment: Production Pilot
              </div>
            </div>
          </header>
          
          <div className="max-w-7xl mx-auto">
            {currentView === 'explorer' && (
              <ForecastExplorer date={date} setDate={setDate} cutoff={cutoff} setCutoff={setCutoff} />
            )}
            {currentView === 'accuracy' && (
              <ForecastAccuracy date={date} setDate={setDate} cutoff={cutoff} setCutoff={setCutoff} />
            )}
            {currentView === 'insights' && (
              <DecisionInsights date={date} setDate={setDate} cutoff={cutoff} setCutoff={setCutoff} />
            )}
          </div>
        </main>
      </div>
    </QueryClientProvider>
  );
}

export default App;
