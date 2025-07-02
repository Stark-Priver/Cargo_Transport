import React from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight, Truck, Package } from 'lucide-react';
import { Order } from '../../../types/order';
import { format } from 'date-fns';

interface RecentOrdersProps {
  orders: Order[];
}

const OrderStatusBadge: React.FC<{ status: Order['status'] }> = ({ status }) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'pending':
        return { color: 'bg-amber-100 text-amber-800', label: 'Pending' };
      case 'accepted':
        return { color: 'bg-blue-100 text-blue-800', label: 'Accepted' };
      case 'in_progress':
        return { color: 'bg-indigo-100 text-indigo-800', label: 'In Progress' };
      case 'in_transit':
        return { color: 'bg-purple-100 text-purple-800', label: 'In Transit' };
      case 'delivered':
        return { color: 'bg-green-100 text-green-800', label: 'Delivered' };
      case 'cancelled':
        return { color: 'bg-red-100 text-red-800', label: 'Cancelled' };
      default:
        return { color: 'bg-gray-100 text-gray-800', label: 'Unknown' };
    }
  };
  
  const { color, label } = getStatusConfig();
  
  return (
    <span className={`px-2.5 py-0.5 text-xs font-medium rounded-full ${color}`}>
      {label}
    </span>
  );
};

const RecentOrders: React.FC<RecentOrdersProps> = ({ orders }) => {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead className="bg-gray-50 dark:bg-gray-700">
          <tr>
            <th scope="col\" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300">
              Order ID
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300">
              Crop
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300">
              Route
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300">
              Status
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300">
              Date
            </th>
            <th scope="col" className="relative px-6 py-3">
              <span className="sr-only">View</span>
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200 dark:bg-gray-800 dark:divide-gray-700">
          {orders.map((order) => (
            <tr key={order.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center">
                  <Package size={16} className="text-gray-500 mr-2" />
                  <div className="text-sm font-medium text-gray-900 dark:text-white">{order.trackNumber}</div>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-900 dark:text-white">{order.crop}</div>
                <div className="text-xs text-gray-500 dark:text-gray-400">{order.quantity} bags</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-900 dark:text-white">
                  {order.pickupLocation.name} → {order.destinationLocation.name}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {order.pickupLocation.region}
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <OrderStatusBadge status={order.status} />
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {format(new Date(order.createdAt), 'dd MMM yyyy')}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <Link
                  to={`/orders/${order.id}`}
                  className="text-primary hover:text-primary-dark flex items-center justify-end"
                >
                  View
                  <ChevronRight size={16} className="ml-1" />
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default RecentOrders;