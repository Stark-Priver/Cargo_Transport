import { create } from 'zustand';
import { Transporter } from '../types/transporter';
import { mockTransporters } from '../mockData/transporters';

interface TransporterState {
  transporters: Transporter[];
  isLoading: boolean;
  error: string | null;
  fetchTransporters: () => Promise<void>;
  getTransporterById: (id: string) => Transporter | undefined;
  addTransporter: (transporter: Omit<Transporter, 'id'>) => Promise<void>;
  updateTransporter: (id: string, updates: Partial<Transporter>) => Promise<void>;
  deleteTransporter: (id: string) => Promise<void>;
}

export const useTransporterStore = create<TransporterState>()((set, get) => ({
  transporters: [],
  isLoading: false,
  error: null,
  
  fetchTransporters: async () => {
    set({ isLoading: true, error: null });
    try {
      // Simulating API call with mock data
      await new Promise((resolve) => setTimeout(resolve, 800));
      set({ transporters: mockTransporters, isLoading: false });
    } catch (error) {
      set({ 
        isLoading: false, 
        error: error instanceof Error ? error.message : 'Failed to fetch transporters' 
      });
    }
  },
  
  getTransporterById: (id: string) => {
    return get().transporters.find((transporter) => transporter.id === id);
  },
  
  addTransporter: async (transporter: Omit<Transporter, 'id'>) => {
    set({ isLoading: true, error: null });
    try {
      // Simulating API call
      await new Promise((resolve) => setTimeout(resolve, 800));
      
      const newTransporter: Transporter = {
        id: `TR${Date.now().toString(36)}`,
        createdAt: new Date().toISOString(),
        ...transporter,
      };
      
      set((state) => ({
        transporters: [...state.transporters, newTransporter],
        isLoading: false
      }));
    } catch (error) {
      set({ 
        isLoading: false, 
        error: error instanceof Error ? error.message : 'Failed to add transporter' 
      });
    }
  },
  
  updateTransporter: async (id: string, updates: Partial<Transporter>) => {
    set({ isLoading: true, error: null });
    try {
      // Simulating API call
      await new Promise((resolve) => setTimeout(resolve, 800));
      
      set((state) => ({
        transporters: state.transporters.map((transporter) => 
          transporter.id === id ? { ...transporter, ...updates } : transporter
        ),
        isLoading: false
      }));
    } catch (error) {
      set({ 
        isLoading: false, 
        error: error instanceof Error ? error.message : 'Failed to update transporter' 
      });
    }
  },
  
  deleteTransporter: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      // Simulating API call
      await new Promise((resolve) => setTimeout(resolve, 800));
      
      set((state) => ({
        transporters: state.transporters.filter((transporter) => transporter.id !== id),
        isLoading: false
      }));
    } catch (error) {
      set({ 
        isLoading: false, 
        error: error instanceof Error ? error.message : 'Failed to delete transporter' 
      });
    }
  },
}));