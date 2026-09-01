FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DISPLAY=:99

# System dependencies for Chromium, Playwright, and virtual display
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    xvfb \
    ca-certificates \
    fonts-liberation \
    fonts-noto-color-emoji \
    libnss3 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libgbm1 \
    libasound2 \
    libxshmfence1 \
    libx11-xcb1 \
    && rm -rf /var/lib/apt/lists/*

# Create an unprivileged application user
RUN useradd \
    --create-home \
    --shell /bin/bash \
    appuser

WORKDIR /app

# Install Python dependencies first for Docker layer caching
COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy application source
COPY app/ ./app/

# Persistent Chromium profile location
RUN mkdir -p /home/appuser/browser-profile \
    && chown -R appuser:appuser /app /home/appuser/browser-profile

USER appuser

# The container itself doesn't need a public browser GUI.
# Xvfb provides the display Chromium needs.
CMD ["bash"]
