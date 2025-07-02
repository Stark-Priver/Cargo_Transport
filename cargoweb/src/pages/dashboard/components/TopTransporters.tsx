import React from 'react';
import { Star, TrendingUp } from 'lucide-react';
import { Transporter } from '../../../types/transporter';

interface TopTransportersProps {
  transporters: Transporter[];
}

const TopTransporters: React.FC<TopTransportersProps> = ({ transporters }) => {
  return (
    <div className="space-y-4">
      {transporters.map((transporter) => (
        <div 
          key={transporter.id}
          className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors dark:hover:bg-gray-700/50"
        >
          <div className="h-10 w-10 rounded-full overflow-hidden flex-shrink-0">
            {transporter.avatarUrl ? (
              <img 
                src={transporter.avatarUrl} 
                alt={transporter.name}
                className="h-full w-full object-cover" 
              />
            ) : (
              <div className="bg-primary h-full w-full flex items-center justify-center text-white">
                {transporter.name.charAt(0)}
              </div>
            )}
          </div>
          
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
              {transporter.name}
            </p>
            <div className="flex items-center mt-1">
              <Star size={14} className="text-yellow-400" />
              <span className="text-xs text-gray-500 ml-1 dark:text-gray-400">
                {transporter.rating}
              </span>
              <span className="mx-2 text-gray-300 dark:text-gray-600">|</span>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {transporter.completedOrders} orders
              </span>
            </div>
          </div>
          
          <div className="text-right">
            <p className="text-sm font-medium text-gray-900 dark:text-white">
              {new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'TZS',
                maximumFractionDigits: 0,
              }).format(transporter.totalEarnings)}
            </p>
            <div className="flex items-center justify-end mt-1">
              <TrendingUp size={14} className="text-green-500 mr-1" />
              <span className="text-xs text-green-600 dark:text-green-400">
                {Math.floor(Math.random() * 20) + 5}%
              </span>
            </div>
          </div>
        </div>
      ))}
      
      <div className="pt-2 border-t border-gray-200 mt-4 dark:border-gray-700">
        <button className="text-sm text-center w-full text-primary hover:text-primary-dark py-2">
          See all transporters
        </button>
      </div>
    </div>
  );
};

export default TopTransporters;