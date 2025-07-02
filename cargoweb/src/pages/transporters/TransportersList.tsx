import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Truck, UserPlus, Filter, Star, Search, ChevronRight, ChevronDown } from 'lucide-react';
import { useTransporterStore } from '../../store/transporterStore';
import Button from '../../components/common/Button';
import { Transporter } from '../../types/transporter';
import { format } from 'date-fns';

const TransportersList: React.FC = () => {
  const { transporters, isLoading, fetchTransporters } = useTransporterStore();
  const [filteredTransporters, setFilteredTransporters] = useState<Transporter[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive' | 'suspended'>('all');
  const [isFiltersOpen, setIsFiltersOpen] = useState(false);
  
  useEffect(() => {
    fetchTransporters();
  }, [fetchTransporters]);
  
  useEffect(() => {
    let result = [...transporters];
    
    if (searchTerm) {
      result = result.filter(
        transporter => 
          transporter.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          transporter.phone.includes(searchTerm) ||
          transporter.vehicleNumber.toLowerCase().includes(searchTerm.toLowerCase()) ||
          (transporter.email && transporter.email.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }
    
    if (statusFilter !== 'all') {
      result = result.filter(transporter => transporter.status === statusFilter);
    }
    
    setFilteredTransporters(result);
  }, [transporters, searchTerm, statusFilter]);
  
  const StatusBadge: React.FC<{ status: Transporter['status'] }> = ({ status }) => {
    const statusConfig = {
      active: { bg: 'bg-green-100', text: 'text-green-800', label: 'Active' },
      inactive: { bg: 'bg-gray-100', text: 'text-gray-800', label: 'Inactive' },
      suspended: { bg: 'bg-red-100', text: 'text-red-800', label: 'Suspended' },
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
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Transporters</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Manage all transporters in the system
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Link to="/transporters/create">
            <Button 
              variant="primary" 
              leftIcon={<UserPlus size={16} />}
            >
              Register Transporter
            </Button>
          </Link>
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
              placeholder="Search transporters by name, phone, vehicle..."
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
                onChange={(e) => setStatusFilter(e.target.value as 'all' | 'active' | 'inactive' | 'suspended')}
                className="block w-full pl-3 pr-10 py-2 text-base border border-gray-300 rounded-md focus:outline-none focus:ring-primary focus:border-primary sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                <option value="all">All Statuses</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="suspended">Suspended</option>
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
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1 dark:text-gray-300">
                Vehicle Type
              </label>
              <select
                className="block w-full pl-3 pr-10 py-2 text-base border border-gray-300 rounded-md focus:outline-none focus:ring-primary focus:border-primary sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                <option value="all">All Types</option>
                <option value="pickup">Pickup</option>
                <option value="lorry-small">Lorry (3 Tons)</option>
                <option value="lorry-medium">Lorry (7 Tons)</option>
                <option value="mini-truck">Mini Truck</option>
                <option value="trailer">Trailer (20 Tons)</option>
              </select>
            </div>
          </div>
        )}
      </div>
      
      {/* Transporters Table */}
      <div className="bg-white rounded-lg shadow-sm overflow-hidden dark:bg-gray-800">
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        ) : filteredTransporters.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64">
            <Truck size={48} className="text-gray-400 mb-4" />
            <p className="text-gray-500 dark:text-gray-400">No transporters found</p>
            <p className="text-sm text-gray-400 mt-1 dark:text-gray-500">Try adjusting your search or filters</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300">
                    Transporter
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300">
                    Contact
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300">
                    Vehicle
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300">
                    Performance
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300">
                    Status
                  </th>
                  <th scope="col" className="relative px-6 py-3">
                    <span className="sr-only">View</span>
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200 dark:bg-gray-800 dark:divide-gray-700">
                {filteredTransporters.map((transporter) => (
                  <tr key={transporter.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="h-10 w-10 flex-shrink-0">
                          {transporter.avatarUrl ? (
                            <img
                              className="h-10 w-10 rounded-full object-cover"
                              src={transporter.avatarUrl}
                              alt={transporter.name}
                            />
                          ) : (
                            <div className="h-10 w-10 rounded-full bg-primary flex items-center justify-center text-white">
                              {transporter.name.charAt(0)}
                            </div>
                          )}
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {transporter.name}
                          </div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">
                            {transporter.region}, {transporter.district}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900 dark:text-white">{transporter.phone}</div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">{transporter.email}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900 dark:text-white">{transporter.vehicleType}</div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        {transporter.vehicleNumber} • {transporter.capacity} kg
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center text-sm text-gray-900 dark:text-white">
                        <Star size={16} className="text-yellow-400 mr-1" />
                        {transporter.rating}
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        {transporter.completedOrders} completed orders
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <StatusBadge status={transporter.status} />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <Link
                        to={`/transporters/${transporter.id}`}
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
        {filteredTransporters.length > 0 && (
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
                  <span className="font-medium">{filteredTransporters.length}</span> results
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

export default TransportersList;