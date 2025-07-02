import React, { useEffect } from 'react';
import { useReportStore } from '../../store/reportStore';

const OrdersOverTimeReport: React.FC = () => {
  const { ordersOverTime, isOverTimeLoading, overTimeError, fetchOrdersOverTime } = useReportStore();

  useEffect(() => {
    fetchOrdersOverTime();
  }, [fetchOrdersOverTime]);

  if (isOverTimeLoading) {
    return <p className="text-gray-600 dark:text-gray-300">Loading orders over time data...</p>;
  }

  if (overTimeError) {
    return <p className="text-red-500">Error loading orders over time data: {overTimeError}</p>;
  }

  if (!ordersOverTime || ordersOverTime.length === 0) {
    return <p className="text-gray-600 dark:text-gray-300">No orders over time data available.</p>;
  }

  return (
    <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6">
      <h2 className="text-xl font-semibold text-gray-700 dark:text-gray-200 mb-4">Orders Over Time</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
              >
                Date
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
              >
                Number of Orders
              </th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {ordersOverTime.map((item) => (
              <tr key={item.order_date}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                  {item.order_date}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                  {item.count}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default OrdersOverTimeReport;
