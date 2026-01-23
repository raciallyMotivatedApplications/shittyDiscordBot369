# Use slim python image to keep size down
FROM python:3.10-slim

# Install system dependencies
# ffmpeg is required for audio
# git is required if we need to install from git urls
# build-essential for compiling some python extensions if needed
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    build-essential \
    libffi-dev \
    libnacl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot files
COPY bot.py .
COPY alarm.mp3 .

# Run the bot
CMD ["python", "bot.py"]
