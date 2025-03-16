FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    wget \
    gnupg \
    libnss3 \
    libatk1.0-0 \
    libgbm-dev \
    libasound2 \
    libpangocairo-1.0-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libxrender1 \
    libxshmfence1 \
    fonts-liberation \
    xdg-utils \
    gnupg2 \
    lsb-release \
    ca-certificates \
    libcurl4 \
    libssl3 \
    libatk-bridge2.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libgtk-3-0 \
    libvulkan1 \
    libxkbcommon0 \
    && rm -rf /var/lib/apt/lists/*


RUN curl -sSL https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o google-chrome.deb && \
    dpkg -i google-chrome.deb && \
    apt-get update && \
    apt-get install -f -y && \
    rm google-chrome.deb


RUN apt-get install -y chromium-driver


COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt


COPY . .

USER root

RUN groupadd -r celery && useradd -r -m -g celery celery

RUN chown -R celery:celery /app
RUN mkdir -p /app/.selenium_cache && chown -R celery:celery /app/.selenium_cache
RUN mkdir -p /app/.cache/selenium && chown -R celery:celery /app/.cache/selenium

USER celery


CMD ["sh", "-c", "python app/init_db.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
