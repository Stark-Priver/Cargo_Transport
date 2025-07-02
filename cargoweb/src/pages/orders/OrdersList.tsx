import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Package, Filter, Download, Search, ChevronRight, ChevronDown } from 'lucide-react';
import { useOrderStore } from '../../store/orderStore';
import Button from '../../components/common/Button';
import { Order, OrderStatus } from '../../types/order';
import { format } from 'date-fns';

const OrdersList: React.FC = () => {
  const { orders, isLoading, fetchOrders } = useOrderStore();
  const [filteredOrders, setFilteredOrders] = useState<Order[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<OrderStatus | 'all'>('all');
  const [isFiltersOpen, setIsFiltersOpen] = useState(false);
  
  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);
  
  useEffect(() => {
    let result = [...orders];
    
    if (searchTerm) {
      result = result.filter(
        order => 
          order.trackNumber.toLowerCase().includes(searchTerm.toLowerCase()) ||
          order.phoneNumber.includes(searchTerm) ||
          order.crop.toLowerCase().includes(searchTerm.toLowerCase()) ||
          order.pickupLocation.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          order.destinationLocation.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    if (statusFilter !== 'all') {
      result = result.filter(order => order.status === statusFilter);
    }
    
    setFilteredOrders(result);
  }, [orders, searchTerm, statusFilter]);
  
  const StatusBadge: React.FC<{ status: OrderStatus }> = ({ status }) => {
    const statusConfig = {
      pending: { bg: 'bg-amber-100', text: 'text-amber-800', label: 'Pending' },
      accepted: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Accepted' },
      in_progress: { bg: 'bg-indigo-100', text: 'text-indigo-800', label: 'In Progress' },
      in_transit: { bg: 'bg-purple-100', text: 'text-purple-800', label: 'In Transit' },
      delivered: { bg: 'bg-green-100', text: 'text-green-800', label: 'Delivered' },
      cancelled: { bg: 'bg-red-100', text: 'text-red-800', label: 'Cancelled' },
    };
    
    const config = statusConfig[status];
    
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.bg} ${config.text}`}>
        {config.label}
      </span>
    );
  };
  
  return (
    <div className="animate-fade-in space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Transport Orders</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            View and manage all crop transport orders
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button 
            variant="outline" 
            leftIcon={<Download size={16} />}
          >
            Export
          </Button>
        </div>
      </div>
      
      {/* Search and Filters */}
      <div className="bg-white rounded-lg shadow-sm p-4 dark:bg-gray-800">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="relative flex-1">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search size={18} className="text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search orders by ID, phone, crop..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>
          
          <div>
            <Button 
              variant="outline"
              leftIcon={<Filter size={16} />}
              rightIcon={isFiltersOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
              onClick={() => setIsFiltersOpen(!isFiltersOpen)}
            >
              Filters
            </Button>
          </div>
        </div>
        
        {isFiltersOpen && (
          <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1 dark:text-gray-300">
                Status
              </label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value as OrderStatus | 'all')}
                className="block w-full pl-3 pr-10 py-2 text-base border border-gray-300 rounded-md focus:outline-none focus:ring-primary focus:border-primary sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                <option value="all">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="accepted">Accepted</option>
                <option value="in_progress">In Progress</option>
                <option value="in_transit">In Transit</option>
                <option value="delivered">Delivered</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1 dark:text-gray-300">
                Date Range
              </label>
              <select
                className="block w-full pl-3 pr-10 py-2 text-base border border-gray-300 rounded-md focus:outline-none focus:ring-primary focus:border-primary sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                <option value="all">All Time</option>
                <option value="today">Today</option>
                <option value="week">This Week</option>
                <option value="month">This Month</option>
                <option value="quarter">Last 3 Months</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1 dark:text-gray-300">
                Region
              </label>
              <select
                className="block w-full pl-3 pr-10 py-2 text-base border border-gray-300 rounded-md focus:outline-none focus:ring-primary focus:border-primary sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                <option value="all">All Regions</option>
                <option value="mbeya">Mbeya</option>
                <option value="songwe">Songwe</option>
                <option value="iringa">Iringa</option>
                <option value="njombe">Njombe</option>
              </select>
            </div>
          </div>
        )}
      </div>
      
      {/* Orders Table */}
      <div className="bg-white rounded-lg shadow-sm overflow-hidden dark:bg-gray-800">
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        ) : filteredOrders.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64">
            <Package size={48} className="text-gray-400 mb-4" />
            <p className="text-gray-500 dark:text-gray-400">No orders found</p>
            <p className="text-sm text-gray-400 mt-1 dark:text-gray-500">Try adjusting your search or filters</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300">
                    Order ID
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300">
                    Crop Details
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300">
                    Route
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300">
                    Customer
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
                {filteredOrders.map((order) => (
                  <tr key={order.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900 dark:text-white">{order.trackNumber}</div>
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
                        {order.pickupLocation.region} → {order.destinationLocation.region}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900 dark:text-white">{order.phoneNumber}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <StatusBadge status={order.status} />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {format(new Date(order.createdAt), 'dd/MM/yyyy')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <Link
                        to={`/orders/${order.id}`}
                        className="text-primary hover:text-primary-dark dark:hover:text-primary-light"
                      >
                        View
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        
        {/* Pagination */}
        {filteredOrders.length > 0 && (
          <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6 dark:bg-gray-800 dark:border-gray-700">
            <div className="flex-1 flex justify-between sm:hidden">
              <button
                className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-600"
              >
                Previous
              </button>
              <button
                className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-600"
              >
                Next
              </button>
            </div>
            <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  Showing <span className="font-medium">1</span> to <span className="font-medium">10</span> of{' '}
                  <span className="font-medium">{filteredOrders.length}</span> results
                </p>
              </div>
              <div>
                <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                  <button
                    className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-600"
                  >
                    <span className="sr-only">Previous</span>
                    <ChevronRight className="h-5 w-5 transform rotate-180" aria-hidden="true" />
                  </button>
                  <button
                    className="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-600"
                  >
                    1
                  </button>
                  <button
                    className="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-primary text-sm font-medium text-white hover:bg-primary-dark"
                  >
                    2
                  </button>
                  <button
                    className="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-600"
                  >
                    3
                  </button>
                  <button
                    className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-600"
                  >
                    <span className="sr-only">Next</span>
                    <ChevronRight className="h-5 w-5" aria-hidden="true" />
                  </button>
                </nav>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default OrdersList;