import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ===== CONFIG =====
MY_CHANNEL = ""
SPORT_SITE = "https://www.kora48.com"

# ===== BROWSER =====
def open_browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--user-data-dir=C:/Temp/ChromeProfile")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# ===== YOUTUBE SHORTS =====
def youtube_session(driver):
    driver.get("https://www.youtube.com")
    time.sleep(3)

    if MY_CHANNEL:
        driver.get(MY_CHANNEL.rstrip("/") + "/shorts")
        time.sleep(5)

        shorts = driver.find_elements(By.CSS_SELECTOR, "a[href*='/shorts/']")
        valid = [s.get_attribute("href") for s in shorts if s.get_attribute("href")]

        if valid:
            driver.get(random.choice(valid))
            time.sleep(3)

            try:
                video = WebDriverWait(driver,10).until(
                    EC.presence_of_element_located((By.TAG_NAME,"video"))
                )
                driver.execute_script("arguments[0].play();", video)
                driver.execute_script("arguments[0].requestFullscreen();", video)
            except:
                pass

            time.sleep(random.randint(20,40))

# ===== CLOSE ADS =====
def close_ads(driver, main):
    for h in driver.window_handles:
        if h != main:
            driver.switch_to.window(h)
            driver.close()
    driver.switch_to.window(main)

# ===== PLAY VIDEO =====
def play_video(driver):
    for _ in range(10):
        try:
            iframes = driver.find_elements(By.TAG_NAME, "iframe")

            for f in iframes:
                try:
                    driver.switch_to.frame(f)
                    time.sleep(2)

                    vids = driver.find_elements(By.TAG_NAME,"video")
                    if vids:
                        driver.execute_script("arguments[0].play();", vids[0])
                        driver.execute_script("arguments[0].requestFullscreen();", vids[0])
                        return True

                    driver.switch_to.default_content()

                except:
                    driver.switch_to.default_content()

            time.sleep(2)

        except:
            pass

    return False

# ===== OPEN STREAM =====
def open_stream(driver):
    main = driver.current_window_handle

    for _ in range(5):
        try:
            btns = driver.find_elements(By.CSS_SELECTOR,"a,button")

            for b in btns:
                try:
                    txt = (b.text or "").lower()
                    if any(w in txt for w in ["watch","live","stream","server","play","مشاهدة","بث"]):
                        if b.is_displayed():
                            driver.execute_script("arguments[0].click();", b)
                            time.sleep(3)
                            close_ads(driver, main)
                except:
                    continue

        except:
            pass

# ===== HUMAN SIMULATION =====
def human_scroll_and_click(driver):
    for _ in range(random.randint(5, 10)):
        try:
            # scroll
            driver.execute_script(f"window.scrollBy(0,{random.randint(300,800)});")
            time.sleep(random.uniform(1,3))

            matches = driver.find_elements(By.CSS_SELECTOR, "div.AY_Match")

            if matches:
                m = random.choice(matches)
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", m)
                time.sleep(1)

                try:
                    link = m.find_element(By.TAG_NAME, "a")
                    driver.execute_script("arguments[0].click();", link)
                    time.sleep(random.randint(5,10))
                except:
                    pass

            # رجوع لور
            if random.random() < 0.3:
                driver.back()
                time.sleep(3)

        except:
            pass

# ===== MATCH =====
def open_match_and_watch(driver):
    try:
        WebDriverWait(driver,15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR,"div.AY_Match"))
        )

        matches = driver.find_elements(By.CSS_SELECTOR,"div.AY_Match")
        if not matches:
            return

        match = random.choice(matches)

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", match)
        time.sleep(2)

        link = match.find_element(By.TAG_NAME,"a")
        driver.execute_script("arguments[0].click();", link)
        time.sleep(6)

    except:
        return

    # فتح البث
    for _ in range(5):
        try:
            btns = driver.find_elements(By.CSS_SELECTOR,"a,button")

            for b in btns:
                txt = (b.text or "").lower()
                if "بث" in txt or "live" in txt:
                    driver.execute_script("arguments[0].click();", b)
                    time.sleep(5)
                    break

            driver.execute_script("window.scrollBy(0,400);")
            time.sleep(2)

        except:
            pass

    open_stream(driver)
    play_video(driver)

    # ===== LOOP =====
    start = time.time()

    while time.time() - start < 900:  # 15 min
        try:
            human_scroll_and_click(driver)

            # تبديل الماتش
            if random.random() < 0.4:
                driver.get(SPORT_SITE)
                time.sleep(5)

        except:
            pass

# ===== TAB =====
def new_tab(driver, url):
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(url)

    for t in driver.window_handles[:-1]:
        driver.switch_to.window(t)
        driver.close()

    driver.switch_to.window(driver.window_handles[0])

# ===== MAIN =====
def main():
    driver = open_browser()

    try:
        youtube_session(driver)

        new_tab(driver, SPORT_SITE)

        open_match_and_watch(driver)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
