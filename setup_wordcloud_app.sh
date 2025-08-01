#!/bin/bash

set -e

echo "🛠️ Updating system packages..."
sudo apt update && sudo apt upgrade -y

echo "📦 Installing required packages..."
sudo apt install -y python3 python3-pip python3-venv git curl unzip ffmpeg build-essential

echo "🐍 Setting up Python virtual environment..."
APP_DIR="/opt/wordcloud_app"
sudo mkdir -p "$APP_DIR"
sudo chown "$USER":"$USER" "$APP_DIR"
cd "$APP_DIR"
python3 -m venv venv
source venv/bin/activate

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install flask watchdog yt-dlp spacy wordcloud matplotlib

echo "📥 Downloading spaCy English model..."
python3 -m spacy download en_core_web_sm

echo "🗂️ Cloning app repository..."
# Replace with your actual repo
git clone https://github.com/robword/wordcloudr.git src

echo "📁 Setting permissions..."
chmod +x src/app.py

echo "🛠️ Creating systemd service..."
sudo tee /etc/systemd/system/wordcloud.service > /dev/null <<EOF
[Unit]
Description=YouTube WordCloud Web App
After=network.target

[Service]
User=$USER
WorkingDirectory=$APP_DIR/src
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "🚀 Enabling and starting service..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable wordcloud.service
sudo systemctl start wordcloud.service

echo "✅ Wordcloud app installed and running as a service!"
