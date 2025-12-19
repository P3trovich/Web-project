FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Установка системных зависимостей для Debian Trixie
RUN apt-get update && apt-get install -y \
    fonts-unifont \
    fonts-freefont-ttf \
    libgtk-3-0 \
    libnotify-dev \
    libnss3 \
    libxss1 \
    libasound2t64 \
    libffi8 \
    libx264-164 \
    # Добавляем библиотеки для работы с графикой:
    libdrm2 \
    libgbm1 \
    libxcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxkbcommon0 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libpango-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# Установить браузер Chromium без флага --with-deps
RUN playwright install chromium

COPY . .

EXPOSE 8000