#!/bin/bash
# FermTrack Production Deployment Script

set -e

echo "🚀 FermTrack Production Deployment"
echo "=================================="

# Check if running with sudo for system modifications
if [[ $EUID -eq 0 ]]; then
   echo "⚠️  Don't run this script as root. It will prompt for sudo when needed."
   exit 1
fi

# Configuration
APP_DIR="/opt/fermtrack"
SERVICE_USER="fermtrack"
NGINX_AVAILABLE="/etc/nginx/sites-available/fermtrack"
NGINX_ENABLED="/etc/nginx/sites-enabled/fermtrack"
SYSTEMD_SERVICE="/etc/systemd/system/fermtrack.service"

echo "📋 Deployment Configuration:"
echo "   App Directory: $APP_DIR" 
echo "   Service User: $SERVICE_USER"
echo "   Domain: ${DOMAIN:-test.fermtrack.com}"
echo ""

# Function to check commands
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 is not installed. Please install it first."
        exit 1
    fi
}

# Check required tools
echo "🔍 Checking prerequisites..."
check_command "python3"
check_command "nginx"
check_command "systemctl"

# Install system packages
echo "📦 Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv sqlite3 nginx certbot python3-certbot-nginx

# Create service user
echo "👤 Creating service user..."
if ! id "$SERVICE_USER" &>/dev/null; then
    sudo useradd --system --shell /bin/bash --home-dir $APP_DIR --create-home $SERVICE_USER
    echo "✅ Created user: $SERVICE_USER"
else
    echo "ℹ️  User $SERVICE_USER already exists"
fi

# Create app directory and set permissions
echo "📁 Setting up application directory..."
sudo mkdir -p $APP_DIR
sudo chown -R $SERVICE_USER:$SERVICE_USER $APP_DIR

# Copy application files
echo "📋 Copying application files..."
if [ "$PWD" != "$APP_DIR" ]; then
    sudo -u $SERVICE_USER cp -r . $APP_DIR/
    sudo chown -R $SERVICE_USER:$SERVICE_USER $APP_DIR
fi

# Set up Python virtual environment
echo "🐍 Setting up Python environment..."
cd $APP_DIR
sudo -u $SERVICE_USER python3 -m venv venv
sudo -u $SERVICE_USER $APP_DIR/venv/bin/pip install -r backend/requirements.txt

# Set up database
echo "🗄️  Setting up database..."
sudo -u $SERVICE_USER mkdir -p $APP_DIR/backend/instance
sudo -u $SERVICE_USER touch $APP_DIR/backend/instance/fermtrack.db
sudo -u $SERVICE_USER chmod 664 $APP_DIR/backend/instance/fermtrack.db

# Run database migrations
echo "🔄 Running database migrations..."
cd $APP_DIR/backend
sudo -u $SERVICE_USER $APP_DIR/venv/bin/python add_verification_columns.py || true
sudo -u $SERVICE_USER $APP_DIR/venv/bin/python add_applications_table.py || true  
sudo -u $SERVICE_USER $APP_DIR/venv/bin/python add_credit_system.py || true

# Create production environment file
echo "⚙️  Creating production environment..."
sudo -u $SERVICE_USER cp .env.production $APP_DIR/.env

# Create systemd service
echo "🔧 Creating systemd service..."
sudo tee $SYSTEMD_SERVICE > /dev/null <<EOF
[Unit]
Description=FermTrack Fermentation Tracking System
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$APP_DIR/backend
Environment=PATH=$APP_DIR/venv/bin
Environment=FLASK_ENV=production
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 3 --timeout 120 wsgi:app
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create WSGI entry point
echo "🔗 Creating WSGI entry point..."
sudo -u $SERVICE_USER tee $APP_DIR/backend/wsgi.py > /dev/null <<EOF
#!/usr/bin/env python3
import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

# Create the Flask application
app = create_app('production')

if __name__ == "__main__":
    app.run()
EOF

