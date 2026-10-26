import React from 'react';

export const Card = ({ children, className = "" }: { children: React.ReactNode, className?: string }) => (
  <div className={`bg-slate-900 border border-slate-800 rounded-xl ${className}`}>
    {children}
  </div>
);

export const CardHeader = ({ children, className = "" }: { children: React.ReactNode, className?: string }) => (
  <div className={`p-6 border-b border-slate-800 ${className}`}>
    {children}
  </div>
);

export const CardTitle = ({ children, className = "" }: { children: React.ReactNode, className?: string }) => (
  <h3 className={`text-lg font-semibold text-slate-100 ${className}`}>
    {children}
  </h3>
);

export const CardContent = ({ children, className = "" }: { children: React.ReactNode, className?: string }) => (
  <div className={`p-6 ${className}`}>
    {children}
  </div>
);
