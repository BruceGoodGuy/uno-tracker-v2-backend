# VPS Deployment Guide - Ubuntu Server

Complete guide to deploy Uno Tracker Backend to a fresh Ubuntu VPS server.

## 🚀 Prerequisites

- Fresh Ubuntu 20.04+ VPS
- Root or sudo access
- Domain name (optional, but recommended)
- Basic SSH knowledge

## 📋 Step-by-Step Deployment

### 1. Initial Server Setup

#### Connect to your VPS
```bash
ssh root@your-server-ip
# or
ssh ubuntu@your-server-ip
```

#### Update system packages
```bash
sudo apt update && sudo apt upgrade -y
```

#### Create a new user (if using root)
```bash
# Create user
adduser deployuser
usermod -aG sudo deployuser

# Switch to new user
su - deployuser
```

#### Setup SSH key authentication (recommended)
```bash
# On your local machine, copy your public key
ssh-copy-id deployuser@your-server-ip

# Or manually:
mkdir -p ~/.ssh
nano ~/.ssh/authorized_keys
# Paste your public key, save and exit
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### 2. Install Required Software

#### Install Docker
```bash
# Install dependencies
sudo apt install apt-transport-https ca-certificates curl software-properties-common -y

# Add Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io -y

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Test Docker installation
docker --version
```

#### Install Docker Compose
```bash
# Download Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make executable
sudo chmod +x /usr/local/bin/docker-compose

# Test installation
docker-compose --version
```

#### Install additional tools
```bash
sudo apt install git nginx certbot python3-certbot-nginx ufw -y
```

### 3. Setup Firewall

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow ssh

# Allow HTTP and HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Allow your app port (if needed for testing)
sudo ufw allow 8000

# Check status
sudo ufw status
```

### 4. Clone and Setup Project

#### Clone your repository
```bash
# Navigate to home directory
cd ~

# Clone repository
git clone https://github.com/BruceGoodGuy/uno-tracker-v2.git
cd uno-tracker-v2/uno-tracker-backend

# Or if you need to setup git credentials
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

#### Setup environment variables
```bash
# Copy environment template
cp .env.example .env

# Edit environment file
nano .env
```

**Update your `.env` file for production:**
```env
# Database
POSTGRES_USER=uno_user
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=uno_tracker

# JWT Configuration  
SECRET_KEY=your-super-secure-secret-key-at-least-32-characters-long
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# URLs (replace with your domain)
FRONTEND_URL=https://yourdomain.com
FRONTEND_URL_DEV=https://yourdomain.com/dev
BACKEND_URL=https://api.yourdomain.com

# Security
COOKIE_SECURE=true
```

### 5. Deploy with Docker

#### Start the application
```bash
# Build and start services
docker-compose -f docker-compose.prod.yml up -d

# Check if services are running
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

#### Verify deployment
```bash
# Check if API is responding
curl http://localhost:8000/docs

# Check database connection
docker-compose -f docker-compose.prod.yml exec backend alembic current
```

### 6. Setup Nginx Reverse Proxy

#### Create Nginx configuration
```bash
sudo nano /etc/nginx/sites-available/uno-tracker-backend
```

**Nginx configuration:**
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;  # Replace with your domain

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://localhost:8000/docs;
    }
}
```

#### Enable the site
```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/uno-tracker-backend /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 7. Setup SSL Certificate (Let's Encrypt)

```bash
# Install SSL certificate
sudo certbot --nginx -d api.yourdomain.com

# Test automatic renewal
sudo certbot renew --dry-run

# Setup auto-renewal cron job
sudo crontab -e
# Add this line:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

### 8. Setup Monitoring and Logging

#### Create log directories
```bash
sudo mkdir -p /var/log/uno-tracker
sudo chown $USER:$USER /var/log/uno-tracker
```

#### Setup log rotation
```bash
sudo nano /etc/logrotate.d/uno-tracker
```

**Log rotation configuration:**
```
/var/log/uno-tracker/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
}
```

#### Update docker-compose for logging
```bash
nano docker-compose.prod.yml
```

Add logging configuration to your services:
```yaml
services:
  backend:
    # ... existing configuration
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 9. Setup Process Management

#### Create systemd service (optional)
```bash
sudo nano /etc/systemd/system/uno-tracker.service
```

**Systemd service file:**
```ini
[Unit]
Description=Uno Tracker Backend
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/deployuser/uno-tracker-v2/uno-tracker-backend
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down
TimeoutStartSec=0
User=deployuser

[Install]
WantedBy=multi-user.target
```

#### Enable and start service
```bash
sudo systemctl daemon-reload
sudo systemctl enable uno-tracker.service
sudo systemctl start uno-tracker.service
```

### 10. Backup Strategy

#### Create backup script
```bash
nano ~/backup.sh
```

**Backup script:**
```bash
#!/bin/bash
BACKUP_DIR="/home/deployuser/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U uno_user uno_tracker > $BACKUP_DIR/db_backup_$DATE.sql

# Backup environment and configs
cp .env $BACKUP_DIR/env_backup_$DATE.env

# Remove old backups (keep last 7 days)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.env" -mtime +7 -delete

echo "Backup completed: $DATE"
```

#### Make executable and schedule
```bash
chmod +x ~/backup.sh

# Add to crontab for daily backups at 2 AM
crontab -e
# Add: 0 2 * * * /home/deployuser/backup.sh
```

## 🔧 Maintenance Commands

### Update application
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build

# Check logs
docker-compose -f docker-compose.prod.yml logs -f backend
```

### Database operations
```bash
# Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Create backup
docker-compose -f docker-compose.prod.yml exec db pg_dump -U uno_user uno_tracker > backup.sql

# Restore backup
docker-compose -f docker-compose.prod.yml exec -i db psql -U uno_user uno_tracker < backup.sql
```

### Monitor resources
```bash
# Check Docker containers
docker ps
docker stats

# Check disk usage
df -h
du -sh /var/lib/docker/

# Check memory and CPU
htop
free -h
```

## 🚨 Troubleshooting

### Common issues:

1. **Port already in use**
   ```bash
   sudo lsof -i :8000
   sudo kill -9 <PID>
   ```

2. **Permission denied**
   ```bash
   sudo chown -R $USER:$USER /path/to/project
   ```

3. **Database connection failed**
   ```bash
   docker-compose -f docker-compose.prod.yml logs db
   docker-compose -f docker-compose.prod.yml restart db
   ```

4. **SSL certificate issues**
   ```bash
   sudo certbot certificates
   sudo certbot renew --force-renewal
   ```

## 🔐 Security Checklist

- [ ] SSH key authentication enabled
- [ ] Root login disabled
- [ ] Firewall configured
- [ ] SSL certificate installed
- [ ] Strong passwords used
- [ ] Regular backups scheduled
- [ ] Log monitoring setup
- [ ] Updates automated

## 📊 Monitoring URLs

After deployment, these URLs should work:

- **API Documentation**: `https://api.yourdomain.com/docs`
- **Health Check**: `https://api.yourdomain.com/health`
- **Backend Status**: `https://api.yourdomain.com/auth/test`

## 🎉 Deployment Complete!

Your FastAPI backend is now deployed and running on your Ubuntu VPS with:
- Docker containerization
- Nginx reverse proxy
- SSL encryption
- Automatic backups
- Process monitoring
- Log rotation
