#!/bin/bash

# Production deployment script for local Linux server

set -e

APP_DIR="/opt/ai-assist-jamboree"
VENV_DIR="$APP_DIR/.venv"

echo "🚀 Deploying AI Assist Jamboree to production..."

# Create application directory
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Copy application files
echo "📁 Copying application files..."
cp -r . $APP_DIR/
cd $APP_DIR

# Install Python dependencies
echo "📦 Installing dependencies..."
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate
pip install pipenv
pipenv install --deploy --system

# Create www-data user if it doesn't exist
if ! id "www-data" &>/dev/null; then
    sudo useradd --system --shell /bin/false www-data
fi

# Set proper permissions
sudo chown -R www-data:www-data $APP_DIR
sudo chmod +x $APP_DIR/deployment/deploy.sh

# Install systemd services
echo "⚙️  Installing systemd services..."
sudo cp deployment/tornado.service /etc/systemd/system/
sudo cp deployment/flask.service /etc/systemd/system/

# Reload systemd and start services
sudo systemctl daemon-reload
sudo systemctl enable tornado.service flask.service
sudo systemctl start tornado.service flask.service

# Check status
echo "✅ Deployment complete! Checking status..."
sudo systemctl status tornado.service --no-pager -l
sudo systemctl status flask.service --no-pager -l

echo ""
echo "🌐 Applications are running:"
echo "   Flask app: http://$(hostname -I | awk '{print $1}'):5000"
echo "   Tornado app: http://$(hostname -I | awk '{print $1}'):8888"
echo ""
echo "📋 Management commands:"
echo "   sudo systemctl status tornado.service flask.service"
echo "   sudo systemctl restart tornado.service flask.service"
echo "   sudo systemctl stop tornado.service flask.service"
echo "   sudo journalctl -u tornado.service -f"
echo "   sudo journalctl -u flask.service -f"