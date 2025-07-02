export type OrderStatus = 
  | 'pending'
  | 'accepted'
  | 'in_progress'
  | 'in_transit'
  | 'delivered'
  | 'cancelled';

export interface Location {
  name: string;
  region?: string;
  district?: string;
  coordinates?: {
    latitude: number;
    longitude: number;
  };
}

export interface Transporter {
  id: string;
  name: string;
  phone: string;
  rating: string;
  avatarUrl?: string;
}

export interface Order {
  id: string;
  trackNumber: string;
  phoneNumber: string;
  crop: string;
  quantity: number;
  pickupLocation: Location;
  destinationLocation: Location;
  status: OrderStatus;
  transporter?: Transporter;
  price?: number;
  notes?: string;
  createdAt: string;
  statusUpdatedAt: string;
  estimatedDelivery?: string;
  paymentStatus?: 'pending' | 'partial' | 'completed';
  paymentAmount?: number;
}