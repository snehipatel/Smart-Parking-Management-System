"""
Smart Parking Management System - Core Logic Module
This module contains the intelligent parking slot allocation algorithms
"""

import numpy as np
from datetime import datetime, timedelta
from database import ParkingDatabase


class ParkingManager:
    """
    Core parking management logic including:
    - Intelligent slot allocation based on distance optimization
    - Real-time availability tracking
    - Rush hour prediction using historical data
    """

    def __init__(self):
        """Initialize parking manager with database connection"""
        self.db = ParkingDatabase()

    def is_vehicle_already_parked(self, vehicle_number):
        """
        Check if vehicle is already parked (Active)
        """
        return self.db.is_vehicle_active(vehicle_number)
    
    
    
    def find_optimal_slot(self, vehicle_type):
        """
        Find the optimal parking slot based on:
        1. Nearest distance from stairs
        2. Lowest slot number (if distances are equal)
        
        Returns:
            dict: Slot information or None if parking is full
        """
        best_slot = self.db.get_best_slot(vehicle_type)
        
        if not best_slot:
            return None
        
        slot_id, floor_number, slot_number, distance, pos_x, pos_y = best_slot
        
        floor_name = self._get_floor_name(floor_number)
        
        return {
            'slot_id': slot_id,
            'floor_number': floor_number,
            'floor_name': floor_name,
            'slot_number': slot_number,
            'distance_from_stairs': distance,
            'position_x': pos_x,
            'position_y': pos_y
        }
    def undo_last_parking(self):
        """
        Undo the most recent parking action
        """
        last_entry = self.db.get_last_parking_entry()

        if not last_entry:
            return False, "No parking action to undo"

        vehicle_number = last_entry["vehicle_number"]
        slot_id = last_entry["slot_id"]

        # Free the slot
        self.db.free_slot(slot_id)

        # Remove parking record
        self.db.remove_parking_record(vehicle_number)

        return True, f"Undo successful for vehicle {vehicle_number}"

    
    def get_all_available_slots(self, vehicle_type):
        """Get all available slots sorted by distance"""
        slots = self.db.get_available_slots(vehicle_type)
        
        result = []
        for slot in slots:
            slot_id, floor_number, slot_number, distance, pos_x, pos_y = slot
            result.append({
                'slot_id': slot_id,
                'floor_number': floor_number,
                'floor_name': self._get_floor_name(floor_number),
                'slot_number': slot_number,
                'distance_from_stairs': distance,
                'position_x': pos_x,
                'position_y': pos_y
            })
        
        return result
  
    def park_vehicle(self, vehicle_number, vehicle_type):
        """
        Park a vehicle in the optimal slot
        """

        # 🚫 PREVENT DUPLICATE PARKING FIRST
        if self.is_vehicle_already_parked(vehicle_number):
            return False, f"Vehicle {vehicle_number} is already parked", None

        # Validate vehicle type
        if vehicle_type not in ["2-Wheeler", "4-Wheeler"]:
            return False, "Invalid vehicle type", None

        # Find optimal slot
        slot_info = self.find_optimal_slot(vehicle_type)

        if not slot_info:
            return False, "🚫 PARKING FULL - No slots available", None

        # Book the slot
        success, message = self.db.book_slot(
            slot_info['slot_id'],
            vehicle_number,
            vehicle_type
        )

        if success:
            return True, "✅ Vehicle parked successfully", slot_info
        else:
            return False, message, None

    
    def exit_vehicle(self, vehicle_number):
        result = self.db.release_slot(vehicle_number)

        if not result:
            return False, "Vehicle is not currently parked"

        slot_id, entry_time, exit_time, duration = result

        return True, {
            "slot_id": slot_id,
            "entry_time": entry_time,   # ISO string
            "exit_time": exit_time,     # datetime
            "duration": duration        # int (minutes)
        }




    
    def get_occupancy_summary(self):
        """
        Get comprehensive occupancy summary
        
        Returns:
            dict: Occupancy statistics for all floors
        """
        floors = self.db.get_floor_occupancy()
        
        summary = {
            'floors': [],
            'total_slots': 0,
            'occupied_slots': 0,
            'vacant_slots': 0,
            'overall_occupancy_rate': 0
        }
        
        for floor in floors:
            floor_num, vehicle_type, total, occupied, vacant, rate = floor
            
            floor_data = {
                'floor_number': floor_num,
                'floor_name': self._get_floor_name(floor_num),
                'vehicle_type': vehicle_type,
                'total_slots': total,
                'occupied_slots': occupied,
                'vacant_slots': vacant,
                'occupancy_rate': rate
            }
            
            summary['floors'].append(floor_data)
            summary['total_slots'] += total
            summary['occupied_slots'] += occupied
            summary['vacant_slots'] += vacant
        
        if summary['total_slots'] > 0:
            summary['overall_occupancy_rate'] = round(
                (summary['occupied_slots'] / summary['total_slots']) * 100, 2
            )
        
        return summary
    
    def get_parking_visualization(self, floor_number):
        """
        Get parking grid data for visualization
        
        Returns:
            dict: Grid layout with slot statuses
        """
        grid_data = self.db.get_parking_grid(floor_number)
        
        if not grid_data:
            return None
        
        # Find grid dimensions
        max_x = max(slot[1] for slot in grid_data)
        max_y = max(slot[2] for slot in grid_data)
        
        # Create grid matrix
        grid = [[None for _ in range(max_x + 1)] for _ in range(max_y + 1)]
        
        for slot in grid_data:
            slot_id, pos_x, pos_y, is_occupied, slot_num = slot
            grid[pos_y][pos_x] = {
                'slot_id': slot_id,
                'slot_number': slot_num,
                'is_occupied': bool(is_occupied),
                'status': 'Occupied' if is_occupied else 'Vacant'
            }
        
        return {
            'floor_number': floor_number,
            'floor_name': self._get_floor_name(floor_number),
            'grid': grid,
            'dimensions': (max_y + 1, max_x + 1)
        }
    
    def predict_rush_hours(self):
        """
        Predict rush hours based on historical parking data
        
        Returns:
            dict: Rush hour predictions
        """
        # Get overall rush prediction
        overall_rush = self.db.get_rush_prediction()
        
        # Get current day rush prediction
        current_day_rush = self.db.get_current_day_rush()
        
        # Classify rush levels
        def classify_rush(occupancy):
            if occupancy >= 80:
                return "🔴 High Rush"
            elif occupancy >= 50:
                return "🟡 Moderate Rush"
            else:
                return "🟢 Low Rush"
        
        overall_predictions = []
        for hour, avg_occ, count in overall_rush:
            overall_predictions.append({
                'hour': hour,
                'time_label': f"{hour:02d}:00 - {hour+1:02d}:00",
                'avg_occupancy': round(avg_occ, 2),
                'rush_level': classify_rush(avg_occ),
                'data_points': count
            })
        
        current_day_predictions = []
        for hour, avg_occ, count in current_day_rush:
            current_day_predictions.append({
                'hour': hour,
                'time_label': f"{hour:02d}:00 - {hour+1:02d}:00",
                'avg_occupancy': round(avg_occ, 2),
                'rush_level': classify_rush(avg_occ),
                'data_points': count
            })
        
        # Get current hour prediction
        current_hour = datetime.now().hour
        current_prediction = None
        
        for pred in current_day_predictions:
            if pred['hour'] == current_hour:
                current_prediction = pred
                break
        
        return {
            'overall_predictions': overall_predictions,
            'today_predictions': current_day_predictions,
            'current_hour_prediction': current_prediction,
            'day_name': datetime.now().strftime('%A')
        }
    
    def get_statistics(self):
        recent_bookings = self.db.get_recent_bookings(limit=10)

        bookings_list = []
        for booking in recent_bookings:
            booking_id, slot_id, vehicle_num, v_type, entry, exit_time, duration = booking

            status = "Active" if exit_time is None else "Exited"

            bookings_list.append({
                "booking_id": booking_id,
                "slot_id": slot_id,
                "vehicle_number": vehicle_num,
                "vehicle_type": v_type,
                "entry_time": entry,
                "exit_time": exit_time,
                "duration_minutes": duration,
                "status": status
            })

        return {"recent_bookings": bookings_list}

    
    def _get_floor_name(self, floor_number):
        """Convert floor number to readable name"""
        floor_names = {
            0: "Ground Floor (2W)",
            1: "Basement 1 (2W)",
            2: "Basement 2 (4W)"
        }
        return floor_names.get(floor_number, f"Floor {floor_number}")
    
    def generate_sample_data(self, num_entries=50):
        """
        Generate sample historical data for rush prediction testing
        This simulates parking activity over the past week
        """
        from random import randint, choice
        
        # Simulate data for past 7 days
        for day_offset in range(7):
            date = datetime.now() - timedelta(days=day_offset)
            
            # Simulate hourly patterns (peak hours: 8-10 AM and 5-7 PM)
            for hour in range(24):
                # Simulate realistic occupancy patterns
                if 8 <= hour <= 10 or 17 <= hour <= 19:
                    # Peak hours - 60-90% occupancy
                    base_occupancy = randint(60, 90)
                elif 11 <= hour <= 16:
                    # Working hours - 40-70% occupancy
                    base_occupancy = randint(40, 70)
                elif 0 <= hour <= 6:
                    # Night hours - 10-30% occupancy
                    base_occupancy = randint(10, 30)
                else:
                    # Other hours - 30-50% occupancy
                    base_occupancy = randint(30, 50)
                
                # Add some randomness
                occupancy = min(100, max(0, base_occupancy + randint(-10, 10)))
                
                # Insert into analytics
                timestamp = date.replace(hour=hour, minute=randint(0, 59))
                self.db.cursor.execute('''
                    INSERT INTO parking_analytics 
                    (hour_of_day, day_of_week, occupancy_rate, timestamp)
                    VALUES (?, ?, ?, ?)
                ''', (hour, date.weekday(), occupancy, timestamp))
        
        self.db.conn.commit()
        print(f"✅ Generated sample data for rush prediction")
    
    def close(self):
        """Close database connection"""
        self.db.close()


if __name__ == "__main__":
        # Test parking manager
            manager = ParkingManager()
            
            print("🚗 Smart Parking Management System - Core Logic Test\n")
            
            # Test finding optimal slot
            print("Finding optimal 2-Wheeler slot...")
            slot = manager.find_optimal_slot("2-Wheeler")
            if slot:
                print(f"  ✅ Best slot: {slot['slot_id']} at {slot['floor_name']}")
                print(f"     Distance from stairs: {slot['distance_from_stairs']}m")
            
            print("\nOccupancy Summary:")
            summary = manager.get_occupancy_summary()
            for floor in summary['floors']:
                print(f"  {floor['floor_name']}: {floor['vacant_slots']}/{floor['total_slots']} available")
            
            manager.close()


