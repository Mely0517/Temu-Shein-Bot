# Use official Python image
FROM python:3.11

# Install system dependencies for aiohttp and Chrome
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    curl \
    wget \
    gnupg \
    libgtk-3-0 \
    libnss3 \
    libxss1 \
    libasound2 \
    fonts-liberation \
    xdg-utils \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy everything into the container
COPY . .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install --root-user-action=ignore -r requirements.txt

# Run the bot
CMD ["python", "main.py"]
