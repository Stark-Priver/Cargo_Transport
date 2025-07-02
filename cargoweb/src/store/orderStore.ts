import { create } from 'zustand';
import { OrderStatus, Order } from '../types/order';
import { mockOrders } from '../mockData/orders';

interface OrderState {
  orders: Order[];
  isLoading: boolean;
  error: string | null;
  fetchOrders: () => Promise<void>;
  getOrderById: (id: string) => Order | undefined;
  updateOrderStatus: (id: string, status: OrderStatus) => Promise<void>;
}

export const useOrderStore = create<OrderState>()((set, get) => ({
  orders: [],
  isLoading: false,
  error: null,
  
  fetchOrders: async () => {
    set({ isLoading: true, error: null });
    try {
      // Simulating API call with mock data
      await new Promise((resolve) => setTimeout(resolve, 800));
      set({ orders: mockOrders, isLoading: false });
    } catch (error) {
      set({ 
        isLoading: false, 
        error: error instanceof Error ? error.message : 'Failed to fetch orders' 
      });
    }
  },
  
  getOrderById: (id: string) => {
    return get().orders.find((order) => order.id === id);
  },
  
  updateOrderStatus: async (id: string, status: OrderStatus) => {
    set({ isLoading: true, error: null });
    try {
      // Simulating API call
      await new Promise((resolve) => setTimeout(resolve, 800));
      
      set((state) => ({
        orders: state.orders.map((order) => 
          order.id === id ? { ...order, status, statusUpdatedAt: new Date().toISOString() } : order
        ),
        isLoading: false
      }));
    } catch (error) {
      set({ 
        isLoading: false, 
        error: error instanceof Error ? error.message : 'Failed to update order status' 
      });
    }
  }
}));