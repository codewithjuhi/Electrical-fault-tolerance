#!/bin/bash

# Electrical Fault Detection - AWS EC2 Automated Deployment Script
# Run this script on your EC2 instance after SSH connection
# Usage: bash deploy.sh

set -e

echo "=========================================="
echo "Starting Fault Detection App Deployment"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Update System
echo -e "\n${YELLOW}[Step 1]${NC} Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Step 2: Install Dependencies
echo -e "\n${YELLOW}[Step 2]${NC} Installing Python and dependencies..."
sudo apt install -y python3.11 python3-pip python3-venv git wget curl nginx

# Step 3: Clone Repository
echo -e "\n${YELLOW}[Step 3]${NC} Cloning repository..."
cd ~/
if [ -d "Electrical-fault-tolerance" ]; then
    echo "Repository already exists, pulling latest changes..."
    cd Electrical-fault-tolerance
    git pull
else
    git clone https://github.com/codewithjuhi/Electrical-fault-tolerance.git
    cd Electrical-fault-tolerance
fi

# Step 4: Create Virtual Environment
echo -e "\n${YELLOW}[Step 4]${NC} Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Step 5: Install Python Dependencies
echo -e "\n${YELLOW}[Step 5]${NC} Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Step 6: Create Systemd Services
echo -e "\n${YELLOW}[Step 6]${NC} Creating systemd services..."

# FastAPI Service
sudo tee /etc/systemd/system/fault-detection-api.service > /dev/null <<EOF
[Unit]
Description=Electrical Fault Detection API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Electrical-fault-tolerance
Environment="PATH=/home/ubuntu/Electrical-fault-tolerance/venv/bin"
ExecStart=/home/ubuntu/Electrical-fault-tolerance/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Streamlit Service
sudo tee /etc/systemd/system/fault-detection-ui.service > /dev/null <<EOF
[Unit]
Description=Electrical Fault Detection UI
After=network.target fault-detection-api.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Electrical-fault-tolerance
Environment="PATH=/home/ubuntu/Electrical-fault-tolerance/venv/bin"
ExecStart=/home/ubuntu/Electrical-fault-tolerance/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Step 7: Enable and Start Services
echo -e "\n${YELLOW}[Step 7]${NC} Enabling and starting services..."
sudo systemctl daemon-reload
sudo systemctl enable fault-detection-api
sudo systemctl enable fault-detection-ui
sudo systemctl start fault-detection-api
sudo systemctl start fault-detection-ui

# Wait for services to start
sleep 5

# Step 8: Configure Nginx
echo -e "\n${YELLOW}[Step 8]${NC} Configuring Nginx reverse proxy..."

# Get public IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

sudo tee /etc/nginx/sites-available/fault-detection > /dev/null <<EOF
upstream api_backend {
    server 127.0.0.1:8001;
}

upstream streamlit_backend {
    server 127.0.0.1:8501;
}

server {
    listen 80 default_server;
    server_name $PUBLIC_IP;

    # API endpoints
    location /api/ {
        proxy_pass http://api_backend/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Direct API access
    location /detect {
        proxy_pass http://api_backend/detect;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    location /classify {
        proxy_pass http://api_backend/classify;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    location /health {
        proxy_pass http://api_backend/health;
        proxy_set_header Host \$host;
    }

    # Streamlit UI
    location / {
        proxy_pass http://streamlit_backend/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
EOF

# Remove default Nginx config
sudo rm -f /etc/nginx/sites-enabled/default

# Enable Nginx configuration
sudo ln -sf /etc/nginx/sites-available/fault-detection /etc/nginx/sites-enabled/

# Test Nginx configuration
if sudo nginx -t; then
    echo -e "${GREEN}✓ Nginx configuration valid${NC}"
else
    echo -e "${RED}✗ Nginx configuration error${NC}"
    exit 1
fi

# Start/Restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx

# Step 9: Verification
echo -e "\n${YELLOW}[Step 9]${NC} Verifying deployment..."

# Check services
echo -e "\n${YELLOW}Service Status:${NC}"
sudo systemctl status fault-detection-api --no-pager || true
echo ""
sudo systemctl status fault-detection-ui --no-pager || true
echo ""
sudo systemctl status nginx --no-pager || true

# Wait for services to be ready
sleep 3

# Test API
echo -e "\n${YELLOW}Testing API connectivity:${NC}"
if curl -s http://localhost:8001/health > /dev/null; then
    HEALTH=$(curl -s http://localhost:8001/health)
    echo -e "${GREEN}✓ API is running${NC}"
    echo "  Health: $HEALTH"
else
    echo -e "${RED}✗ API is not responding${NC}"
fi

# Summary
echo -e "\n${GREEN}=========================================="
echo "Deployment Complete!"
echo "==========================================${NC}\n"

echo "Access your application:"
echo "  Web UI: http://$PUBLIC_IP:8501 or http://$PUBLIC_IP"
echo "  API: http://$PUBLIC_IP:8001"
echo ""
echo "Service Management:"
echo "  View API logs: sudo journalctl -u fault-detection-api -f"
echo "  View UI logs: sudo journalctl -u fault-detection-ui -f"
echo "  Restart API: sudo systemctl restart fault-detection-api"
echo "  Restart UI: sudo systemctl restart fault-detection-ui"
echo ""
echo "Update Application:"
echo "  cd ~/Electrical-fault-tolerance"
echo "  git pull"
echo "  sudo systemctl restart fault-detection-api fault-detection-ui"
echo ""
