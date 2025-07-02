import React, { useEffect } from 'react';
import { useReportStore } from '../../store/reportStore';

const OrdersSummaryReport: React.FC = () => {
  const { ordersSummary, isSummaryLoading, summaryError, fetchOrdersSummary } = useReportStore();

  useEffect(() => {
    fetchOrdersSummary();
  }, [fetchOrdersSummary]);

  if (isSummaryLoading) {
    return <p className="text-gray-600 dark:text-gray-300">Loading orders summary...</p>;
  }

  if (summaryError) {
    return <p className="text-red-500">Error loading orders summary: {summaryError}</p>;
  }

  if (!ordersSummary) {
    return <p className="text-gray-600 dark:text-gray-300">No summary data available.</p>;
  }

  return (
    <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6 mb-6">
      <h2 className="text-xl font-semibold text-gray-700 dark:text-gray-200 mb-4">Orders Summary</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-primary/10 dark:bg-primary/20 p-4 rounded-lg">
          <p className="text-sm text-gray-500 dark:text-gray-400">Total Orders</p>
          <p className="text-3xl font-bold text-primary">{ordersSummary.total_orders}</p>
        </div>
      </div>

      <div className="mt-6">
        <h3 className="text-lg font-medium text-gray-700 dark:text-gray-200 mb-3">Orders by Status</h3>
        {ordersSummary.orders_by_status && ordersSummary.orders_by_status.length > 0 ? (
          <ul className="space-y-2">
            {ordersSummary.orders_by_status.map((item) => (
              <li
                key={item.status}
                className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-md"
              >
                <span className="text-gray-600 dark:text-gray-300">{item.status}</span>
                <span className="font-semibold text-gray-800 dark:text-gray-100">{item.count}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-500 dark:text-gray-400">No status data available.</p>
        )}
      </div>
    </div>
  );
};

export default OrdersSummaryReport;
