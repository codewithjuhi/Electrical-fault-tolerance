# AWS EC2 Deployment - Quick Start

## 5-Minute Quick Start

### 1. Launch EC2 Instance
- Go to AWS Console → EC2 → Launch Instances
- **AMI**: Ubuntu Server 22.04 LTS
- **Type**: t2.micro (free tier)
- **Security Group**: Allow SSH (22), HTTP (80), HTTPS (443)
- Copy your **Public IP**

### 2. Connect via SSH
```bash
ssh -i your-key.pem ubuntu@YOUR_PUBLIC_IP
```

### 3. Run Automated Deployment
```bash
# Download and run deployment script
wget https://raw.githubusercontent.com/codewithjuhi/Electrical-fault-tolerance/main/deploy-aws.sh
bash deploy-aws.sh
```

### 4. Access Application
- **Streamlit UI**: `http://YOUR_PUBLIC_IP:8501`
- **API**: `http://YOUR_PUBLIC_IP:8001`
- **Health Check**: `http://YOUR_PUBLIC_IP:8001/health`

---

## Manual Setup Steps (if automated script doesn't work)

### 1. Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Dependencies
```bash
sudo apt install -y python3.11 python3-pip python3-venv git
```

### 3. Clone & Setup
```bash
cd ~
git clone https://github.com/codewithjuhi/Electrical-fault-tolerance.git
cd Electrical-fault-tolerance
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Run Services
```bash
# Terminal 1 - API
python main.py

# Terminal 2 - UI (new SSH session)
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

---

## Service Management

```bash
# Start services
sudo systemctl start fault-detection-api
sudo systemctl start fault-detection-ui

# Stop services
sudo systemctl stop fault-detection-api
sudo systemctl stop fault-detection-ui

# View logs
sudo journalctl -u fault-detection-api -f
sudo journalctl -u fault-detection-ui -f

# Restart services
sudo systemctl restart fault-detection-api
sudo systemctl restart fault-detection-ui
```

---

## Monitoring & Troubleshooting

### Check if services are running
```bash
sudo systemctl status fault-detection-api
sudo systemctl status fault-detection-ui
```

### Test API connectivity
```bash
curl http://localhost:8001/health
```

### View service errors
```bash
sudo journalctl -u fault-detection-api --no-pager | tail -20
sudo journalctl -u fault-detection-ui --no-pager | tail -20
```

---

## Update Application

```bash
cd ~/Electrical-fault-tolerance
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart fault-detection-api
sudo systemctl restart fault-detection-ui
```

---

## Free Tier Benefits
✅ **t2.micro**: 750 hours/month (free for 12 months)
✅ **20 GB EBS Storage**: Free
✅ **1 GB Data Transfer**: Free
✅ **Total Cost**: $0 for eligible AWS accounts (first 12 months)

---

## Cost After 12 Months
- **t2.micro**: ~$9.50/month
- **EBS Storage**: ~$1.00/month  
- **Total**: ~$10.50/month

Upgrade to t2.small if needed (~$17/month)

---

## Support
- See `AWS_DEPLOYMENT_GUIDE.md` for detailed setup
- See [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- Check logs with: `sudo journalctl -u SERVICE_NAME -f`
