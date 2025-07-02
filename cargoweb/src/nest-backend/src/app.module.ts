import { Module } from '@nestjs/common';
import { APP_GUARD } from '@nestjs/core';
import { ConfigModule } from '@nestjs/config';
import { JwtModule } from '@nestjs/jwt';
import { AuthModule } from './auth/auth.module';
import { UsersModule } from './users/users.module';
import { OrdersModule } from './orders/orders.module';
import { TransportersModule } from './transporters/transporters.module';
import { JwtAuthGuard } from './auth/guards/jwt-auth.guard';

@Module({
  imports: [
    // Load environment variables
    ConfigModule.forRoot({
      isGlobal: true,
    }),
    
    // JWT configuration
    JwtModule.register({
      global: true,
      secret: process.env.JWT_SECRET || 'supersecret',
      signOptions: { expiresIn: '1d' },
    }),
    
    // Feature modules
    AuthModule,
    UsersModule,
    OrdersModule,
    TransportersModule,
  ],
  providers: [
    // Global JWT guard
    {
      provide: APP_GUARD,
      useClass: JwtAuthGuard,
    },
  ],
})
export class AppModule {}