import React, { useMemo } from 'react';
import Chart from 'react-apexcharts';
import { Order } from '../../../types/order';
import { useTheme } from '../../../context/ThemeContext';

interface OrderStatusChartProps {
  orders: Order[];
}

const OrderStatusChart: React.FC<OrderStatusChartProps> = ({ orders }) => {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  
  const statusCounts = useMemo(() => {
    const counts = {
      pending: 0,
      accepted: 0,
      in_progress: 0,
      in_transit: 0,
      delivered: 0,
      cancelled: 0,
    };
    
    orders.forEach((order) => {
      counts[order.status] = (counts[order.status] || 0) + 1;
    });
    
    return counts;
  }, [orders]);
  
  const chartOptions = {
    chart: {
      type: 'bar' as const,
      height: 350,
      toolbar: {
        show: false,
      },
      background: 'transparent',
    },
    plotOptions: {
      bar: {
        borderRadius: 4,
        horizontal: false,
        columnWidth: '55%',
      },
    },
    colors: ['#1C6758', '#7D5A50', '#445694', '#FF8C32', '#22C55E', '#EF4444'],
    dataLabels: {
      enabled: false,
    },
    stroke: {
      show: true,
      width: 2,
      colors: ['transparent'],
    },
    xaxis: {
      categories: [
        'Pending', 
        'Accepted', 
        'In Progress', 
        'In Transit', 
        'Delivered', 
        'Cancelled'
      ],
      labels: {
        style: {
          colors: isDark ? '#CBD5E1' : '#64748B',
        },
      },
      axisBorder: {
        show: false,
      },
      axisTicks: {
        show: false,
      },
    },
    yaxis: {
      title: {
        text: 'Number of Orders',
        style: {
          color: isDark ? '#CBD5E1' : '#64748B',
        },
      },
      labels: {
        style: {
          colors: isDark ? '#CBD5E1' : '#64748B',
        },
      },
    },
    fill: {
      opacity: 1,
    },
    tooltip: {
      y: {
        formatter: function (val: number) {
          return val + " orders";
        }
      },
      theme: isDark ? 'dark' : 'light',
    },
    grid: {
      borderColor: isDark ? '#374151' : '#E5E7EB',
    },
    legend: {
      labels: {
        colors: isDark ? '#CBD5E1' : '#64748B',
      },
    },
  };

  const series = [
    {
      name: 'Orders',
      data: [
        statusCounts.pending,
        statusCounts.accepted,
        statusCounts.in_progress,
        statusCounts.in_transit,
        statusCounts.delivered,
        statusCounts.cancelled,
      ],
    },
  ];

  return (
    <div className="w-full">
      <Chart
        options={chartOptions}
        series={series}
        type="bar"
        height={350}
      />
    </div>
  );
};

export default OrderStatusChart;