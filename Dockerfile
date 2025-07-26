# Use full Python base image (not slim) to avoid missing build tools
FROM python:3.11

# Install all system dependencies required for aiohttp, selenium, Chrome
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    pkg-config \
    libffi-dev \
    libssl-dev \
    libc6-dev \
    libxml2-dev \
    libxslt-dev \
    zlib1g-dev \
    libcurl4-openssl-dev \
    libpq-dev \
    libjpeg-dev \
    libsqlite3-dev \
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
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy your project files into the container
COPY . .

# Upgrade pip and install Python packages from requirements.txt
RUN pip install --upgrade pip setuptools wheel
RUN pip install --root-user-action=ignore -r requirements.txt

# Start the bot
CMD ["python", "main.py"]



