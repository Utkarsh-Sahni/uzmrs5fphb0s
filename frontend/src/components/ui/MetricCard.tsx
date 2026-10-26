import { Card, CardContent } from './Card';

interface MetricCardProps {
  label: string;
  value: string | number;
  description?: string;
  trend?: 'up' | 'down' | 'neutral';
}

export const MetricCard = ({ label, value, description, trend }: MetricCardProps) => (
  <Card className="flex-1 min-w-[200px]">
    <CardContent className="p-6">
      <p className="text-sm font-medium text-slate-400">{label}</p>
      <div className="flex items-baseline gap-2 mt-2">
        <span className="text-3xl font-bold text-slate-100">{value}</span>
        {trend && (
          <span className={`text-xs font-medium ${trend === 'up' ? 'text-emerald-400' : trend === 'down' ? 'text-rose-400' : 'text-slate-400'}`}>
            {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'}
          </span>
        )}
      </div>
      {description && <p className="text-xs text-slate-500 mt-1">{description}</p>}
    </CardContent>
  </Card>
);
