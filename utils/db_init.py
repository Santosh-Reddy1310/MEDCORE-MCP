"""
Database initialization utility for production deployment.
Automatically creates and populates the database if it doesn't exist.
"""
import sqlite3
import os
import sys
from datetime import datetime, timedelta
import random

# Add parent directory to path to import from db folder
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "db", "hospital.db")
DB_DIR = os.path.dirname(DB_PATH)


def ensure_db_directory():
    """Ensure the database directory exists."""
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        print(f"✓ Created database directory: {DB_DIR}")


def check_database_exists():
    """Check if database file exists and has tables."""
    if not os.path.exists(DB_PATH):
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        conn.close()
        
        required_tables = ['doctors', 'patients', 'beds', 'appointments', 'hospital_stats']
        existing_tables = [t[0] for t in tables]
        
        return all(table in existing_tables for table in required_tables)
    except Exception as e:
        print(f"⚠ Error checking database: {e}")
        return False


def initialize_database(populate=True):
    """Initialize the database with schema and optional sample data."""
    ensure_db_directory()
    
    if check_database_exists():
        print("✓ Database already exists and is valid")
        return True
    
    print("⚡ Initializing database...")
    
    try:
        # Import and run the setup script
        from db.setup_db import create_tables, insert_sample_data
        
        conn = sqlite3.connect(DB_PATH)
        
        # Create tables
        create_tables(conn)
        print("✓ Created database tables")
        
        # Insert sample data if requested
        if populate:
            insert_sample_data(conn)
            print("✓ Populated sample data")
        
        conn.commit()
        conn.close()
        
        print("✅ Database initialization complete!")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_db_stats():
    """Get quick database statistics."""
    if not check_database_exists():
        return None
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM patients WHERE status != 'discharged'")
        active_patients = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM doctors WHERE available = 1")
        available_doctors = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM beds WHERE is_occupied = 1")
        occupied_beds = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM beds")
        total_beds = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "active_patients": active_patients,
            "available_doctors": available_doctors,
            "occupied_beds": occupied_beds,
            "total_beds": total_beds,
            "occupancy_rate": round((occupied_beds / total_beds * 100), 1) if total_beds > 0 else 0
        }
    except Exception as e:
        print(f"⚠ Error getting stats: {e}")
        return None


if __name__ == "__main__":
    # Run initialization
    initialize_database(populate=True)
    
    # Show stats
    stats = get_db_stats()
    if stats:
        print("\n📊 Database Statistics:")
        print(f"   Active Patients: {stats['active_patients']}")
        print(f"   Available Doctors: {stats['available_doctors']}")
        print(f"   Bed Occupancy: {stats['occupied_beds']}/{stats['total_beds']} ({stats['occupancy_rate']}%)")
