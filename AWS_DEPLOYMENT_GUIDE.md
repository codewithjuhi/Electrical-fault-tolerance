# AWS EC2 Deployment Guide (Free Tier)

## Overview
Deploy the Electrical Fault Detection application on AWS EC2 t2.micro instance (free tier eligible for 12 months).

## Prerequisites
- AWS Account (with free tier eligibility)
- AWS CLI installed locally
- SSH key pair for EC2 access
- Application code pushed to GitHub

## Step 1: Launch EC2 Instance

### Option A: Using AWS CLI
```bash
# Create EC2 instance (Ubuntu 22.04 LTS, t2.micro)
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t2.micro \
  --key-name your-key-pair \
  --security-groups "fault-detection-sg" \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=FaultDetectionApp}]'
```

### Option B: AWS Console (Manual)
1. Go to **EC2 Dashboard** → **Launch Instances**
2. **AMI**: Select Ubuntu Server 22.04 LTS
3. **Instance Type**: t2.micro (Free tier eligible)
4. **Security Group**: Create new with rules:
   - SSH (22): Your IP
   - HTTP (80): Anywhere
   - HTTPS (443): Anywhere
   - Custom TCP (8001, 8501): Anywhere (or restrict to your IP)
5. **Storage**: 20 GB (default is free tier eligible)
6. **Review & Launch** → Select/Create key pair → Launch

## Step 2: Connect to EC2 Instance

```bash
# Set permissions on key pair
chmod 400 your-key-pair.pem

# Connect via SSH
ssh -i your-key-pair.pem ec2-user@<PUBLIC_IP>
# or for Ubuntu
ssh -i your-key-pair.pem ubuntu@<PUBLIC_IP>
```

## Step 3: Update System and Install Dependencies

```bash
# Update system packages
sudo apt update
sudo apt upgrade -y

# Install Python and required tools
sudo apt install -y python3.11 python3-pip python3-venv git wget curl

# Verify Python installation
python3 --version
```

## Step 4: Clone Application

```bash
# Navigate to home directory
cd ~/

# Clone the repository
git clone https://github.com/codewithjuhi/Electrical-fault-tolerance.git
cd Electrical-fault-tolerance

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 5: Setup Application Services

### Create Systemd Service for FastAPI Backend

**File**: `/etc/systemd/system/fault-detection-api.service`

```bash
sudo nano /etc/systemd/system/fault-detection-api.service
```

**Content**:
```ini
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
```

### Create Systemd Service for Streamlit Frontend

**File**: `/etc/systemd/system/fault-detection-ui.service`

```bash
sudo nano /etc/systemd/system/fault-detection-ui.service
```

**Content**:
```ini
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
```

## Step 6: Enable and Start Services

```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Enable services to start on boot
sudo systemctl enable fault-detection-api
sudo systemctl enable fault-detection-ui

# Start services
sudo systemctl start fault-detection-api
sudo systemctl start fault-detection-ui

# Check service status
sudo systemctl status fault-detection-api
sudo systemctl status fault-detection-ui
```

## Step 7: Setup Nginx Reverse Proxy (Optional but Recommended)

```bash
# Install Nginx
sudo apt install -y nginx

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/fault-detection
```

**Content**:
```nginx
upstream api_backend {
    server 127.0.0.1:8001;
}

upstream streamlit_backend {
    server 127.0.0.1:8501;
}

server {
    listen 80;
    server_name <YOUR_EC2_PUBLIC_IP>;

    # API endpoints
    location /api/ {
        proxy_pass http://api_backend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Streamlit UI
    location / {
        proxy_pass http://streamlit_backend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
# Enable Nginx configuration
sudo ln -s /etc/nginx/sites-available/fault-detection /etc/nginx/sites-enabled/

# Test Nginx configuration
sudo nginx -t

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

## Step 8: Verify Deployment

```bash
# Check service logs
sudo journalctl -u fault-detection-api -f
sudo journalctl -u fault-detection-ui -f

# Test API endpoint
curl http://localhost:8001/health

# Check open ports
sudo netstat -tuln | grep -E '8001|8501|80'
```

## Step 9: Access Application

- **Streamlit UI**: `http://<YOUR_EC2_PUBLIC_IP>:8501` or `http://<YOUR_EC2_PUBLIC_IP>/` (if Nginx configured)
- **API Health**: `http://<YOUR_EC2_PUBLIC_IP>:8001/health`
- **API Endpoints**:
  - POST `/detect` - Fault detection
  - POST `/classify` - Fault classification

## Troubleshooting

### Service won't start
```bash
# Check service status
sudo systemctl status fault-detection-api
sudo journalctl -u fault-detection-api -n 50
```

### Port already in use
```bash
# Find process using port
sudo lsof -i :8001
sudo lsof -i :8501

# Kill process if needed
sudo kill -9 <PID>
```

### ModuleNotFoundError
```bash
# Reactivate virtual environment and reinstall
source ~/Electrical-fault-tolerance/venv/bin/activate
pip install -r requirements.txt
```

## Cost Estimation (Free Tier - 12 months)
- **EC2 t2.micro**: Free (750 hours/month)
- **Data Transfer**: Free (1 GB/month outbound)
- **Storage**: Free (20 GB EBS)
- **Total Cost**: $0 for 12 months (eligible accounts)

After 12 months: ~$10-15/month for t2.micro

## Scaling Options
1. **Increase Instance Type**: Move to t2.small or t3.micro
2. **Use Elastic Load Balancer**: Distribute traffic
3. **Auto Scaling Group**: Automatic scaling based on demand
4. **RDS Database**: Add persistent data storage
5. **S3 Bucket**: Store model files and backups

## Security Recommendations
- [ ] Use security groups to restrict inbound traffic
- [ ] Enable AWS CloudWatch for monitoring
- [ ] Use AWS Secrets Manager for sensitive data
- [ ] Implement SSL/TLS with AWS Certificate Manager
- [ ] Set up VPC for network isolation
- [ ] Enable EC2 instance monitoring
- [ ] Regular security updates and patches
