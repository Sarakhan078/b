FROM python:3.12-slim

# Working directory
WORKDIR /app

# Copy repo files
COPY . .

# Create bin folder and compile C binary
RUN mkdir -p bin && gcc raj.c -o bin/bgmi -pthread -O2 -lm && chmod +x bin/bgmi

# Setup venv & install dependencies
RUN python3 -m venv venv && \
    venv/bin/pip install --upgrade pip && \
    venv/bin/pip install -r requirements.txt

# Start both bgmi binary and Python script
CMD ["sh", "-c", "./bin/bgmi & ./venv/bin/python a.py"]
