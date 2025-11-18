FROM python:3.9-slim

# 1. Встановлюємо wget та gnupg (потрібен для apt-key)
# Ми робимо це першим кроком і одразу очищуємо кеш, щоб зменшити розмір
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    --no-install-recommends

# 2. Додаємо ключі Google та репозиторій Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'

# 3. Встановлюємо сам Google Chrome
RUN apt-get update && apt-get install -y google-chrome-stable

# 4. Налаштовуємо робочу папку
WORKDIR /app
COPY . /app

# 5. Встановлюємо бібліотеки Python
RUN pip install --no-cache-dir -r requirements.txt

# 6. Запускаємо бота
CMD ["python", "main.py"]