# Create Nginx configuration
echo "🌐 Creating Nginx configuration..."
sudo tee $NGINX_AVAILABLE > /dev/null <<EOF
# FermTrack Nginx Configuration

# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name ${DOMAIN:-test.fermtrack.com};
    return 301 https://\$server_name\$request_uri;
}

# HTTPS Server Configuration
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name ${DOMAIN:-test.fermtrack.com};

    # SSL Configuration (will be configured by certbot)
    # ssl_certificate /etc/letsencrypt/live/${DOMAIN:-test.fermtrack.com}/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/${DOMAIN:-test.fermtrack.com}/privkey.pem;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; font-src 'self' https://cdnjs.cloudflare.com; connect-src 'self'; img-src 'self' data: https:; object-src 'none'; base-uri 'self'; form-action 'self';" always;

    # Root directory for static files
    root $APP_DIR/frontend;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml
        text/css
        text/javascript
        text/xml
        text/plain;

    # Static file caching
    location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header X-Content-Type-Options "nosniff" always;
    }

    # API proxy to Flask backend
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$server_name;
        proxy_redirect off;
        
        # CORS headers for API
        add_header Access-Control-Allow-Origin "https://\$server_name" always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Content-Type, Authorization, X-Bakery-Slug" always;
        add_header Access-Control-Allow-Credentials "true" always;

        # Handle preflight OPTIONS requests
        if (\$request_method = 'OPTIONS') {
            add_header Access-Control-Allow-Origin "https://\$server_name";
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
            add_header Access-Control-Allow-Headers "Content-Type, Authorization, X-Bakery-Slug";
            add_header Access-Control-Allow-Credentials "true";
            add_header Content-Length 0;
            add_header Content-Type text/plain;
            return 204;
        }
    }

    # Frontend application
    location / {
        try_files \$uri \$uri/ /index.html;
        add_header Cache-Control "no-cache, no-store, must-revalidate" always;
        add_header X-Content-Type-Options "nosniff" always;
    }

    # Deny access to sensitive files
    location ~ /\. {
        deny all;
    }

    location ~ \.(htaccess|htpasswd|ini|log|sh|sql|conf)$ {
        deny all;
    }
}
EOF

# Enable nginx site
sudo ln -sf $NGINX_AVAILABLE $NGINX_ENABLED

# Test nginx configuration
echo "🧪 Testing Nginx configuration..."
sudo nginx -t

# Enable and start services
echo "🚀 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable fermtrack
sudo systemctl start fermtrack
sudo systemctl reload nginx

# Set up SSL certificate
if [ -n "$DOMAIN" ]; then
    echo "🔒 Setting up SSL certificate..."
    echo "   Domain: $DOMAIN"
    echo "   This will use Let's Encrypt via certbot"
    echo ""
    read -p "Do you want to set up SSL certificate now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN
    fi
fi

# Set up log rotation
echo "📋 Setting up log rotation..."
sudo tee /etc/logrotate.d/fermtrack > /dev/null <<EOF
$APP_DIR/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 0644 $SERVICE_USER $SERVICE_USER
    postrotate
        systemctl reload fermtrack
    endscript
}
EOF

# Create logs directory
sudo -u $SERVICE_USER mkdir -p $APP_DIR/logs

echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "📋 Service Status:"
sudo systemctl status fermtrack --no-pager -l
echo ""
echo "🌐 Your application should now be available at:"
echo "   https://${DOMAIN:-test.fermtrack.com}"
echo ""
echo "🔍 Useful commands:"
echo "   sudo systemctl status fermtrack    # Check service status"
echo "   sudo systemctl restart fermtrack   # Restart application"
echo "   sudo journalctl -u fermtrack -f    # View live logs"
echo "   sudo nginx -t                      # Test nginx config"
echo "   sudo systemctl reload nginx       # Reload nginx"
echo ""
echo "📚 Check the CLOUDFLARE_CONFIG.md file for Cloudflare setup instructions"