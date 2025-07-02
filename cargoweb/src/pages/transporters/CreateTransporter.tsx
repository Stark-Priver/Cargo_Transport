import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Truck, Camera, ArrowLeft } from 'lucide-react';
import { useTransporterStore } from '../../store/transporterStore';
import Button from '../../components/common/Button';

// Tanzania regions and districts
const regions = [
  'Mbeya', 'Songwe', 'Njombe', 'Iringa', 'Rukwa', 'Katavi', 'Dar es Salaam'
];

const districtsByRegion: Record<string, string[]> = {
  'Mbeya': ['Mbeya Urban', 'Mbeya Rural', 'Kyela', 'Rungwe', 'Chunya'],
  'Songwe': ['Songwe', 'Vwawa', 'Tunduma', 'Mbozi'],
  'Njombe': ['Njombe Urban', 'Njombe Rural', 'Wanging\'ombe'],
  'Iringa': ['Iringa Urban', 'Iringa Rural', 'Kilolo'],
  'Rukwa': ['Sumbawanga', 'Kalambo', 'Nkasi'],
  'Katavi': ['Mpanda', 'Tanganyika', 'Mlele'],
  'Dar es Salaam': ['Ilala', 'Kinondoni', 'Temeke', 'Kigamboni', 'Ubungo'],
};

const vehicleTypes = [
  'Pickup', 'Lorry (3 Tons)', 'Lorry (7 Tons)', 'Mini Truck', 'Trailer (20 Tons)'
];

