import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchAccuracy, fetchIntervalErrors } from '../api/client';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { MetricCard } from '../components/ui/MetricCard';
import { Input } from '../components/ui/Input';
import { AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';

interface ForecastAccuracyProps {
  date: string;
  setDate: (date: string) => void;
  cutoff: string;
  setCutoff: (cutoff: string) => void;
}

export const ForecastAccuracy = ({ date, setDate, cutoff, setCutoff }: ForecastAccuracyProps) => {
  const [editDate, setEditDate] = useState(date);
  const [editCutoff, setEditCutoff] = useState(cutoff);

  const { data: metrics, isLoading: loadingMetrics, error: errorMetrics, isFetching: fetchingMetrics } = useQuery({
    queryKey: ['accuracy', date, cutoff],
    queryFn: () => fetchAccuracy(date, cutoff),
    enabled: !!date && !!cutoff,
  });

  const { data: intervals, isLoading: loadingIntervals, error: errorIntervals } = useQuery({
    queryKey: ['intervals', date, cutoff],
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
        <div className="text-xs text-slate-500 italic pb-2">
          Evaluates forecasts as they existed at the cutoff.
        </div>
      </div>

      <div className="relative min-h-[600px]">
        {/* 1. Initial Load: Full screen loader (Priority 1) */}
        {loadingMetrics || loadingIntervals ? (
          <div className="flex flex-col items-center justify-center h-[600px] text-center">
            <Loader2 className="w-12 h-12 text-brand-500 animate-spin mb-4" />
            <p className="text-slate-400">Analyzing historical forecasts...</p>
          </div>
        ) : errorMetrics || errorIntervals ? (
          /* 2. Error State (Priority 2) */
          <div className="flex flex-col items-center justify-center h-[600px] text-center">
            <AlertCircle className="w-12 h-12 text-rose-500 mb-4" />
            <h3 className="text-xl font-semibold text-slate-100">No Data Found</h3>
            <p className="text-slate-400 max-w-md mt-2">
              No data available for the selected date and cutoff. Please try a different date.
            </p>
          </div>
        ) : metrics ? (
          /* 3. Data View (Priority 3) */
          <div className="space-y-8">
            {/* Background update loader: only shown when we already have data and are refetching */}
            {fetchingMetrics && (
              <div className="absolute inset-0 z-10 bg-slate-950/40 backdrop-blur-[1px] flex items-center justify-center pointer-events-none">
                <div className="flex items-center gap-3 bg-slate-900 border border-slate-800 px-4 py-2 rounded-full shadow-xl">
                  <Loader2 className="w-4 h-4 text-brand-500 animate-spin" />
                  <span className="text-sm text-slate-300 font-medium">Updating data...</span>
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <MetricCard
                label="MAE"
                value={`${metrics.mae.toFixed(2)} MW`}
                description="Mean Absolute Error: The average magnitude of the errors. Tells you the typical 'miss' distance regardless of direction."
              />
              <MetricCard
                label="RMSE"
                value={`${metrics.rmse.toFixed(2)} MW`}
                description="Root Mean Square Error: Penalizes larger errors more heavily. A high RMSE compared to MAE indicates a few very large misses."
              />
              <MetricCard
                label="Bias"
                value={`${metrics.bias.toFixed(2)} MW`}
                description="Forecast Bias: Average error. Negative values mean the forecast is consistently too high (over-forecasting), positive means too low."
              />
              <MetricCard
                label="WAPE"
                value={`${(metrics.wape * 100).toFixed(2)}%`}
                description="Weighted Absolute Percentage Error: Normalizes error relative to total generation. Best for comparing accuracy across different days."
              />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <Card className="lg:col-span-2">
                <CardHeader>
                  <CardTitle>Interval Breakdown</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                      <thead className="text-slate-400 border-b border-slate-800">
                        <tr>
                          <th className="pb-3 font-medium">Period</th>
                          <th className="pb-3 font-medium">Actual (MW)</th>
                          <th className="pb-3 font-medium">Forecast (MW)</th>
                          <th className="pb-3 font-medium">Error (MW)</th>
                          <th className="pb-3 font-medium">Published At</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800">
                        {intervals?.map((row: any) => (
                          <tr key={row.period} className="group hover:bg-slate-800/50 transition-colors">
                            <td className="py-3 font-medium text-slate-300">{row.period}</td>
                            <td className="py-3 text-slate-400">{row.actual ?? 'N/A'}</td>
                            <td className="py-3 text-slate-400">{row.forecast ?? 'N/A'}</td>
                            <td className={`py-3 font-medium ${row.error > 0 ? 'text-emerald-400' : row.error < 0 ? 'text-rose-400' : 'text-slate-400'}`}>
                              {row.error?.toFixed(1) ?? 'N/A'}
                            </td>
                            <td className="py-3 text-xs text-slate-500">{row.publish_time ?? 'N/A'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle>Metadata</CardTitle></CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex justify-between items-center py-2 border-b border-slate-800">
                    <span className="text-sm text-slate-400">Coverage</span>
                    <span className="text-sm font-semibold text-slate-100">{(metrics.coverage * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-slate-800">
                    <span className="text-sm text-slate-400">Samples</span>
                    <span className="text-sm font-semibold text-slate-100">{metrics.sample_count} / {metrics.metadata.target_intervals}</span>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-slate-800">
                    <span className="text-sm text-slate-400">Missing Data</span>
                    <span className="text-sm font-semibold text-rose-400">{metrics.missing_count}</span>
                  </div>
                  <div className="flex justify-between items-center py-2">
                    <span className="text-sm text-slate-400">Units</span>
                    <span className="text-sm font-semibold text-slate-100">{metrics.metadata.units}</span>
                  </div>
                  <div className="mt-6 p-4 bg-brand-900/20 rounded-lg border border-brand-800/50">
                    <div className="flex gap-2 items-start text-brand-400">
                      <CheckCircle2 className="w-4 h-4 mt-0.5 flex-shrink-0" />
                      <p className="text-xs leading-relaxed">
                        Forecasts selected are strictly prior to the decision cutoff of {metrics.metadata.decision_cutoff}.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
};
