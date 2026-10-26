import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchAccuracy } from '../api/client';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Input } from '../components/ui/Input';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Loader2 } from 'lucide-react';

interface DecisionInsightsProps {
  date: string;
  setDate: (date: string) => void;
  cutoff: string;
  setCutoff: (cutoff: string) => void;
}

export const DecisionInsights = ({ date, setDate, cutoff, setCutoff }: DecisionInsightsProps) => {
  const [editDate, setEditDate] = useState(date);
  const [editCutoff, setEditCutoff] = useState(cutoff);

  const cutoffs = [
    "2022-09-19T05:00",
    "2022-09-19T17:00",
    "2022-09-19T23:00",
    "2022-09-20T04:00",
  ];

  const { data: results, isLoading, error, isFetching } = useQuery({
    queryKey: ['insights', date],
    queryFn: async () => {
      const res = await Promise.all(
        cutoffs.map(async (cutoffVal) => {
          try {
            const acc = await fetchAccuracy(date, cutoffVal);
            return { cutoff: cutoffVal, mae: acc.mae };
          } catch {
            return { cutoff: cutoffVal, mae: null };
          }
        })
      );
      return res;
    },
    enabled: !!date,
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
        {isFetching && results && (
          <div className="absolute inset-0 z-10 bg-slate-950/40 backdrop-blur-[1px] flex items-center justify-center pointer-events-none">
            <div className="flex items-center gap-3 bg-slate-900 border border-slate-800 px-4 py-2 rounded-full shadow-xl">
              <Loader2 className="w-4 h-4 text-brand-500 animate-spin" />
              <span className="text-sm text-slate-300 font-medium">Calculating Convergence...</span>
            </div>
          </div>
        )}

        {isLoading ? (
          <div className="flex flex-col items-center justify-center h-[400px] text-center">
            <Loader2 className="w-12 h-12 text-brand-500 animate-spin mb-4" />
            <p className="text-slate-400">Computing decision insights...</p>
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center h-[400px] text-center">
            <div className="text-rose-500 text-lg">Error loading insights.</div>
          </div>
        ) : (
          <>
            <Card>
              <CardHeader>
                <CardTitle>Forecast Convergence (MAE over time)</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-[300px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={results}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                      <XAxis 
                        dataKey="cutoff" 
                        stroke="#94a3b8" 
                        fontSize={10} 
                        tickFormatter={(val) => val.split('T')[1]} 
                      />
                      <YAxis stroke="#94a3b8" fontSize={12} />
                      <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#f1f5f9' }} />
                      <Line type="monotone" dataKey="mae" stroke="#38bdf8" strokeWidth={3} dot={{ r: 6 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
              <Card>
                <CardHeader><CardTitle>Analyst Note</CardTitle></CardHeader>
                <CardContent className="text-sm text-slate-400 leading-relaxed">
                  The convergence chart shows how the forecast error (MAE) typically decreases as the decision cutoff approaches 
                  the delivery interval. In this dataset, we observe that moving the cutoff from 24h to 1h provides a 
                  significant reduction in absolute error, highlighting the value of late-stage updates.
                </CardContent>
              </Card>
              <Card>
                <CardHeader><CardTitle>System Behavior</CardTitle></CardHeader>
                <CardContent className="text-sm text-slate-400 leading-relaxed">
                  The "As-Of" selection logic ensures that only information available at that 
                  precise moment is used. This mimics the real-world constraint of a procurement analyst making 
                  purchasing decisions on the day-ahead market.
                </CardContent>
              </Card>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
