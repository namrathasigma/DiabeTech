#!/usr/bin/env python3
"""
GCP Cloud SQL Deployment Script
Automates the deployment of the diabetes database to Google Cloud Platform
"""

import subprocess
import sys
import os
import time
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GCPDeployer:
    def __init__(self):
        self.project_id = os.getenv('GCP_PROJECT_ID')
        self.instance_name = 'diabetes-db'
        self.database_name = 'diabetes_db'
        self.user_name = 'diabetes_user'
        self.region = 'us-west2'
        self.tier = 'db-f1-micro'
        
        if not self.project_id:
            print("❌ GCP_PROJECT_ID not set in environment variables")
            print("Please set GCP_PROJECT_ID in your .env file or environment")
            sys.exit(1)
    
    def run_command(self, command, check=True):
        """Run a shell command and return the result"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {command}")
            print(f"Error: {e.stderr}")
            if check:
                sys.exit(1)
            return None
    
    def check_gcloud_auth(self):
        """Check if gcloud is authenticated"""
        print("🔍 Checking gcloud authentication...")
        result = self.run_command("gcloud auth list --filter=status:ACTIVE --format='value(account)'", check=False)
        if not result:
            print("❌ Not authenticated with gcloud")
            print("Please run: gcloud auth login")
            sys.exit(1)
        print(f"✅ Authenticated as: {result}")
    
    def set_project(self):
        """Set the GCP project"""
        print(f"🔧 Setting project to: {self.project_id}")
        self.run_command(f"gcloud config set project {self.project_id}")
        print("✅ Project set successfully")
    
    def enable_apis(self):
        """Enable required Google Cloud APIs"""
        print("🔧 Enabling required APIs...")
        apis = [
            'sqladmin.googleapis.com',
            'compute.googleapis.com'
        ]
        
        for api in apis:
            print(f"Enabling {api}...")
            self.run_command(f"gcloud services enable {api}")
        
        print("✅ APIs enabled successfully")
    
    def check_instance_exists(self):
        """Check if the Cloud SQL instance already exists"""
        print(f"🔍 Checking if instance {self.instance_name} exists...")
        result = self.run_command(
            f"gcloud sql instances list --filter='name:{self.instance_name}' --format='value(name)'",
            check=False
        )
        return bool(result)
    
    def create_instance(self):
        """Create the Cloud SQL PostgreSQL instance"""
        if self.check_instance_exists():
            print(f"✅ Instance {self.instance_name} already exists")
            return
        
        print(f"🔧 Creating Cloud SQL instance: {self.instance_name}")
        
        # Get root password from environment or prompt
        root_password = os.getenv('GCP_ROOT_PASSWORD')
        if not root_password:
            root_password = input("Enter root password for Cloud SQL instance: ")
        
        command = f"""gcloud sql instances create {self.instance_name} \
            --database-version=POSTGRES_14 \
            --tier={self.tier} \
            --region={self.region} \
            --storage-type=SSD \
            --storage-size=10GB \
            --backup-start-time=02:00 \
            --maintenance-window-day=SUN \
            --maintenance-window-hour=3 \
            --authorized-networks=0.0.0.0/0 \
            --root-password='{root_password}'"""
        
        self.run_command(command)
        print("✅ Cloud SQL instance created successfully")
        
        # Wait for instance to be ready
        print("⏳ Waiting for instance to be ready...")
        time.sleep(30)
    
    def create_database(self):
        """Create the database"""
        print(f"🔧 Creating database: {self.database_name}")
        self.run_command(f"gcloud sql databases create {self.database_name} --instance={self.instance_name}")
        print("✅ Database created successfully")
    
    def create_user(self):
        """Create database user"""
        print(f"🔧 Creating user: {self.user_name}")
        
        # Get user password from environment or prompt
        user_password = os.getenv('GCP_USER_PASSWORD')
        if not user_password:
            user_password = input(f"Enter password for user {self.user_name}: ")
        
        self.run_command(f"gcloud sql users create {self.user_name} --instance={self.instance_name} --password='{user_password}'")
        print("✅ User created successfully")
        
        return user_password
    
    def get_instance_ip(self):
        """Get the instance IP address"""
        print("🔍 Getting instance IP address...")
        ip = self.run_command(f"gcloud sql instances describe {self.instance_name} --format='value(ipAddresses[0].ipAddress)'")
        print(f"✅ Instance IP: {ip}")
        return ip
    
    def get_connection_name(self):
        """Get the connection name for Cloud SQL Proxy"""
        print("🔍 Getting connection name...")
        connection_name = self.run_command(f"gcloud sql instances describe {self.instance_name} --format='value(connectionName)'")
        print(f"✅ Connection name: {connection_name}")
        return connection_name
    
    def update_env_file(self, ip_address, user_password):
        """Update the .env file with GCP connection details"""
        print("🔧 Updating .env file with GCP connection details...")
        
        env_content = f"""# GCP Cloud SQL Configuration
