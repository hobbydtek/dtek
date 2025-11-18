# Використовуємо повну версію Python (не slim), щоб уникнути проблем з бібліотеками
FROM python:3.9

# 1. Оновлюємо систему і ставимо wget
RUN apt-get update && apt-get install -y wget --no-install-recommends

# 2. Завантажуємо інсталятор Chrome напряму
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

# 3. Встановлюємо Chrome через apt (він сам підтягне залежності)
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb

# 4. Видаляємо інсталятор, щоб очистити місце
RUN rm google-chrome-stable_current_amd64.deb

# 5. Налаштування робочої папки
WORKDIR /app
COPY . /app

# 6. Встановлення Python-бібліотек
RUN pip install --no-cache-dir -r requirements.txt

# 7. Запуск
CMD ["python", "main.py"]
