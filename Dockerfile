# Use official Python image
FROM python:3.11-slim

# Install system dependencies (for aiohttp, Chrome, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libffi-dev \
    libssl-dev \
    wget \
    curl \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    unzip \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' && \
    apt-get update && \
    apt-get install -y google-chrome-stable

# Set work directory
WORKDIR /app

# Copy all project files
COPY . .

# Upgrade pip & install dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Expose port (optional)
EXPOSE 8080

# Run the bot
CMD ["python", "main.py"]