DB_HOST={ip_address}
DB_NAME={self.database_name}
DB_USER={self.user_name}
DB_PASSWORD={user_password}
DB_PORT=5432

# GCP Project Configuration
GCP_PROJECT_ID={self.project_id}
GCP_INSTANCE_NAME={self.instance_name}
GCP_REGION={self.region}
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ .env file updated successfully")
    
    def install_dependencies(self):
        """Install Python dependencies"""
        print("🔧 Installing Python dependencies...")
        self.run_command("pip install -r requirements.txt")
        print("✅ Dependencies installed successfully")
    
    def deploy_database(self):
        """Deploy the database schema and data"""
        print("🔧 Deploying database schema and data...")
        
        # Run setup script
        print("Running database setup...")
        self.run_command("python setup_database.py")
        
        # Run population script
        print("Populating database with sample data...")
        self.run_command("python populate_database.py")
        
        print("✅ Database deployment completed successfully")
    
    def create_cloud_sql_proxy_script(self, connection_name):
        """Create a script to start Cloud SQL Proxy"""
        script_content = f"""#!/bin/bash
# Cloud SQL Proxy startup script

echo "Starting Cloud SQL Proxy..."
echo "Connection: {connection_name}"
echo "Local port: 5432"
echo ""
echo "To connect to the database:"
echo "psql 'host=localhost port=5432 dbname={self.database_name} user={self.user_name} password=YOUR_PASSWORD'"
echo ""
echo "Press Ctrl+C to stop the proxy"
echo ""

./cloud_sql_proxy -instances={connection_name}=tcp:5432
"""
        
        with open('start_proxy.sh', 'w') as f:
            f.write(script_content)
        
        os.chmod('start_proxy.sh', 0o755)
        print("✅ Cloud SQL Proxy script created: start_proxy.sh")
    
    def download_cloud_sql_proxy(self):
        """Download Cloud SQL Proxy"""
        print("🔧 Downloading Cloud SQL Proxy...")
        self.run_command("curl -o cloud_sql_proxy https://dl.google.com/cloudsql/cloud_sql_proxy.darwin.amd64")
        self.run_command("chmod +x cloud_sql_proxy")
        print("✅ Cloud SQL Proxy downloaded successfully")
    
    def deploy(self):
        """Main deployment function"""
        print("🚀 Starting GCP Cloud SQL deployment...")
        print(f"Project: {self.project_id}")
        print(f"Instance: {self.instance_name}")
        print(f"Region: {self.region}")
        print("")
        
        try:
            # Check authentication
            self.check_gcloud_auth()
            
            # Set project
            self.set_project()
            
            # Enable APIs
            self.enable_apis()
            
            # Create instance
            self.create_instance()
            
            # Create database
            self.create_database()
            
            # Create user
            user_password = self.create_user()
            
            # Get connection details
            ip_address = self.get_instance_ip()
            connection_name = self.get_connection_name()
            
            # Update environment file
            self.update_env_file(ip_address, user_password)
            
            # Install dependencies
            self.install_dependencies()
            
            # Download Cloud SQL Proxy
            self.download_cloud_sql_proxy()
            
            # Create proxy script
            self.create_cloud_sql_proxy_script(connection_name)
            
            print("")
            print("🎉 Deployment completed successfully!")
            print("")
            print("Next steps:")
            print("1. Start Cloud SQL Proxy: ./start_proxy.sh")
            print("2. In another terminal, deploy the database: python deploy_database.py")
            print("3. Test connection: psql 'host=localhost port=5432 dbname=diabetes_db user=diabetes_user'")
            print("")
            print("⚠️  Security Note: Remove 0.0.0.0/0 from authorized networks for production use")
            
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            sys.exit(1)

def main():
    """Main function"""
    deployer = GCPDeployer()
    deployer.deploy()

if __name__ == "__main__":
    main() 