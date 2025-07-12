#!/usr/bin/env python3
"""
Database Deployment Script for GCP Cloud SQL
Deploys the diabetes database schema and sample data to GCP
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
    'user': os.getenv('DB_USER', 'diabetes_user'),
    'password': os.getenv('DB_PASSWORD'),
    'port': int(os.getenv('DB_PORT', 5432))
}

def test_connection():
    """Test database connection"""
    print("🔍 Testing database connection...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Connected successfully to PostgreSQL: {version[0]}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def apply_schema():
    """Apply the database schema"""
    print("🔧 Applying database schema...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Read and execute schema file
        with open('schema.sql', 'r') as f:
            schema_sql = f.read()
        
        cursor.execute(schema_sql)
        conn.commit()
        print("✅ Schema applied successfully!")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Schema application failed: {e}")
        return False

def populate_data():
    """Populate the database with sample data"""
    print("🔧 Populating database with sample data...")
    
    try:
        # Import and run the population script
        from populate_database import main as populate_main
        populate_main()
        print("✅ Data population completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Data population failed: {e}")
        return False

def verify_deployment():
    """Verify the deployment by checking key tables"""
    print("🔍 Verifying deployment...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('patients', 'phenotypes', 'patient_phenotypes')
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        if len(tables) >= 3:
            print("✅ Core tables created successfully")
        else:
            print(f"⚠️  Only {len(tables)} core tables found")
        
        # Check patient count
        cursor.execute("SELECT COUNT(*) FROM patients;")
        patient_count = cursor.fetchone()[0]
        print(f"✅ {patient_count} patients loaded")
        
        # Check phenotype count
        cursor.execute("SELECT COUNT(*) FROM phenotypes;")
        phenotype_count = cursor.fetchone()[0]
        print(f"✅ {phenotype_count} phenotypes loaded")
        
        # Check patient-phenotype assignments
        cursor.execute("SELECT COUNT(*) FROM patient_phenotypes;")
        assignment_count = cursor.fetchone()[0]
        print(f"✅ {assignment_count} patient-phenotype assignments created")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def show_connection_info():
    """Show connection information"""
    print("\n📋 Connection Information:")
    print(f"Host: {DB_CONFIG['host']}")
    print(f"Database: {DB_CONFIG['database']}")
    print(f"User: {DB_CONFIG['user']}")
    print(f"Port: {DB_CONFIG['port']}")
    print("")
    print("🔗 To connect directly:")
    print(f"psql 'host={DB_CONFIG['host']} port={DB_CONFIG['port']} dbname={DB_CONFIG['database']} user={DB_CONFIG['user']} password=YOUR_PASSWORD'")
    print("")
    print("🔗 To connect via Cloud SQL Proxy:")
    print("psql 'host=localhost port=5432 dbname=diabetes_db user=diabetes_user password=YOUR_PASSWORD'")

def main():
    """Main deployment function"""
    print("🚀 Starting database deployment to GCP Cloud SQL...")
    print("")
    
    # Check if required environment variables are set
    if not DB_CONFIG['password']:
        print("❌ DB_PASSWORD not set in environment variables")
        print("Please set DB_PASSWORD in your .env file")
        sys.exit(1)
    
    # Test connection
    if not test_connection():
        print("\n❌ Cannot proceed without database connection")
        print("Please ensure:")
        print("1. Cloud SQL Proxy is running (./start_proxy.sh)")
        print("2. Database credentials are correct in .env file")
        print("3. Network access is configured")
        sys.exit(1)
    
    # Apply schema
    if not apply_schema():
        print("\n❌ Schema deployment failed")
        sys.exit(1)
    
    # Populate data
    if not populate_data():
        print("\n❌ Data population failed")
        sys.exit(1)
    
    # Verify deployment
    if not verify_deployment():
        print("\n❌ Deployment verification failed")
        sys.exit(1)
    
    print("")
    print("🎉 Database deployment completed successfully!")
    print("")
    
    # Show connection information
    show_connection_info()
    
    print("📊 Sample queries to test:")
    print("-- Check patient count by phenotype")
    print("SELECT ph.phenotype_name, COUNT(p.patient_id) FROM patients p")
    print("JOIN patient_phenotypes pp ON p.patient_id = pp.patient_id")
    print("JOIN phenotypes ph ON pp.phenotype_id = ph.phenotype_id")
    print("GROUP BY ph.phenotype_name;")
    print("")
    print("-- Check recent glucose readings")
    print("SELECT p.first_name, gr.glucose_value, gr.reading_date")
    print("FROM patients p JOIN glucose_readings gr ON p.patient_id = gr.patient_id")
    print("ORDER BY gr.reading_date DESC LIMIT 10;")

if __name__ == "__main__":
    main() 