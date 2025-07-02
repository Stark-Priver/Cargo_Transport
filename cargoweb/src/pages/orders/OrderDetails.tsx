import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Package, MapPin, Phone, Calendar, Clock, Truck, CreditCard } from 'lucide-react';
import { useOrderStore } from '../../store/orderStore';
import Button from '../../components/common/Button';
import { format } from 'date-fns';

const OrderDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { getOrderById } = useOrderStore();
  const [order, setOrder] = useState(getOrderById(id || ''));
  
  useEffect(() => {
    if (!order) {
      navigate('/orders');
    }
  }, [order, navigate]);
  
  if (!order) {
    return null;
  }
  
  const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
    const statusConfig = {
      pending: { bg: 'bg-amber-100', text: 'text-amber-800', label: 'Pending' },
      accepted: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Accepted' },
      in_progress: { bg: 'bg-indigo-100', text: 'text-indigo-800', label: 'In Progress' },
      in_transit: { bg: 'bg-purple-100', text: 'text-purple-800', label: 'In Transit' },
      delivered: { bg: 'bg-green-100', text: 'text-green-800', label: 'Delivered' },
      cancelled: { bg: 'bg-red-100', text: 'text-red-800', label: 'Cancelled' },
    };
    
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.pending;
    
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
          <button
            onClick={() => navigate('/orders')}
            className="flex items-center text-gray-600 hover:text-gray-900 mb-4 dark:text-gray-400 dark:hover:text-white"
          >
            <ArrowLeft size={16} className="mr-1" />
            Back to Orders
          </button>
          
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Order #{order.trackNumber}
            </h1>
            <StatusBadge status={order.status} />
          </div>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Created on {format(new Date(order.createdAt), 'dd MMM yyyy, HH:mm')}
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button variant="outline">
            Print Details
          </Button>
          <Button variant="primary">
            Update Status
          </Button>
        </div>
      </div>
      
      {/* Order Details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Info */}
          <div className="bg-white rounded-lg shadow-sm p-6 dark:bg-gray-800">
            <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Order Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <div className="flex items-center text-gray-500 dark:text-gray-400 mb-1">
                  <Package size={16} className="mr-2" />
                  <span className="text-sm">Crop Details</span>
                </div>
                <p className="text-gray-900 dark:text-white">{order.crop}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">{order.quantity} bags</p>
              </div>
              
              <div>
                <div className="flex items-center text-gray-500 dark:text-gray-400 mb-1">
                  <Phone size={16} className="mr-2" />
                  <span className="text-sm">Customer Contact</span>
                </div>
                <p className="text-gray-900 dark:text-white">{order.phoneNumber}</p>
              </div>
              
              <div>
                <div className="flex items-center text-gray-500 dark:text-gray-400 mb-1">
                  <MapPin size={16} className="mr-2" />
                  <span className="text-sm">Pickup Location</span>
                </div>
                <p className="text-gray-900 dark:text-white">{order.pickupLocation.name}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {order.pickupLocation.district}, {order.pickupLocation.region}
                </p>
              </div>
              
              <div>
                <div className="flex items-center text-gray-500 dark:text-gray-400 mb-1">
                  <MapPin size={16} className="mr-2" />
                  <span className="text-sm">Destination</span>
                </div>
                <p className="text-gray-900 dark:text-white">{order.destinationLocation.name}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {order.destinationLocation.district}, {order.destinationLocation.region}
                </p>
              </div>
            </div>
          </div>
          
          {/* Timeline */}
          <div className="bg-white rounded-lg shadow-sm p-6 dark:bg-gray-800">
            <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Order Timeline</h2>
            <div className="space-y-6">
              <div className="relative flex items-center">
                <div className="h-4 w-4 rounded-full bg-green-500 flex-shrink-0"></div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">Order Created</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {format(new Date(order.createdAt), 'dd MMM yyyy, HH:mm')}
                  </p>
                </div>
              </div>
              
              {order.status !== 'pending' && (
                <div className="relative flex items-center">
                  <div className="h-4 w-4 rounded-full bg-blue-500 flex-shrink-0"></div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-900 dark:text-white">Transporter Assigned</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {format(new Date(order.statusUpdatedAt), 'dd MMM yyyy, HH:mm')}
                    </p>
                  </div>
                </div>
              )}
              
              {order.status === 'delivered' && (
                <div className="relative flex items-center">
                  <div className="h-4 w-4 rounded-full bg-green-500 flex-shrink-0"></div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-900 dark:text-white">Order Delivered</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {format(new Date(order.statusUpdatedAt), 'dd MMM yyyy, HH:mm')}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
          
          {/* Notes */}
          {order.notes && (
            <div className="bg-white rounded-lg shadow-sm p-6 dark:bg-gray-800">
              <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Additional Notes</h2>
              <p className="text-gray-600 dark:text-gray-300">{order.notes}</p>
            </div>
          )}
        </div>
        
        {/* Side Details */}
        <div className="space-y-6">
          {/* Status Card */}
          <div className="bg-white rounded-lg shadow-sm p-6 dark:bg-gray-800">
            <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Status Details</h2>
            <div className="space-y-4">
              <div>
                <div className="flex items-center text-gray-500 dark:text-gray-400 mb-1">
                  <Clock size={16} className="mr-2" />
                  <span className="text-sm">Last Updated</span>
                </div>
                <p className="text-gray-900 dark:text-white">
                  {format(new Date(order.statusUpdatedAt), 'dd MMM yyyy, HH:mm')}
                </p>
              </div>
              
              {order.estimatedDelivery && (
                <div>
                  <div className="flex items-center text-gray-500 dark:text-gray-400 mb-1">
                    <Calendar size={16} className="mr-2" />
                    <span className="text-sm">Estimated Delivery</span>
                  </div>
                  <p className="text-gray-900 dark:text-white">
                    {format(new Date(order.estimatedDelivery), 'dd MMM yyyy')}
                  </p>
                </div>
              )}
            </div>
          </div>
          
          {/* Transporter Details */}
          {order.transporter && (
            <div className="bg-white rounded-lg shadow-sm p-6 dark:bg-gray-800">
              <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Transporter Details</h2>
              <div className="space-y-4">
                <div className="flex items-center">
                  <div className="h-10 w-10 rounded-full bg-primary flex items-center justify-center text-white overflow-hidden">
                    {order.transporter.avatarUrl ? (
                      <img 
                        src={order.transporter.avatarUrl} 
                        alt={order.transporter.name}
                        className="h-full w-full object-cover"
                      />
                    ) : (
                      <Truck size={20} />
                    )}
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {order.transporter.name}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Rating: {order.transporter.rating}
                    </p>
                  </div>
                </div>
                
                <div>
                  <div className="flex items-center text-gray-500 dark:text-gray-400 mb-1">
                    <Phone size={16} className="mr-2" />
                    <span className="text-sm">Contact</span>
                  </div>
                  <p className="text-gray-900 dark:text-white">{order.transporter.phone}</p>
                </div>
              </div>
            </div>
          )}
          
          {/* Payment Details */}
          {order.price && (
            <div className="bg-white rounded-lg shadow-sm p-6 dark:bg-gray-800">
              <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Payment Details</h2>
              <div className="space-y-4">
                <div>
                  <div className="flex items-center text-gray-500 dark:text-gray-400 mb-1">
                    <CreditCard size={16} className="mr-2" />
                    <span className="text-sm">Transport Fee</span>
                  </div>
                  <p className="text-gray-900 dark:text-white">
                    {new Intl.NumberFormat('en-US', {
                      style: 'currency',
                      currency: 'TZS',
                      minimumFractionDigits: 0,
                      maximumFractionDigits: 0,
                    }).format(order.price)}
                  </p>
                </div>
                
                {order.paymentStatus && (
                  <div>
                    <div className="flex items-center text-gray-500 dark:text-gray-400 mb-1">
                      <CreditCard size={16} className="mr-2" />
                      <span className="text-sm">Payment Status</span>
                    </div>
                    <div className="flex items-center">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        order.paymentStatus === 'completed' 
                          ? 'bg-green-100 text-green-800' 
                          : order.paymentStatus === 'partial'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {order.paymentStatus.charAt(0).toUpperCase() + order.paymentStatus.slice(1)}
                      </span>
                      {order.paymentAmount && (
                        <span className="ml-2 text-sm text-gray-500 dark:text-gray-400">
                          ({new Intl.NumberFormat('en-US', {
                            style: 'currency',
                            currency: 'TZS',
                            minimumFractionDigits: 0,
                            maximumFractionDigits: 0,
                          }).format(order.paymentAmount)} paid)
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default OrderDetails;