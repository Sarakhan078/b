#!/bin/bash
set -e

mkdir -p bin

echo "[*] Compiling raj.c → bin/bgmi"
gcc raj.c -o bin/bgmi -pthread -O2 -lm
chmod +x bin/bgmi
echo "[✓] Binary created: bin/bgmi"

echo "[*] Setting up Python virtual environment"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
echo "[✓] Python dependencies installed"

echo "[*] Build complete. Push repo to Render to deploy."
