"""
Smart Parking Management System - Database Module
This module handles all database operations including slot management and booking history
"""

import sqlite3
from datetime import datetime
import os
import tempfile

class ParkingDatabase:
    def __init__(self, db_name="smart_parking.db"):
        """Initialize database connection and create tables if they don't exist"""
        # Use a writable directory for the database (needed for Streamlit Cloud)
        # Check if running on Streamlit Cloud (has specific env markers)
        if os.environ.get("STREAMLIT_SERVER_HEADLESS") or os.environ.get("STREAMLIT_SHARING_MODE"):
            # Streamlit Cloud: use /tmp which is writable
            db_path = os.path.join(tempfile.gettempdir(), db_name)
        else:
            # Local development: use current directory
            db_path = db_name
        self.db_name = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.initialize_database()
    
    def initialize_database(self):
        """Create tables and initialize parking slots"""
        # Create parking slots table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS parking_slots (
                slot_id TEXT PRIMARY KEY,
                floor_number INTEGER NOT NULL,
                slot_number INTEGER NOT NULL,
                vehicle_type TEXT NOT NULL,
                is_occupied BOOLEAN DEFAULT 0,
                distance_from_stairs REAL NOT NULL,
                position_x INTEGER NOT NULL,
                position_y INTEGER NOT NULL
            )
        ''')
        
        # Create booking history table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS booking_history (
                booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                slot_id TEXT NOT NULL,
                vehicle_number TEXT NOT NULL,
                vehicle_type TEXT NOT NULL,
                entry_time TIMESTAMP NOT NULL,
                exit_time TIMESTAMP,
                duration_minutes INTEGER,
                FOREIGN KEY (slot_id) REFERENCES parking_slots(slot_id)
            )
        ''')
        
        # Create analytics table for rush prediction
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS parking_analytics (
                record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                hour_of_day INTEGER NOT NULL,
                day_of_week INTEGER NOT NULL,
                occupancy_rate REAL NOT NULL,
                timestamp TIMESTAMP NOT NULL
            )
        ''')
        
        self.conn.commit()
        
        # Initialize slots if database is empty
        self.cursor.execute("SELECT COUNT(*) FROM parking_slots")
        if self.cursor.fetchone()[0] == 0:
            self.create_parking_slots()
    
    def create_parking_slots(self):
        """
        Initialize parking layout:
        - 2 floors for 2-wheelers (Ground Floor and Basement 1)
        - 1 floor for 4-wheelers (Basement 2)
        Each floor has slots arranged in a grid
        """
        slots = []
        
        # Ground Floor - 2 Wheeler (20 slots in 4x5 grid)
        # Stairs are at position (0, 0)
        for row in range(4):
            for col in range(5):
                slot_num = row * 5 + col + 1
                # Calculate Euclidean distance from stairs at (0, 0)
                distance = ((row * 2) ** 2 + (col * 2) ** 2) ** 0.5
                slots.append((
                    f"GF-2W-{slot_num:02d}",  # slot_id
                    0,  # floor_number (Ground Floor)
                    slot_num,  # slot_number
                    "2-Wheeler",  # vehicle_type
                    0,  # is_occupied
                    round(distance, 2),  # distance_from_stairs
                    col,  # position_x
                    row   # position_y
                ))
        
        # Basement 1 - 2 Wheeler (20 slots in 4x5 grid)
        for row in range(4):
            for col in range(5):
                slot_num = row * 5 + col + 1
                distance = ((row * 2) ** 2 + (col * 2) ** 2) ** 0.5
                slots.append((
                    f"B1-2W-{slot_num:02d}",
                    1,  # Basement 1
                    slot_num,
                    "2-Wheeler",
                    0,
                    round(distance, 2),
                    col,
                    row
                ))
        
        # Basement 2 - 4 Wheeler (15 slots in 3x5 grid)
        for row in range(3):
            for col in range(5):
                slot_num = row * 5 + col + 1
                distance = ((row * 3) ** 2 + (col * 3) ** 2) ** 0.5
                slots.append((
                    f"B2-4W-{slot_num:02d}",
                    2,  # Basement 2
                    slot_num,
                    "4-Wheeler",
                    0,
                    round(distance, 2),
                    col,
                    row
                ))
        
        # Insert all slots
        self.cursor.executemany('''
            INSERT INTO parking_slots 
            (slot_id, floor_number, slot_number, vehicle_type, is_occupied, 
             distance_from_stairs, position_x, position_y)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', slots)
        
        self.conn.commit()
        print(f"✅ Initialized {len(slots)} parking slots")
    
    def get_available_slots(self, vehicle_type):
        """Get all available slots for a specific vehicle type, sorted by distance"""
        self.cursor.execute('''
            SELECT slot_id, floor_number, slot_number, distance_from_stairs, 
                   position_x, position_y
            FROM parking_slots
            WHERE vehicle_type = ? AND is_occupied = 0
            ORDER BY distance_from_stairs ASC, slot_number ASC
        ''', (vehicle_type,))
        
        return self.cursor.fetchall()
    
    def get_best_slot(self, vehicle_type):
        """Get the best available slot (nearest to stairs)"""
        available_slots = self.get_available_slots(vehicle_type)
        return available_slots[0] if available_slots else None
    
    def book_slot(self, slot_id, vehicle_number, vehicle_type):
        """Book a parking slot"""
        try:
            # Mark slot as occupied
            self.cursor.execute('''
                UPDATE parking_slots 
                SET is_occupied = 1 
                WHERE slot_id = ? AND is_occupied = 0
            ''', (slot_id,))
            
            if self.cursor.rowcount == 0:
                return False, "Slot already occupied or doesn't exist"
            
            # Record booking
            self.cursor.execute('''
                INSERT INTO booking_history 
                (slot_id, vehicle_number, vehicle_type, entry_time)
                VALUES (?, ?, ?, ?)
            ''', (slot_id, vehicle_number, vehicle_type, datetime.now()))
            
            self.conn.commit()
            
            # Update analytics
            self.update_analytics()
            
            return True, "Slot booked successfully"
        except Exception as e:
            self.conn.rollback()
            return False, str(e)
    
    def release_slot(self, vehicle_number):
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT slot_id, entry_time
            FROM booking_history
            WHERE vehicle_number = ?
            AND exit_time IS NULL
        """, (vehicle_number,))

        row = cursor.fetchone()
        if not row:
            return None

        slot_id, entry_time = row

        exit_time = datetime.now()
        entry_dt = datetime.fromisoformat(entry_time)
        duration = int((exit_time - entry_dt).total_seconds() / 60)

        # Update booking
        cursor.execute("""
            UPDATE booking_history
            SET exit_time = ?, duration_minutes = ?
            WHERE vehicle_number = ? AND exit_time IS NULL
        """, (exit_time.isoformat(), duration, vehicle_number))

        # Free slot
        cursor.execute("""
            UPDATE parking_slots
            SET is_occupied = 0
            WHERE slot_id = ?
        """, (slot_id,))

        self.conn.commit()

        return slot_id, entry_time, exit_time, duration


    def is_vehicle_active(self, vehicle_number):
        """
        Check if a vehicle currently has an active booking
        """
        self.cursor.execute("""
            SELECT 1
            FROM booking_history
            WHERE vehicle_number = ?
            AND exit_time IS NULL
            LIMIT 1
        """, (vehicle_number,))
        
        return self.cursor.fetchone() is not None

    def get_last_parking_entry(self):
        """
        Get the most recent active parking entry
        """
        self.cursor.execute("""
            SELECT vehicle_number, slot_id
            FROM booking_history
            WHERE exit_time IS NULL
            ORDER BY entry_time DESC
            LIMIT 1
        """)
        
        row = self.cursor.fetchone()
        if not row:
            return None

        return {
            "vehicle_number": row[0],
            "slot_id": row[1]
        }
    
    def remove_parking_record(self, vehicle_number):
        """
        Remove active parking record (used for undo)
        """
        self.cursor.execute("""
            DELETE FROM booking_history
            WHERE vehicle_number = ?
            AND exit_time IS NULL
        """, (vehicle_number,))
        
        self.conn.commit()
    
    def free_slot(self, slot_id):
        """
        Mark a slot as vacant
        """
        self.cursor.execute("""
            UPDATE parking_slots
            SET is_occupied = 0
            WHERE slot_id = ?
        """, (slot_id,))
        
        self.conn.commit()




    def get_floor_occupancy(self):
        """Get occupancy statistics for each floor"""
        self.cursor.execute('''
            SELECT 
                floor_number,
                vehicle_type,
                COUNT(*) as total_slots,
                SUM(is_occupied) as occupied_slots,
                COUNT(*) - SUM(is_occupied) as vacant_slots,
                ROUND(SUM(is_occupied) * 100.0 / COUNT(*), 2) as occupancy_rate
            FROM parking_slots
            GROUP BY floor_number, vehicle_type
            ORDER BY floor_number
        ''')
        
        return self.cursor.fetchall()
    
    def get_parking_grid(self, floor_number):
        """Get parking grid layout for visualization"""
        self.cursor.execute('''
            SELECT slot_id, position_x, position_y, is_occupied, slot_number
            FROM parking_slots
            WHERE floor_number = ?
            ORDER BY position_y, position_x
        ''', (floor_number,))
        
        return self.cursor.fetchall()
    
    def update_analytics(self):
        """Record current occupancy for rush prediction"""
        now = datetime.now()
        
        self.cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(is_occupied) as occupied
            FROM parking_slots
        ''')
        
        total, occupied = self.cursor.fetchone()
        occupancy_rate = (occupied / total * 100) if total > 0 else 0
        
        self.cursor.execute('''
            INSERT INTO parking_analytics 
            (hour_of_day, day_of_week, occupancy_rate, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (now.hour, now.weekday(), occupancy_rate, now))
        
        self.conn.commit()
    
    def get_rush_prediction(self):
        """Predict rush hours based on historical data"""
        self.cursor.execute('''
            SELECT 
                hour_of_day,
                AVG(occupancy_rate) as avg_occupancy,
                COUNT(*) as sample_count
            FROM parking_analytics
            GROUP BY hour_of_day
            HAVING sample_count > 0
            ORDER BY hour_of_day
        ''')
        
        return self.cursor.fetchall()
    
    def get_current_day_rush(self):
        """Get rush prediction for current day of week"""
        current_day = datetime.now().weekday()
        
        self.cursor.execute('''
            SELECT 
                hour_of_day,
                AVG(occupancy_rate) as avg_occupancy,
                COUNT(*) as sample_count
            FROM parking_analytics
            WHERE day_of_week = ?
            GROUP BY hour_of_day
            HAVING sample_count > 0
            ORDER BY hour_of_day
        ''', (current_day,))
        
        return self.cursor.fetchall()
    
    def get_recent_bookings(self, limit=10):
        """Get recent booking history"""
        self.cursor.execute('''
            SELECT 
                booking_id,
                slot_id,
                vehicle_number,
                vehicle_type,
                entry_time,
                exit_time,
                duration_minutes
            FROM booking_history
            ORDER BY entry_time DESC
            LIMIT ?
        ''', (limit,))
        
        return self.cursor.fetchall()
    
    def reset_database(self):
        """Reset entire database (for testing/demo purposes)"""
        self.cursor.execute("DELETE FROM parking_slots")
        self.cursor.execute("DELETE FROM booking_history")
        self.cursor.execute("DELETE FROM parking_analytics")
        self.conn.commit()
        self.create_parking_slots()
    
    def close(self):
        """Close database connection"""
        self.conn.close()


if __name__ == "__main__":
    db = ParkingDatabase()
    print("\n📊 Floor Occupancy:")
    for floor in db.get_floor_occupancy():
        print(f"Floor {floor[0]} - {floor[1]}: {floor[4]} vacant / {floor[2]} total")
    db.close()