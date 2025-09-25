#!/bin/bash
# Give execute permission
chmod +x bgmi

# Run binary in background
./bgmi &

# Run Python bot
python3 a.py
