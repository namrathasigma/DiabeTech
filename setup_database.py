#!/usr/bin/env python3
"""
Database Setup Script
Creates the diabetes database and applies the schema
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

def create_database():
    """Create the diabetes database if it doesn't exist"""
    # Connect to default postgres database
    conn = psycopg2.connect(
        host=DB_CONFIG['host'],
        database='postgres',
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        port=DB_CONFIG['port']
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Check if database exists
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_CONFIG['database'],))
    exists = cursor.fetchone()
    
    if not exists:
        print(f"Creating database: {DB_CONFIG['database']}")
        cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']}")
        print("Database created successfully!")
    else:
        print(f"Database {DB_CONFIG['database']} already exists.")
    
    cursor.close()
    conn.close()

def apply_schema():
    """Apply the database schema"""
    # Connect to the diabetes database
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Read and execute schema file
    with open('schema.sql', 'r') as f:
        schema_sql = f.read()
    
    print("Applying database schema...")
    cursor.execute(schema_sql)
    conn.commit()
    print("Schema applied successfully!")
    
    cursor.close()
    conn.close()

def main():
    """Main setup function"""
    print("Setting up Diabetes Database...")
    
    try:
        create_database()
        apply_schema()
        print("\nDatabase setup completed successfully!")
        print("\nNext steps:")
        print("1. Install Python dependencies: pip install -r requirements.txt")
        print("2. Run the population script: python populate_database.py")
        
    except Exception as e:
        print(f"Error during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 