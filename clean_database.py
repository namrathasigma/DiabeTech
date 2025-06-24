#!/usr/bin/env python3
"""
Database Cleanup Script
Removes existing tables to start fresh
"""

import psycopg2
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection parameters
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'diabetes_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'password'),
    'port': int(os.getenv('DB_PORT', 5431))
}

def clean_database():
    """Remove all existing tables"""
    try:
        # Connect to the diabetes database
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Drop all tables in the correct order (respecting foreign keys)
        tables_to_drop = [
            'appointments',
            'vital_signs', 
            'patient_medications',
            'medications',
            'glucose_readings',
            'lab_results',
            'medical_history',
            'patient_phenotypes',
            'phenotypes',
            'patients'
        ]
        
        print("Cleaning up existing tables...")
        for table in tables_to_drop:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                print(f"Dropped table: {table}")
            except Exception as e:
                print(f"Error dropping {table}: {e}")
        
        # Drop views
        try:
            cursor.execute("DROP VIEW IF EXISTS patient_summary CASCADE")
            print("Dropped view: patient_summary")
        except Exception as e:
            print(f"Error dropping view: {e}")
        
        # Drop functions
        try:
            cursor.execute("DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE")
            print("Dropped function: update_updated_at_column")
        except Exception as e:
            print(f"Error dropping function: {e}")
        
        cursor.close()
        conn.close()
        print("Database cleanup completed successfully!")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    clean_database() 