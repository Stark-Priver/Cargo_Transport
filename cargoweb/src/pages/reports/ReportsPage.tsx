import React from 'react';
import OrdersSummaryReport from './OrdersSummaryReport';
import OrdersOverTimeReport from './OrdersOverTimeReport';

const ReportsPage: React.FC = () => {
  return (
    <div className="p-4 md:p-6 space-y-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold text-gray-800 dark:text-white">
          Reports Dashboard
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Overview of order activities and trends.
        </p>
      </div>

      <OrdersSummaryReport />
      <OrdersOverTimeReport />

    </div>
  );
};

export default ReportsPage;
