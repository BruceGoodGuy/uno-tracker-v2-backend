#!/bin/bash

# Uno Tracker Backend - Quick Deployment Script
# Run this script on your Ubuntu VPS server

set -e

echo "🚀 Starting Uno Tracker Backend Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    print_error "Please don't run this script as root. Use a regular user with sudo privileges."
    exit 1
fi

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker
print_status "Installing Docker..."
if ! command -v docker &> /dev/null; then
    sudo apt install apt-transport-https ca-certificates curl software-properties-common -y
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt update
    sudo apt install docker-ce docker-ce-cli containerd.io -y
    sudo usermod -aG docker $USER
    print_status "Docker installed successfully!"
else
    print_status "Docker already installed, skipping..."
fi

# Install Docker Compose
print_status "Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_status "Docker Compose installed successfully!"
else
    print_status "Docker Compose already installed, skipping..."
fi

# Install additional tools
print_status "Installing additional tools..."
sudo apt install git nginx certbot python3-certbot-nginx ufw htop -y

# Setup firewall
print_status "Configuring firewall..."
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8000

# Clone repository (if not exists)
print_status "Setting up project..."
if [ ! -d "uno-tracker-v2" ]; then
    echo "Enter your GitHub repository URL (or press Enter for default):"
    read -p "Repository URL: " repo_url
    if [ -z "$repo_url" ]; then
        repo_url="https://github.com/BruceGoodGuy/uno-tracker-v2.git"
    fi
    git clone $repo_url
    cd uno-tracker-v2/uno-tracker-backend
else
    print_status "Project directory already exists, updating..."
    cd uno-tracker-v2/uno-tracker-backend
    git pull origin main
fi

# Setup environment variables
print_status "Setting up environment variables..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    print_warning "Please edit the .env file with your configuration:"
    print_warning "nano .env"
    echo
    echo "Required changes:"
    echo "1. Set strong POSTGRES_PASSWORD"
    echo "2. Set strong SECRET_KEY (at least 32 characters)"
    echo "3. Update GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET"
    echo "4. Update FRONTEND_URL and BACKEND_URL with your domain"
    echo "5. Set COOKIE_SECURE=true"
    echo
    read -p "Press Enter after editing .env file..."
fi

# Start Docker services
print_status "Starting Docker services..."
newgrp docker << END
docker-compose -f docker-compose.prod.yml up -d
END

# Wait for services to start
print_status "Waiting for services to start..."
sleep 30

# Check if services are running
print_status "Checking service status..."
docker-compose -f docker-compose.prod.yml ps

# Test API
print_status "Testing API..."
if curl -f http://localhost:8000/docs > /dev/null 2>&1; then
    print_status "API is responding successfully!"
else
    print_error "API is not responding. Check logs:"
    print_error "docker-compose -f docker-compose.prod.yml logs backend"
fi

# Setup Nginx (optional)
read -p "Do you want to setup Nginx reverse proxy? (y/n): " setup_nginx
if [ "$setup_nginx" = "y" ] || [ "$setup_nginx" = "Y" ]; then
    print_status "Setting up Nginx..."
    
    read -p "Enter your domain name (e.g., api.yourdomain.com): " domain_name
    
    # Create Nginx config
    sudo tee /etc/nginx/sites-available/uno-tracker-backend > /dev/null <<EOF
server {
    listen 80;
    server_name $domain_name;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

    # Enable site
    sudo ln -sf /etc/nginx/sites-available/uno-tracker-backend /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Test and restart Nginx
    sudo nginx -t && sudo systemctl restart nginx
    sudo systemctl enable nginx
    
    print_status "Nginx configured successfully!"
    
    # Setup SSL
    read -p "Do you want to setup SSL certificate with Let's Encrypt? (y/n): " setup_ssl
    if [ "$setup_ssl" = "y" ] || [ "$setup_ssl" = "Y" ]; then
        print_status "Setting up SSL certificate..."
        sudo certbot --nginx -d $domain_name --non-interactive --agree-tos --email admin@$domain_name
        print_status "SSL certificate installed successfully!"
    fi
fi

# Create backup script
print_status "Creating backup script..."
cat > ~/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/$(whoami)/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

cd ~/uno-tracker-v2/uno-tracker-backend
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U uno_user uno_tracker > $BACKUP_DIR/db_backup_$DATE.sql
cp .env $BACKUP_DIR/env_backup_$DATE.env

find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.env" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x ~/backup.sh

# Add backup to crontab
print_status "Setting up automatic backups..."
(crontab -l 2>/dev/null; echo "0 2 * * * /home/$(whoami)/backup.sh") | crontab -

echo
echo "🎉 Deployment completed successfully!"
echo
echo "📋 Next steps:"
echo "1. Your API is running at: http://localhost:8000"
if [ ! -z "$domain_name" ]; then
    echo "   Or at: https://$domain_name"
fi
echo "2. API Documentation: http://localhost:8000/docs"
echo "3. Check logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "4. Monitor: docker-compose -f docker-compose.prod.yml ps"
echo
echo "📁 Important files:"
echo "- Project: ~/uno-tracker-v2/uno-tracker-backend"
echo "- Environment: ~/uno-tracker-v2/uno-tracker-backend/.env"
echo "- Backup script: ~/backup.sh"
echo "- Backup location: ~/backups/"
echo
echo "🔧 Useful commands:"
echo "- Update app: cd ~/uno-tracker-v2/uno-tracker-backend && git pull && docker-compose -f docker-compose.prod.yml up -d --build"
echo "- View logs: cd ~/uno-tracker-v2/uno-tracker-backend && docker-compose -f docker-compose.prod.yml logs -f backend"
echo "- Restart: cd ~/uno-tracker-v2/uno-tracker-backend && docker-compose -f docker-compose.prod.yml restart"
