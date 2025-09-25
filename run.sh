#!/bin/bash
# Compile raj.c to bgmi binary
gcc raj.c -o bgmi -lm
chmod +x bgmi

# Run binary in background
./bgmi &

# Run Telegram bot
python3 a.py
