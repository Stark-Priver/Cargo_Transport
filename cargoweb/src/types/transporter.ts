export interface Transporter {
  id: string;
  name: string;
  phone: string;
  email?: string;
  nationalId: string;
  rating: string;
  avatarUrl?: string;
  vehicleType: string;
  vehicleNumber: string;
  capacity: number;
  status: 'active' | 'inactive' | 'suspended';
  address?: string;
  region: string;
  district: string;
  completedOrders: number;
  totalEarnings: number;
  createdAt: string;
  licenseNumber?: string;
  transportPermit?: string;
}