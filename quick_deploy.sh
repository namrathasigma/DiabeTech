#!/bin/bash

# Quick Deploy Script for GCP Cloud SQL
# This script automates the entire deployment process

set -e  # Exit on any error

echo "🚀 Quick Deploy Script for GCP Cloud SQL"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}$1${NC}"
}

print_success() {
    echo -e "${GREEN}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}$1${NC}"
}

print_error() {
    echo -e "${RED}$1${NC}"
}

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning "No .env file found. Creating from template..."
    if [ -f "env_gcp_example.txt" ]; then
        cp env_gcp_example.txt .env
        print_success "Created .env file from template"
        print_warning "Please edit .env file with your GCP credentials before continuing"
        echo ""
        echo "Required values to set in .env:"
        echo "- GCP_PROJECT_ID: Your Google Cloud Project ID"
        echo "- GCP_ROOT_PASSWORD: Password for root user"
        echo "- GCP_USER_PASSWORD: Password for diabetes_user"
        echo ""
        echo "After editing .env, run this script again."
        exit 1
    else
        print_error "No environment template found. Please create .env file manually."
        exit 1
    fi
fi

# Load environment variables
source .env

# Check if GCP_PROJECT_ID is set
if [ -z "$GCP_PROJECT_ID" ]; then
    print_error "GCP_PROJECT_ID not set in .env file"
    exit 1
fi

print_status "Using GCP Project: $GCP_PROJECT_ID"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    print_error "gcloud CLI not found. Please install Google Cloud SDK first."
    echo "Installation guide: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if gcloud is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    print_warning "Not authenticated with gcloud. Please run: gcloud auth login"
    exit 1
fi

print_success "gcloud authentication verified"

# Check if Python dependencies are installed
if ! python3 -c "import psycopg2, dotenv" 2>/dev/null; then
    print_status "Installing Python dependencies..."
    pip3 install -r requirements.txt
    print_success "Dependencies installed"
fi

# Step 1: Deploy infrastructure
print_status "Step 1: Deploying GCP infrastructure..."
python3 deploy_to_gcp.py

if [ $? -ne 0 ]; then
    print_error "Infrastructure deployment failed"
    exit 1
fi

print_success "Infrastructure deployment completed"

# Step 2: Start Cloud SQL Proxy
print_status "Step 2: Starting Cloud SQL Proxy..."
if [ -f "start_proxy.sh" ]; then
    print_warning "Starting Cloud SQL Proxy in background..."
    ./start_proxy.sh &
    PROXY_PID=$!
    
    # Wait a moment for proxy to start
    sleep 5
    
    print_success "Cloud SQL Proxy started (PID: $PROXY_PID)"
else
    print_error "start_proxy.sh not found. Please run deploy_to_gcp.py first."
    exit 1
fi

# Step 3: Deploy database
print_status "Step 3: Deploying database schema and data..."
python3 deploy_database.py

if [ $? -ne 0 ]; then
    print_error "Database deployment failed"
    # Kill proxy if it's still running
    if kill -0 $PROXY_PID 2>/dev/null; then
        kill $PROXY_PID
    fi
    exit 1
fi

print_success "Database deployment completed"

# Step 4: Verification
print_status "Step 4: Running verification tests..."

# Test connection
if python3 -c "
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    port=int(os.getenv('DB_PORT', 5432))
)
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM patients')
count = cursor.fetchone()[0]
print(f'Patient count: {count}')
cursor.close()
conn.close()
"; then
    print_success "Connection test passed"
else
    print_error "Connection test failed"
fi

# Final instructions
echo ""
print_success "🎉 Deployment completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Your database is now running on GCP Cloud SQL"
echo "2. Cloud SQL Proxy is running (PID: $PROXY_PID)"
echo "3. You can connect using:"
echo "   psql 'host=localhost port=5432 dbname=diabetes_db user=diabetes_user'"
echo ""
echo "🔧 To stop the Cloud SQL Proxy:"
echo "   kill $PROXY_PID"
echo ""
echo "📊 To run sample queries, see the queries in sample_queries.sql"
echo ""
print_warning "⚠️  Remember to secure your instance for production use:"
echo "   - Remove 0.0.0.0/0 from authorized networks"
echo "   - Use Cloud SQL Proxy for secure connections"
echo "   - Set up proper IAM roles and permissions" 