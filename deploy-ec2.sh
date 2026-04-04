#!/bin/bash

# FermTrack EC2 Deployment Script
echo "🚀 Setting up FermTrack on EC2..."

# Change to fermtrack directory
cd /home/ec2-user/fermtrack

# Run database migrations
echo "📂 Running database migrations..."
cd backend
python3 add_verification_columns.py
python3 add_applications_table.py  
python3 add_global_admin.py

# Copy service files
echo "⚙️  Setting up systemd services..."
sudo cp fermtrack-backend.service /etc/systemd/system/
sudo cp fermtrack-frontend.service /etc/systemd/system/

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