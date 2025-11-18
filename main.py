import os
import time
import telebot
from threading import Thread
from flask import Flask, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ================= НАЛАШТУВАННЯ =================
# ВАШ ТОКЕН ВПИСАНИЙ ПРЯМО СЮДИ:
BOT_TOKEN = "8599975771:AAEHrZ15guNC80JJDbjg7Z2vKfvrlfubW5M"

MY_CITY_TEXT = "с. Старі Петрівці"
MY_STREET_TEXT = "Князя Святослава"
MY_HOUSE_TEXT = "167а"

# XPATH
XPATH_CITY_ITEM   = "/html/body/div[1]/div[1]/main/section[3]/div/section/div[2]/div[1]/form/div/div[1]/div/div/div/strong"
XPATH_STREET_ITEM = "/html/body/div[1]/div[1]/main/section[3]/div/section/div[2]/div[1]/form/div/div[2]/div/div/div/strong"
XPATH_HOUSE_ITEM  = "/html/body/div[1]/div[1]/main/section[3]/div/section/div[2]/div[1]/form/div/div[3]/div/div/div/strong"
XPATH_ANCHOR = "/html/body/div[1]/div[1]/main/section[3]/div/section/div[2]/div[2]/div[2]/div[2]"

OFFSET_X = 0
OFFSET_Y = 0
# ================================================

bot = telebot.TeleBot(BOT_TOKEN)
server = Flask(__name__)

def slow_type(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(0.05)

def fill_and_click_users_xpath(driver, wait, input_id, text_value, user_xpath, step_name):
    print(f"🔹 {step_name}...")
    try:
        field = wait.until(EC.element_to_be_clickable((By.ID, input_id)))
        field.click()
        field.clear()
        slow_type(field, text_value)
        time.sleep(2) 
        item = wait.until(EC.element_to_be_clickable((By.XPATH, user_xpath)))
        item.click()
        print(f"✅ {step_name}: ОК")
        return True
    except:
        return False

def click_relative_to_header(driver, wait):
    print(f"➡️ Клік від заголовка...")
    try:
        anchor = wait.until(EC.visibility_of_element_located((By.XPATH, XPATH_ANCHOR)))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", anchor)
        time.sleep(1)
        action = ActionChains(driver)
        action.move_to_element(anchor).move_by_offset(OFFSET_X, OFFSET_Y).click().perform()
        print("✅ Клік виконано!")
        return True
    except Exception as e:
        print(f"❌ Помилка кліку: {e}")
        return False

def get_dtek_screenshots():
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1280,1800")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    screenshots = [] 

    try:
        print("🌍 Старт...")
        driver.get("https://www.dtek-krem.com.ua/ua/shutdowns")
        wait = WebDriverWait(driver, 20)

        time.sleep(3)
        try: ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        except: pass

        # 1. ЗАПОВНЕННЯ
        if fill_and_click_users_xpath(driver, wait, "city", MY_CITY_TEXT, XPATH_CITY_ITEM, "Місто"):
            time.sleep(1.5)
            if fill_and_click_users_xpath(driver, wait, "street", MY_STREET_TEXT, XPATH_STREET_ITEM, "Вулиця"):
                time.sleep(1.5)
                fill_and_click_users_xpath(driver, wait, "house_num", MY_HOUSE_TEXT, XPATH_HOUSE_ITEM, "Будинок")

        # 2. ПЕРЕВІРКА
        print("📸 Перевіряю графік...")
        time.sleep(5)
        
        try:
            header_element = wait.until(EC.visibility_of_element_located((By.XPATH, XPATH_ANCHOR)))
        except:
            print("⚠️ Заголовок не знайдено.")
            driver.save_screenshot("error_debug.png")
            return ["error_debug.png"]
        
        # 3. ФОТО СЬОГОДНІ
        driver.save_screenshot("today.png")
        screenshots.append("today.png")

        # 4. ФОТО ЗАВТРА
        if click_relative_to_header(driver, wait):
            print("⏳ Чекаю оновлення...")
            time.sleep(4)
            driver.save_screenshot("tomorrow.png")
            screenshots.append("tomorrow.png")

        return screenshots

    except Exception as e:
        print(f"❌ Error: {e}")
        return []
    finally:
        driver.quit()

@bot.message_handler(commands=['light'])
def send_light(message):
    bot.send_message(message.chat.id, "⚡️ Отримую графіки...")
    files = get_dtek_screenshots()
    if files:
        for i, photo in enumerate(files):
            try:
                if "error" in photo:
                    cap = "Помилка"
                else:
                    cap = "СЬОГОДНІ" if i == 0 else "ЗАВТРА"
                with open(photo, 'rb') as img:
                    bot.send_photo(message.chat.id, img, caption=cap)
            except: pass
    else:
        bot.send_message(message.chat.id, "Помилка.")

# --- ВЕБ-СЕРВЕР ---
@server.route("/")
def webhook():
    return "Bot is running!", 200

def run_web_server():
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 10000)))

if __name__ == "__main__":
    # Запускаємо веб-сервер
    t = Thread(target=run_web_server)
    t.start()
    
    # === ВИПРАВЛЕННЯ ПОМИЛКИ 409 ===
    # Видаляємо старий вебхук, щоб дозволити getUpdates
    print("♻️ Скидаю вебхук...")
    try:
        bot.remove_webhook()
        time.sleep(1)
    except Exception as e:
        print(f"⚠️ Не вдалося скинути вебхук (це ок, якщо його не було): {e}")

    print("✅ Бот запущено!")
    bot.polling(non_stop=True)
