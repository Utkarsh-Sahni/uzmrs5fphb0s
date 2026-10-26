import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchIntervalErrors } from '../api/client';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Input } from '../components/ui/Input';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Loader2, AlertCircle } from 'lucide-react';

interface ForecastExplorerProps {
  date: string;
  setDate: (date: string) => void;
  cutoff: string;
  setCutoff: (cutoff: string) => void;
}

export const ForecastExplorer = ({ date, setDate, cutoff, setCutoff }: ForecastExplorerProps) => {
  const [editDate, setEditDate] = useState(date);
  const [editCutoff, setEditCutoff] = useState(cutoff);

  const { data: intervals, isLoading, error, isFetching } = useQuery({
    queryKey: ['explorer', date, cutoff],
    queryFn: () => fetchIntervalErrors(date, cutoff),
    enabled: !!date && !!cutoff,
  });

  const handleBlur = () => {
    setDate(editDate);
    setCutoff(editCutoff);
  };

  return (
    <div className="space-y-8 p-6 relative">
      <div className="flex flex-col md:flex-row gap-4 items-end">
        <div className="space-y-2">
          <label className="text-xs font-medium text-slate-400 uppercase">Target Date</label>
          <Input 
            type="date" 
            value={editDate} 
            onChange={(e) => setEditDate(e.target.value)} 
            onBlur={handleBlur}
            className="w-48" 
          />
        </div>
        <div className="space-y-2">
          <label className="text-xs font-medium text-slate-400 uppercase">Decision Cutoff</label>
          <Input 
            type="datetime-local" 
            value={editCutoff} 
            onChange={(e) => setEditCutoff(e.target.value)} 
            onBlur={handleBlur}
            className="w-64" 
          />
        </div>
      </div>

      <div className="relative min-h-[400px]">
        {/* Overlay loader for updates */}
        {isFetching && intervals && (
          <div className="absolute inset-0 z-10 bg-slate-950/40 backdrop-blur-[1px] flex items-center justify-center pointer-events-none">
            <div className="flex items-center gap-3 bg-slate-900 border border-slate-800 px-4 py-2 rounded-full shadow-xl">
              <Loader2 className="w-4 h-4 text-brand-500 animate-spin" />
              <span className="text-sm text-slate-300 font-medium">Updating profile...</span>
            </div>
          </div>
        )}

        {isLoading ? (
          <div className="flex flex-col items-center justify-center h-[400px] text-center">
            <Loader2 className="w-12 h-12 text-brand-500 animate-spin mb-4" />
            <p className="text-slate-400">Loading generation profiles...</p>
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center h-[400px] text-center">
            <AlertCircle className="w-12 h-12 text-rose-500 mb-4" />
            <h3 className="text-xl font-semibold text-slate-100">Data Fetch Error</h3>
            <p className="text-slate-400 max-w-md mt-2">Unable to load time-series data. Check parameters.</p>
          </div>
        ) : (
          <Card>
            <CardHeader>
              <CardTitle>Generation Profile: Actual vs Forecast</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[400px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={intervals}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis 
                      dataKey="period" 
                      stroke="#94a3b8" 
                      fontSize={12} 
                      tickLine={false} 
                      axisLine={false} 
                      label={{ value: 'Settlement Period', position: 'insideBottom', offset: -5, fill: '#94a3b8', fontSize: 12 }}
                    />
                    <YAxis 
                      stroke="#94a3b8" 
                      fontSize={12} 
                      tickLine={false} 
                      axisLine={false} 
                      label={{ value: 'MW', angle: -90, position: 'insideLeft', fill: '#94a3b8', fontSize: 12 }}
                    />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#f1f5f9' }}
                      itemStyle={{ color: '#f1f5f9' }}
                    />
                    <Legend verticalAlign="top" height={36} />
                    <Line 
                      type="monotone" 
                      dataKey="actual" 
                      name="Actual Generation" 
                      stroke="#38bdf8" 
                      strokeWidth={2} 
                      dot={{ r: 3 }} 
                      activeDot={{ r: 5 }} 
                    />
                    <Line 
                      type="monotone" 
                      dataKey="forecast" 
                      name="As-Of Forecast" 
                      stroke="#94a3b8" 
                      strokeWidth={2} 
                      strokeDasharray="5 5" 
                      dot={{ r: 3 }} 
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};
