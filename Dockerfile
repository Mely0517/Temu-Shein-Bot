# Use official Python 3.13 slim image
FROM python:3.13-slim

# Install dependencies for Chrome and undetected_chromedriver
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libappindicator3-1 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libasound2 \
    libx11-xcb1 \
    xdg-utils \
    libgbm-dev \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy source code
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose no ports since bot does not listen to HTTP
# Just run the bot on start

CMD ["python", "main.py"]
