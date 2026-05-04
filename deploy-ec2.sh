#!/bin/bash

# FermTrack EC2 Deployment Script
echo "🚀 Setting up FermTrack on EC2..."

# Change to fermtrack directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Run database migrations
echo "📂 Running database migrations..."
cd backend
python3 add_verification_columns.py
python3 add_applications_table.py  
python3 add_global_admin.py

# Copy service files (substitute current user into service files)
DEPLOY_USER="$(whoami)"
echo "⚙️  Setting up systemd services (user: $DEPLOY_USER)..."
sed "s/DEPLOY_USER/$DEPLOY_USER/g" "$SCRIPT_DIR/fermtrack-backend.service" | sudo tee /etc/systemd/system/fermtrack-backend.service > /dev/null
sed "s/DEPLOY_USER/$DEPLOY_USER/g" "$SCRIPT_DIR/fermtrack-frontend.service" | sudo tee /etc/systemd/system/fermtrack-frontend.service > /dev/null

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable fermtrack-backend
sudo systemctl enable fermtrack-frontend
sudo systemctl start fermtrack-backend
sudo systemctl start fermtrack-frontend

# Check status
echo "✅ Checking service status..."
sudo systemctl status fermtrack-backend --no-pager
sudo systemctl status fermtrack-frontend --no-pager

echo ""
echo "🎉 FermTrack deployment complete!"
echo "📱 Frontend: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8080"  
echo "🔧 Backend: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):5000"
echo "👤 Default login: admin / admin123"