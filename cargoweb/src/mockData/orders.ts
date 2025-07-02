import { Order, OrderStatus } from '../types/order';

// Generate random Tanzanian phone numbers
const generatePhone = () => {
  const prefixes = ['0754', '0755', '0756', '0757', '0765', '0766', '0767', '0713', '0715'];
  const randomPrefix = prefixes[Math.floor(Math.random() * prefixes.length)];
  const randomNumbers = Math.floor(Math.random() * 10000000).toString().padStart(6, '0');
  return `${randomPrefix}${randomNumbers}`;
};

// Generate a tracking number
const generateTrackNumber = (index: number) => {
  const date = new Date();
  const year = date.getFullYear().toString().slice(2);
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  const day = date.getDate().toString().padStart(2, '0');
  return `TRK${year}${month}${day}${index.toString().padStart(3, '0')}`;
};

const crops = ['Mahindi', 'Viazi', 'Mpunga', 'Maharagwe', 'Vitunguu', 'Ndizi', 'Nyanya'];

const locations = [
  { name: 'Mbeya Mjini', region: 'Mbeya', district: 'Mbeya Urban' },
  { name: 'Uyole', region: 'Mbeya', district: 'Mbeya Rural' },
  { name: 'Maendeleo', region: 'Mbeya', district: 'Mbeya Urban' },
  { name: 'Sisimba', region: 'Mbeya', district: 'Mbeya Urban' },
  { name: 'Itiji', region: 'Mbeya', district: 'Mbeya Rural' },
  { name: 'Ruanda', region: 'Mbeya', district: 'Mbeya Urban' },
  { name: 'Tunduma', region: 'Songwe', district: 'Tunduma' },
  { name: 'Vwawa', region: 'Songwe', district: 'Vwawa' },
  { name: 'Chunya', region: 'Mbeya', district: 'Chunya' },
  { name: 'Kyela', region: 'Mbeya', district: 'Kyela' },
];

const statuses: OrderStatus[] = ['pending', 'accepted', 'in_progress', 'in_transit', 'delivered', 'cancelled'];

const transporters = [
  { id: 'TR001', name: 'Juma Mwalimu', phone: '0754123456', rating: '4.8/5', avatarUrl: 'https://randomuser.me/api/portraits/men/1.jpg' },
  { id: 'TR002', name: 'Fatuma Hassan', phone: '0755789012', rating: '4.9/5', avatarUrl: 'https://randomuser.me/api/portraits/women/2.jpg' },
  { id: 'TR003', name: 'Mohamed Ally', phone: '0756345678', rating: '4.7/5', avatarUrl: 'https://randomuser.me/api/portraits/men/3.jpg' },
  { id: 'TR004', name: 'Grace Mapunda', phone: '0757901234', rating: '4.6/5', avatarUrl: 'https://randomuser.me/api/portraits/women/4.jpg' },
  { id: 'TR005', name: 'John Msigwa', phone: '0765567890', rating: '4.8/5', avatarUrl: 'https://randomuser.me/api/portraits/men/5.jpg' },
];

// Generate mock orders
export const mockOrders: Order[] = Array(30).fill(null).map((_, index) => {
  const createdDate = new Date();
  createdDate.setDate(createdDate.getDate() - Math.floor(Math.random() * 30));
  const createdAt = createdDate.toISOString();
  
  const status = statuses[Math.floor(Math.random() * statuses.length)];
  const statusDate = new Date(createdDate);
  statusDate.setHours(statusDate.getHours() + Math.floor(Math.random() * 48));
  const statusUpdatedAt = statusDate.toISOString();
  
  const estimatedDate = new Date(statusDate);
  estimatedDate.setDate(estimatedDate.getDate() + Math.floor(Math.random() * 5) + 1);
  const estimatedDelivery = estimatedDate.toISOString();
  
  const pickupLocation = locations[Math.floor(Math.random() * locations.length)];
  let destinationLocation;
  do {
    destinationLocation = locations[Math.floor(Math.random() * locations.length)];
  } while (destinationLocation.name === pickupLocation.name);
  
  const quantity = Math.floor(Math.random() * 100) + 1;
  const crop = crops[Math.floor(Math.random() * crops.length)];
  
  const transporter = status !== 'pending' ? 
    transporters[Math.floor(Math.random() * transporters.length)] : 
    undefined;
  
  const price = status !== 'pending' ? Math.floor(Math.random() * 500000) + 50000 : undefined;
  
  return {
    id: `ORD${(index + 1).toString().padStart(3, '0')}`,
    trackNumber: generateTrackNumber(index + 1),
    phoneNumber: generatePhone(),
    crop,
    quantity,
    pickupLocation,
    destinationLocation,
    status,
    transporter,
    price,
    notes: Math.random() > 0.7 ? 'Handle with care. Fragile items inside.' : undefined,
    createdAt,
    statusUpdatedAt,
    estimatedDelivery: status !== 'pending' && status !== 'cancelled' ? estimatedDelivery : undefined,
    paymentStatus: status === 'delivered' ? 
      (Math.random() > 0.3 ? 'completed' : 'partial') : 
      (status !== 'cancelled' ? 'pending' : undefined),
    paymentAmount: status === 'delivered' ? Math.floor((price || 0) * (Math.random() * 0.3 + 0.7)) : undefined,
  };
});