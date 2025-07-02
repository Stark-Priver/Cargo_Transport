import { Transporter } from '../types/transporter';

// Vehicle types commonly used in Tanzania for transporting crops
const vehicleTypes = [
  'Pickup', 'Lorry (3 Tons)', 'Lorry (7 Tons)', 'Mini Truck', 'Trailer (20 Tons)'
];

// Tanzanian regions where the service operates
const regions = [
  'Mbeya', 'Songwe', 'Njombe', 'Iringa', 'Rukwa', 'Katavi', 'Dar es Salaam'
];

// Districts for each region (simplified)
const districts = {
  'Mbeya': ['Mbeya Urban', 'Mbeya Rural', 'Kyela', 'Rungwe', 'Chunya'],
  'Songwe': ['Songwe', 'Vwawa', 'Tunduma', 'Mbozi'],
  'Njombe': ['Njombe Urban', 'Njombe Rural', 'Wanging\'ombe'],
  'Iringa': ['Iringa Urban', 'Iringa Rural', 'Kilolo'],
  'Rukwa': ['Sumbawanga', 'Kalambo', 'Nkasi'],
  'Katavi': ['Mpanda', 'Tanganyika', 'Mlele'],
  'Dar es Salaam': ['Ilala', 'Kinondoni', 'Temeke', 'Kigamboni', 'Ubungo'],
};

// Generate mock transporters
export const mockTransporters: Transporter[] = Array(15).fill(null).map((_, index) => {
  const id = `TR${(index + 1).toString().padStart(3, '0')}`;
  const name = [
    'Juma Mwalimu', 'Fatuma Hassan', 'Mohamed Ally', 'Grace Mapunda', 'John Msigwa',
    'Amina Rashid', 'Peter Kikwete', 'Salma Juma', 'Hassan Mwenda', 'Neema Shayo',
    'David Mwakyusa', 'Sarah Kimaro', 'James Lugakingira', 'Rose Mwasumbi', 'Joseph Mkinga'
  ][index];
  
  // Generate phone number
  const prefixes = ['0754', '0755', '0756', '0757', '0765', '0766', '0767', '0713', '0715'];
  const randomPrefix = prefixes[Math.floor(Math.random() * prefixes.length)];
  const randomNumbers = Math.floor(Math.random() * 10000000).toString().padStart(6, '0');
  const phone = `${randomPrefix}${randomNumbers}`;
  
  // Randomly select other attributes
  const vehicleType = vehicleTypes[Math.floor(Math.random() * vehicleTypes.length)];
  const vehicleNumber = `T ${Math.floor(Math.random() * 1000)} ${String.fromCharCode(65 + Math.floor(Math.random() * 26))}${String.fromCharCode(65 + Math.floor(Math.random() * 26))}`;
  const capacity = vehicleType.includes('Trailer') ? 20000 :
                  vehicleType.includes('7 Tons') ? 7000 :
                  vehicleType.includes('3 Tons') ? 3000 :
                  vehicleType.includes('Mini') ? 1500 : 800;
  
  const region = regions[Math.floor(Math.random() * regions.length)];
  const district = districts[region][Math.floor(Math.random() * districts[region].length)];
  
  const completedOrders = Math.floor(Math.random() * 50) + 1;
  const rating = (Math.floor(Math.random() * 10) + 38) / 10 + '/5';
  const totalEarnings = Math.floor(Math.random() * 5000000) + 500000;
  
  const createdDate = new Date();
  createdDate.setDate(createdDate.getDate() - Math.floor(Math.random() * 500));
  
  const status: 'active' | 'inactive' | 'suspended' = 
    Math.random() > 0.8 ? 'inactive' : Math.random() > 0.9 ? 'suspended' : 'active';
    
  const licenseNumber = `${Math.floor(Math.random() * 10000000).toString().padStart(7, '0')}`;
  const transportPermit = `TP${Math.floor(Math.random() * 1000000).toString().padStart(6, '0')}`;
  
  // Create transporter object
  return {
    id,
    name,
    phone,
    email: name.toLowerCase().replace(' ', '.') + '@example.com',
    nationalId: `${Math.floor(Math.random() * 10000000000).toString().padStart(10, '0')}`,
    rating,
    avatarUrl: `https://randomuser.me/api/portraits/${Math.random() > 0.6 ? 'men' : 'women'}/${index + 1}.jpg`,
    vehicleType,
    vehicleNumber,
    capacity,
    status,
    address: `${Math.floor(Math.random() * 1000)} ${district}, ${region}`,
    region,
    district,
    completedOrders,
    totalEarnings,
    createdAt: createdDate.toISOString(),
    licenseNumber,
    transportPermit,
  };
});