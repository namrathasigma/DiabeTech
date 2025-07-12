#!/bin/bash
# Cloud SQL Proxy startup script

# Load environment variables from .env
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

echo "Starting Cloud SQL Proxy..."
echo "Connection: $GCP_PROJECT_ID:$GCP_REGION:$GCP_INSTANCE_NAME"
echo "Local port: $DB_PORT"
echo ""
echo "To connect to the database:"
echo "psql 'host=localhost port=$DB_PORT dbname=$DB_NAME user=$DB_USER password=$DB_PASSWORD'"
echo ""
echo "Press Ctrl+C to stop the proxy"
echo ""

./cloud_sql_proxy -instances=$GCP_PROJECT_ID:$GCP_REGION:$GCP_INSTANCE_NAME=tcp:$DB_PORT
