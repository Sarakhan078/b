# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install build tools for compiling C code
RUN apt-get update && \
    apt-get install -y gcc make build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app

# Create virtual environment
RUN python -m venv /app/venv

# Upgrade pip
RUN /app/venv/bin/pip install --upgrade pip

# Install Python dependencies
RUN /app/venv/bin/pip install -r requirements.txt

# Compile raj.c to binary
RUN mkdir -p /app/bin && \
    gcc /app/raj.c -o /app/bin/bgmi -lm && \
    chmod +x /app/bin/bgmi

# Set environment variables for Python
ENV PATH="/app/venv/bin:$PATH"

# Command to run bgmi binary and a.py script
CMD ["/bin/bash", "-c", "/app/bin/bgmi & python /app/a.py"]
