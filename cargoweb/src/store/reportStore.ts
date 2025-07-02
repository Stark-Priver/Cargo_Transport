import { create } from 'zustand';

// TODO: Move to a more appropriate config location or environment variable
const API_BASE_URL = 'http://localhost:5000/api'; // Assuming Flask backend runs on port 5000

interface OrdersSummary {
  total_orders: number;
  orders_by_status: Array<{ status: string; count: number }>;
}

interface ReportState {
  ordersSummary: OrdersSummary | null;
  isSummaryLoading: boolean;
  summaryError: string | null;
  fetchOrdersSummary: () => Promise<void>;

  ordersOverTime: Array<{ order_date: string; count: number }> | null;
  isOverTimeLoading: boolean;
  overTimeError: string | null;
  fetchOrdersOverTime: () => Promise<void>;
}

export const useReportStore = create<ReportState>()((set) => ({
  ordersSummary: null,
  isSummaryLoading: false,
  summaryError: null,

  ordersOverTime: null,
  isOverTimeLoading: false,
  overTimeError: null,

  fetchOrdersSummary: async () => {
    set({ isSummaryLoading: true, summaryError: null });
    try {
      const response = await fetch(`${API_BASE_URL}/reports/orders-summary`);
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
      const data: OrdersSummary = await response.json();
      set({ ordersSummary: data, isSummaryLoading: false });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch orders summary';
      console.error("Error fetching orders summary:", errorMessage);
      set({
        isSummaryLoading: false,
        summaryError: errorMessage
      });
    }
  },


  fetchOrdersOverTime: async () => {
    set({ isOverTimeLoading: true, overTimeError: null });
    try {
      const response = await fetch(`${API_BASE_URL}/reports/orders-over-time`);
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
      const data: Array<{ order_date: string; count: number }> = await response.json();
      set({ ordersOverTime: data, isOverTimeLoading: false });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch orders over time';
      console.error("Error fetching orders over time:", errorMessage);
      set({
        isOverTimeLoading: false,
        overTimeError: errorMessage
      });
    }
  },
}));
