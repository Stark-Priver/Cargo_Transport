import { Injectable, NotFoundException } from '@nestjs/common';
import { CreateTransporterDto } from './dto/create-transporter.dto';
import { UpdateTransporterDto } from './dto/update-transporter.dto';
import { mockTransporters } from '../mock-data/transporters';

@Injectable()
export class TransportersService {
  private transporters = [...mockTransporters];

  findAll() {
    return this.transporters;
  }

  findOne(id: string) {
    const transporter = this.transporters.find(t => t.id === id);
    if (!transporter) {
      throw new NotFoundException(`Transporter with ID ${id} not found`);
    }
    return transporter;
  }

  create(createTransporterDto: CreateTransporterDto) {
    const newTransporter = {
      id: `TR${Date.now().toString(36)}`,
      createdAt: new Date().toISOString(),
      status: 'active',
      completedOrders: 0,
      totalEarnings: 0,
      rating: '0/5',
      ...createTransporterDto,
    };
    
    this.transporters.push(newTransporter);
    return newTransporter;
  }

  update(id: string, updateTransporterDto: UpdateTransporterDto) {
    const index = this.transporters.findIndex(t => t.id === id);
    
    if (index === -1) {
      throw new NotFoundException(`Transporter with ID ${id} not found`);
    }
    
    const updatedTransporter = {
      ...this.transporters[index],
      ...updateTransporterDto,
    };
    
    this.transporters[index] = updatedTransporter;
    return updatedTransporter;
  }

  remove(id: string) {
    const index = this.transporters.findIndex(t => t.id === id);
    
    if (index === -1) {
      throw new NotFoundException(`Transporter with ID ${id} not found`);
    }
    
    const removed = this.transporters[index];
    this.transporters.splice(index, 1);
    
    return removed;
  }
}