const CreateTransporter: React.FC = () => {
  const navigate = useNavigate();
  const { addTransporter, isLoading } = useTransporterStore();
  
  const [formState, setFormState] = useState({
    name: '',
    phone: '',
    email: '',
    nationalId: '',
    vehicleType: '',
    vehicleNumber: '',
    capacity: '',
    region: '',
    district: '',
    address: '',
    licenseNumber: '',
    transportPermit: '',
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormState(prev => ({ ...prev, [name]: value }));
    
    // Clear error when user types
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
    
    // If region changes, reset district
    if (name === 'region') {
      setFormState(prev => ({ ...prev, district: '' }));
    }
    
    // Set capacity based on vehicle type
    if (name === 'vehicleType') {
      let capacity = '';
      switch (value) {
        case 'Trailer (20 Tons)':
          capacity = '20000';
          break;
        case 'Lorry (7 Tons)':
          capacity = '7000';
          break;
        case 'Lorry (3 Tons)':
          capacity = '3000';
          break;
        case 'Mini Truck':
          capacity = '1500';
          break;
        case 'Pickup':
          capacity = '800';
          break;
      }
      setFormState(prev => ({ ...prev, capacity }));
    }
  };
  
  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    if (!formState.name.trim()) newErrors.name = 'Name is required';
    if (!formState.phone.trim()) newErrors.phone = 'Phone number is required';
    else if (!/^0[0-9]{9}$/.test(formState.phone)) newErrors.phone = 'Invalid phone number format';
    
    if (formState.email && !/^\S+@\S+\.\S+$/.test(formState.email)) 
      newErrors.email = 'Invalid email format';
    
    if (!formState.nationalId.trim()) newErrors.nationalId = 'National ID is required';
    if (!formState.vehicleType) newErrors.vehicleType = 'Vehicle type is required';
    if (!formState.vehicleNumber.trim()) newErrors.vehicleNumber = 'Vehicle number is required';
    if (!formState.region) newErrors.region = 'Region is required';
    if (!formState.district) newErrors.district = 'District is required';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    try {
      await addTransporter({
        ...formState,
        rating: '0/5',
        status: 'active',
        completedOrders: 0,
        totalEarnings: 0,
        capacity: parseInt(formState.capacity) || 0,
      });
      
      navigate('/transporters');
    } catch (error) {
      console.error('Failed to add transporter:', error);
    }
  };
  
  return (
    <div className="animate-fade-in">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/transporters')}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-4 dark:text-gray-400 dark:hover:text-white"
        >
          <ArrowLeft size={16} className="mr-1" />
          Back to Transporters
        </button>
        
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Register New Transporter</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Add a new transporter to the system
        </p>
      </div>
      
      {/* Form */}
      <div className="bg-white rounded-lg shadow-sm p-6 dark:bg-gray-800">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Personal Information */}
          <div>
            <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
              <Truck size={20} className="mr-2 text-primary" />
              Personal Information
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1 dark:text-gray-300">
                  Full Name*
                </label>
                <input
                  type="text"
                  name="name"
                  value={formState.name}
                  onChange={handleInputChange}
                  className={`block w-full px-3 py-2 border ${errors.name ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300 focus:ring-primary focus:border-primary'} rounded-md shadow-sm placeholder-gray-400 focus:outline-none sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white`}
                  placeholder="Enter full name"
                />
                {errors.name && <p className="mt-1 text-sm text-red-600">{errors.name}</p>}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1 dark:text-gray-300">
                  Phone Number*
                </label>
                <input
                  type="text"
                  name="phone"
                  value={formState.phone}
                  onChange={handleInputChange}
                  className={`block w-full px-3 py-2 border ${errors.phone ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300 focus:ring-primary focus:border-primary'} rounded-md shadow-sm placeholder-gray-400 focus:outline-none sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white`}
                  placeholder="e.g. 0755123456"
                />
                {errors.phone && <p className="mt-1 text-sm text-red-600">{errors.phone}</p>}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1 dark:text-gray-300">
                  Email Address
                </label>
                <input
                  type="email"
                  name="email"
                  value={formState.email}
                  onChange={handleInputChange}
                  className={`block w-full px-3 py-2 border ${errors.email ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300 focus:ring-primary focus:border-primary'} rounded-md shadow-sm placeholder-gray-400 focus:outline-none sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white`}
                  placeholder="Enter email address (optional)"
                />
                {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email}</p>}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1 dark:text-gray-300">
                  National ID*
                </label>
                <input
                  type="text"
                  name="nationalId"
                  value={formState.nationalId}
                  onChange={handleInputChange}
                  className={`block w-full px-3 py-2 border ${errors.nationalId ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300 focus:ring-primary focus:border-primary'} rounded-md shadow-sm placeholder-gray-400 focus:outline-none sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white`}
                  placeholder="Enter national ID number"
                />
                {errors.nationalId && <p className="mt-1 text-sm text-red-600">{errors.nationalId}</p>}
              </div>
              
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1 dark:text-gray-300">
                  Profile Picture
                </label>
                <div className="mt-1 flex items-center">
                  <div className="h-20 w-20 rounded-full bg-gray-100 flex items-center justify-center dark:bg-gray-700">
                    <Camera size={24} className="text-gray-400" />
                  </div>
                  <button
                    type="button"
                    className="ml-5 bg-white py-2 px-3 border border-gray-300 rounded-md shadow-sm text-sm leading-4 font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary dark:bg-gray-700 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-600"
                  >
                    Upload
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          {/* Vehicle Information */}
          <div className="border-t border-gray-200 pt-6 dark:border-gray-700">
            <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
              <Truck size={20} className="mr-2 text-primary" />
              Vehicle Information
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1 dark:text-gray-300">
                  Vehicle Type*
                </label>
                <select
                  name="vehicleType"
                  value={formState.vehicleType}
                  onChange={handleInputChange}
                  className={`block w-full px-3 py-2 border ${errors.vehicleType ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300 focus:ring-primary focus:border-primary'} rounded-md shadow-sm focus:outline-none sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white`}
                >
                  <option value="">Select vehicle type</option>
                  {vehicleTypes.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
                {errors.vehicleType && <p className="mt-1 text-sm text-red-600">{errors.vehicleType}</p>}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1 dark:text-gray-300">
                  Vehicle Number*
                </label>
                <input
                  type="text"
                  name="vehicleNumber"
                  value={formState.vehicleNumber}
                  onChange={handleInputChange}
                  className={`block w-full px-3 py-2 border ${errors.vehicleNumber ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300 focus:ring-primary focus:border-primary'} rounded-md shadow-sm placeholder-gray-400 focus:outline-none sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white`}
                  placeholder="e.g. T 123 ABC"
                />
                {errors.vehicleNumber && <p className="mt-1 text-sm text-red-600">{errors.vehicleNumber}</p>}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1 dark:text-gray-300">
                  Capacity (kg)
                </label>
                <input
                  type="text"
                  name="capacity"
                  value={formState.capacity}
                  onChange={handleInputChange}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  placeholder="Capacity in kilograms"
                  readOnly
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1 dark:text-gray-300">
                  License Number
                </label>
                <input
                  type="text"
                  name="licenseNumber"
                  value={formState.licenseNumber}
                  onChange={handleInputChange}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  placeholder="Driver's license number"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1 dark:text-gray-300">
                  Transport Permit
                </label>
                <input
                  type="text"
                  name="transportPermit"
                  value={formState.transportPermit}
                  onChange={handleInputChange}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  placeholder="Transport permit number"
                />
              </div>
            </div>
          </div>
          
          {/* Location Information */}
          <div className="border-t border-gray-200 pt-6 dark:border-gray-700">
            <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              Location Information
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1 dark:text-gray-300">
                  Region*
                </label>
                <select
                  name="region"
                  value={formState.region}
                  onChange={handleInputChange}
                  className={`block w-full px-3 py-2 border ${errors.region ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300 focus:ring-primary focus:border-primary'} rounded-md shadow-sm focus:outline-none sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white`}
                >
                  <option value="">Select region</option>
                  {regions.map(region => (
                    <option key={region} value={region}>{region}</option>
                  ))}
                </select>
                {errors.region && <p className="mt-1 text-sm text-red-600">{errors.region}</p>}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1 dark:text-gray-300">
                  District*
                </label>
                <select
                  name="district"
                  value={formState.district}
                  onChange={handleInputChange}
                  className={`block w-full px-3 py-2 border ${errors.district ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300 focus:ring-primary focus:border-primary'} rounded-md shadow-sm focus:outline-none sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white`}
                  disabled={!formState.region}
                >
                  <option value="">Select district</option>
                  {formState.region && districtsByRegion[formState.region]?.map(district => (
                    <option key={district} value={district}>{district}</option>
                  ))}
                </select>
                {errors.district && <p className="mt-1 text-sm text-red-600">{errors.district}</p>}
              </div>
              
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1 dark:text-gray-300">
                  Address
                </label>
                <textarea
                  name="address"
                  value={formState.address}
                  onChange={handleInputChange}
                  rows={3}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  placeholder="Enter detailed address"
                ></textarea>
              </div>
            </div>
          </div>
          
          {/* Form Actions */}
          <div className="border-t border-gray-200 pt-6 flex justify-end gap-3 dark:border-gray-700">
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate('/transporters')}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              loading={isLoading}
            >
              Register Transporter
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateTransporter;