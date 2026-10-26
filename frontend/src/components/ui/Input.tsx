import React from 'react';

export const Input = ({ className = "", ...props }: React.InputHTMLAttributes<HTMLInputElement>) => (
  <input 
    className={`bg-slate-950 border border-slate-800 text-slate-100 px-3 py-2 rounded-md focus:outline-none focus:ring-2 focus:ring-brand-500 transition-all ${className}`} 
    {...props} 
  />
);
