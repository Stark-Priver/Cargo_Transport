import { 
  IsNotEmpty, IsString, IsOptional, IsEmail, 
  Matches, IsEnum, IsNumber, Min 
} from 'class-validator';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

enum VehicleType {
  PICKUP = 'Pickup',
  LORRY_SMALL = 'Lorry (3 Tons)',
  LORRY_MEDIUM = 'Lorry (7 Tons)',
  MINI_TRUCK = 'Mini Truck',
  TRAILER = 'Trailer (20 Tons)',
}

export class CreateTransporterDto {
  @ApiProperty({ description: 'Full name of the transporter' })
  @IsNotEmpty()
  @IsString()
  name: string;

  @ApiProperty({ description: 'Phone number of the transporter' })
  @IsNotEmpty()
  @IsString()
  @Matches(/^0[0-9]{9}$/, { message: 'Invalid phone number format' })
  phone: string;

  @ApiPropertyOptional({ description: 'Email address of the transporter' })
  @IsOptional()
  @IsEmail()
  email?: string;

  @ApiProperty({ description: 'National ID number of the transporter' })
  @IsNotEmpty()
  @IsString()
  nationalId: string;

  @ApiProperty({ enum: VehicleType, enumName: 'VehicleType', description: 'Type of vehicle' })
  @IsNotEmpty()
  @IsEnum(VehicleType)
  vehicleType: string;

  @ApiProperty({ description: 'Vehicle registration number' })
  @IsNotEmpty()
  @IsString()
  vehicleNumber: string;

  @ApiProperty({ description: 'Capacity of the vehicle in kilograms' })
  @IsNotEmpty()
  @IsNumber()
  @Min(0)
  capacity: number;

  @ApiProperty({ description: 'Region where the transporter is based' })
  @IsNotEmpty()
  @IsString()
  region: string;

  @ApiProperty({ description: 'District where the transporter is based' })
  @IsNotEmpty()
  @IsString()
  district: string;

  @ApiPropertyOptional({ description: 'Detailed address of the transporter' })
  @IsOptional()
  @IsString()
  address?: string;

  @ApiPropertyOptional({ description: "Driver's license number" })
  @IsOptional()
  @IsString()
  licenseNumber?: string;

  @ApiPropertyOptional({ description: 'Transport permit number' })
  @IsOptional()
  @IsString()
  transportPermit?: string;
}