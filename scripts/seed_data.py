#!/usr/bin/env python3
"""
Data seeding script for Phase 2.
Run this after setting up the database to populate initial sensor types and sample data.
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import random
import uuid

from backend.core.config import settings
from backend.models.user import User
from backend.models.vehicle import Vehicle
from backend.models.sensor import SensorData, SensorType
from backend.core.database import Base
from backend.core.auth import get_password_hash

async def seed_database():
    """Seed the database with initial data."""

    # Create engine
    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            print("🌱 Seeding database...")

            # Create sample users
            print("Creating sample users...")
            users_data = [
                {"name": "Admin User", "email": "admin@apms.com", "password": "admin123", "role": "admin"},
                {"name": "John Engineer", "email": "john@apms.com", "password": "engineer123", "role": "engineer"},
                {"name": "Sarah Viewer", "email": "sarah@apms.com", "password": "viewer123", "role": "viewer"},
            ]

            users = []
            for user_data in users_data:
                user = User(
                    name=user_data["name"],
                    email=user_data["email"],
                    password_hash=get_password_hash(user_data["password"]),
                    role=user_data["role"]
                )
                session.add(user)
                users.append(user)

            await session.commit()

            # Create sample vehicles
            print("Creating sample vehicles...")
            vehicles_data = [
                {"name": "Truck-001", "model": "Volvo FH16", "registration_number": "TRK001", "owner_id": users[0].id},
                {"name": "Truck-002", "model": "Scania R500", "registration_number": "TRK002", "owner_id": users[1].id},
                {"name": "Van-001", "model": "Ford Transit", "registration_number": "VAN001", "owner_id": users[2].id},
            ]

            vehicles = []
            for vehicle_data in vehicles_data:
                vehicle = Vehicle(
                    name=vehicle_data["name"],
                    model=vehicle_data["model"],
                    registration_number=vehicle_data["registration_number"],
                    owner_id=vehicle_data["owner_id"]
                )
                session.add(vehicle)
                vehicles.append(vehicle)

            await session.commit()

            # Create sensor types
            print("Creating sensor types...")
            sensor_types_data = [
                {"name": "temperature", "description": "Engine temperature sensor", "unit": "celsius", "normal_range_min": 80.0, "normal_range_max": 105.0, "critical_threshold": 110.0},
                {"name": "vibration", "description": "Engine vibration sensor", "unit": "hz", "normal_range_min": 0.0, "normal_range_max": 50.0, "critical_threshold": 100.0},
                {"name": "pressure", "description": "Oil pressure sensor", "unit": "psi", "normal_range_min": 30.0, "normal_range_max": 60.0, "critical_threshold": 25.0},
                {"name": "fuel_level", "description": "Fuel level sensor", "unit": "percent", "normal_range_min": 10.0, "normal_range_max": 100.0, "critical_threshold": 5.0},
                {"name": "battery_voltage", "description": "Battery voltage sensor", "unit": "volts", "normal_range_min": 12.0, "normal_range_max": 14.5, "critical_threshold": 11.5},
            ]

            sensor_types = []
            for sensor_data in sensor_types_data:
                sensor_type = SensorType(
                    name=sensor_data["name"],
                    description=sensor_data["description"],
                    unit=sensor_data["unit"],
                    normal_range_min=sensor_data["normal_range_min"],
                    normal_range_max=sensor_data["normal_range_max"],
                    critical_threshold=sensor_data["critical_threshold"]
                )
                session.add(sensor_type)
                sensor_types.append(sensor_type)

            await session.commit()

            # Generate sample sensor data
            print("Generating sample sensor data...")
            base_time = datetime.utcnow() - timedelta(hours=48)  # 48 hours of data

            for vehicle in vehicles:
                print(f"Generating data for {vehicle.name}...")

                # Generate readings every 15 minutes for 48 hours
                current_time = base_time
                while current_time < datetime.utcnow():
                    for sensor_type in sensor_types:
                        # Generate realistic sensor values with some noise
                        if sensor_type.name == "temperature":
                            base_value = 90.0 + random.uniform(-5, 5)
                        elif sensor_type.name == "vibration":
                            base_value = 25.0 + random.uniform(-10, 10)
                        elif sensor_type.name == "pressure":
                            base_value = 45.0 + random.uniform(-5, 5)
                        elif sensor_type.name == "fuel_level":
                            base_value = max(0, 80.0 + random.uniform(-20, 5))  # Fuel decreases over time
                        elif sensor_type.name == "battery_voltage":
                            base_value = 13.2 + random.uniform(-0.5, 0.5)

                        # Add some anomalies (5% chance)
                        is_anomaly = 1 if random.random() < 0.05 else 0
                        if is_anomaly:
                            # Make anomalous readings more extreme
                            base_value *= random.uniform(1.5, 2.0) if random.random() > 0.5 else random.uniform(0.3, 0.7)

                        sensor_reading = SensorData(
                            vehicle_id=vehicle.id,
                            sensor_type=sensor_type.name,
                            sensor_value=round(base_value, 2),
                            unit=sensor_type.unit,
                            location="engine" if sensor_type.name in ["temperature", "vibration", "pressure"] else "general",
                            timestamp=current_time,
                            quality_score=round(random.uniform(0.8, 1.0), 2),
                            is_anomaly=is_anomaly
                        )
                        session.add(sensor_reading)

                    current_time += timedelta(minutes=15)

            await session.commit()

            print("✅ Database seeding completed successfully!")
            print(f"Created {len(users)} users, {len(vehicles)} vehicles, {len(sensor_types)} sensor types")
            print("Generated sample sensor data for the last 48 hours")

            # Print login credentials
            print("\n🔐 Sample Login Credentials:")
            for user_data in users_data:
                print(f"Email: {user_data['email']} | Password: {user_data['password']} | Role: {user_data['role']}")

        except Exception as e:
            print(f"❌ Error seeding database: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()

if __name__ == "__main__":
    asyncio.run(seed_database())