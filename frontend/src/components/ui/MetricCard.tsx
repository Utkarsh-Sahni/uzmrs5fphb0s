import React from 'react';
import { Card, CardContent } from './Card';
import { HelpCircle } from 'lucide-react';

interface MetricCardProps {
  label: string;
  value: string | number;
  description?: string;
  trend?: 'up' | 'down' | 'neutral';
}

export const MetricCard = ({ label, value, description, trend }: MetricCardProps) => {
  return (
    <Card className="flex-1 min-w-[200px]">
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-2">
          <p className="text-sm font-medium text-slate-400">{label}</p>
          <div className="relative group">
            <HelpCircle className="w-3.5 h-3.5 text-slate-500 cursor-help" />
            {description && (
              <div className="absolute bottom-full right-0 mb-2 w-48 p-2 bg-slate-800 text-slate-200 text-[10px] rounded shadow-xl border border-slate-700 z-50 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                {description}
              </div>
            )}
          </div>
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-bold text-slate-100">{value}</span>
          {trend && (
            <span className={`text-xs font-medium ${trend === 'up' ? 'text-emerald-400' : trend === 'down' ? 'text-rose-400' : 'text-slate-400'}`}>
              {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'}
            </span>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
