import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: number;
  change: number;
  icon: React.ReactNode;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, change, icon }) => {
  const isPositive = change >= 0;
  
  return (
    <div className="bg-white p-6 rounded-lg shadow-sm transition-all duration-300 hover:shadow-md dark:bg-gray-800">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{title}</p>
          <p className="mt-1 text-2xl font-semibold text-gray-900 dark:text-white">{value}</p>
        </div>
        <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
          {icon}
        </div>
      </div>
      
      <div className="mt-4 flex items-center">
        <span className={`inline-flex items-center text-sm ${isPositive ? 'text-green-600' : 'text-red-600'} dark:text-green-400 dark:text-red-400`}>
          {isPositive ? (
            <>
              <TrendingUp size={16} className="mr-1" />
              <span>+{change}%</span>
            </>
          ) : (
            <>
              <TrendingDown size={16} className="mr-1" />
              <span>{change}%</span>
            </>
          )}
        </span>
        <span className="ml-2 text-sm text-gray-500 dark:text-gray-400">vs last month</span>
      </div>
    </div>
  );
};

export default StatCard;