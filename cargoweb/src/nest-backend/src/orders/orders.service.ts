import { Injectable, NotFoundException } from '@nestjs/common';
import { UpdateOrderStatusDto } from './dto/update-order-status.dto';
import { mockOrders } from '../mock-data/orders';

@Injectable()
export class OrdersService {
  private orders = [...mockOrders];

  findAll() {
    return this.orders;
  }

  findOne(id: string) {
    const order = this.orders.find(o => o.id === id);
    if (!order) {
      throw new NotFoundException(`Order with ID ${id} not found`);
    }
    return order;
  }

  findByTrackNumber(trackNumber: string) {
    const order = this.orders.find(o => o.trackNumber === trackNumber);
    if (!order) {
      throw new NotFoundException(`Order with tracking number ${trackNumber} not found`);
    }
    return order;
  }

  updateStatus(id: string, updateOrderStatusDto: UpdateOrderStatusDto) {
    const order = this.findOne(id);
    
    const updatedOrder = {
      ...order,
      status: updateOrderStatusDto.status,
      statusUpdatedAt: new Date().toISOString(),
    };
    
    this.orders = this.orders.map(o => o.id === id ? updatedOrder : o);
    
    return updatedOrder;
  }

  // In a real app, we would have methods to create orders, but since they come from USSD
  // for this prototype we're just using mock data
}