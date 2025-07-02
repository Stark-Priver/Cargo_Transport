import React, { useEffect, useState } from 'react';
import { Truck, Package, TrendingUp, TrendingDown, AlertCircle, CheckCircle } from 'lucide-react';
import { useOrderStore } from '../../store/orderStore';
import { useTransporterStore } from '../../store/transporterStore';
import StatCard from './components/StatCard';
import OrderStatusChart from './components/OrderStatusChart';
import RecentOrders from './components/RecentOrders';
import TopTransporters from './components/TopTransporters';

const Dashboard: React.FC = () => {
  const { orders, fetchOrders } = useOrderStore();
  const { transporters, fetchTransporters } = useTransporterStore();
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    const loadData = async () => {
      await Promise.all([fetchOrders(), fetchTransporters()]);
      setIsLoading(false);
    };
    
    loadData();
  }, [fetchOrders, fetchTransporters]);
  
  // Calculate statistics
  const totalOrders = orders.length;
  const pendingOrders = orders.filter(order => order.status === 'pending').length;
  const inTransitOrders = orders.filter(order => order.status === 'in_transit').length;
  const completedOrders = orders.filter(order => order.status === 'delivered').length;
  
  // Calculate percentage change (simulated for demo)
  const getRandomChange = () => Math.floor(Math.random() * 30) - 10;
  const ordersChange = getRandomChange();
  const transportersChange = getRandomChange();
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="flex flex-col items-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-300">Loading dashboard data...</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="animate-fade-in space-y-6">
      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Orders"
          value={totalOrders}
          change={ordersChange}
          icon={<Package className="text-blue-500" />}
        />
        
        <StatCard
          title="Pending Orders"
          value={pendingOrders}
          change={getRandomChange()}
          icon={<AlertCircle className="text-amber-500" />}
        />
        
        <StatCard
          title="In Transit"
          value={inTransitOrders}
          change={getRandomChange()}
          icon={<Truck className="text-indigo-500" />}
        />
        
        <StatCard
          title="Completed Orders"
          value={completedOrders}
          change={getRandomChange()}
          icon={<CheckCircle className="text-green-500" />}
        />
      </div>
      
      {/* Charts and Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-white p-6 rounded-lg shadow-sm dark:bg-gray-800">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-medium text-gray-900 dark:text-white">Order Status Overview</h2>
              <select className="text-sm border border-gray-300 rounded-md p-1 dark:bg-gray-700 dark:border-gray-600 dark:text-white">
                <option value="week">This Week</option>
                <option value="month">This Month</option>
                <option value="year">This Year</option>
              </select>
            </div>
            <OrderStatusChart orders={orders} />
          </div>
        </div>
        
        <div>
          <div className="bg-white p-6 rounded-lg shadow-sm h-full dark:bg-gray-800">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-medium text-gray-900 dark:text-white">Top Transporters</h2>
              <button className="text-sm text-primary hover:underline">View All</button>
            </div>
            <TopTransporters transporters={transporters.slice(0, 5)} />
          </div>
        </div>
      </div>
      
      {/* Recent Orders */}
      <div className="bg-white p-6 rounded-lg shadow-sm dark:bg-gray-800">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white">Recent Orders</h2>
          <button className="text-sm text-primary hover:underline">View All Orders</button>
        </div>
        <RecentOrders orders={orders.slice(0, 5)} />
      </div>
    </div>
  );
};

export default Dashboard;