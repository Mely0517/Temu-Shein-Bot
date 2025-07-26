# Use official Python slim image
FROM python:3.11-slim

# Install system dependencies required for audioop and Chrome (for undetected-chromedriver)
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libffi-dev \
    libssl-dev \
    libc6-dev \
    libasound2-dev \
    wget \
    curl \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
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
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Set working directory inside container
WORKDIR /app

# Copy all project files into container
COPY . .

# Upgrade pip and install Python dependencies from requirements.txt
RUN pip install --upgrade pip setuptools wheel
RUN pip install --root-user-action=ignore -r requirements.txt

# Expose port (optional, not needed for Discord bot but good practice)
EXPOSE 8080

# Command to run your bot
CMD ["python", "main.py"]
