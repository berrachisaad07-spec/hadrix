import time
import random
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ===== CONFIG =====
MY_CHANNEL = "https://www.youtube.com/@ayat_khashia"  # حط هنا رابط القناة ديالك

SPORT_SITES = [
    "https://www.kora48.com/",
    "https://www.yallagool77.com/",
    "https://www.koora4u.online/"
]


# مدة المشاهدة بالثواني
SITE_WATCH_TIME = {
    "youtube.com": 60,
    "koora.live": 600,
    "yalla-shoot.com": 600,
    "livehd7.com": 600
}

SEARCH_TERMS = ["gaming","music","news"]

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
        print("Opening Shorts...")
        shorts_page = MY_CHANNEL.rstrip("/") + "/shorts"
        driver.get(shorts_page)
        time.sleep(5)

        shorts = driver.find_elements(By.CSS_SELECTOR, "a[href*='/shorts/']")
        valid = [s.get_attribute("href") for s in shorts if s.get_attribute("href")]

        if valid:
            short_url = random.choice(valid)
            print("Watching short:", short_url)
            driver.get(short_url)
            time.sleep(3)

            # play + fullscreen
            try:
                player = WebDriverWait(driver,10).until(
                    EC.presence_of_element_located((By.TAG_NAME,"video"))
                )
                driver.execute_script("arguments[0].play();", player)
                driver.execute_script("arguments[0].requestFullscreen();", player)
            except:
                pass

            start = time.time()
            while time.time() - start < random.randint(30,60):
                time.sleep(random.uniform(2,4))
    else:
        print("Search normal...")
        WebDriverWait(driver,15).until(
            EC.presence_of_element_located((By.NAME,"search_query"))
        )
        term = random.choice(SEARCH_TERMS)
        box = driver.find_element(By.NAME,"search_query")
        box.send_keys(term)
        box.send_keys(Keys.RETURN)
        time.sleep(3)

        vids = driver.find_elements(By.CSS_SELECTOR,"a#video-title")
        valid = [v.get_attribute("href") for v in vids if v.get_attribute("href")]
        if valid:
            driver.get(random.choice(valid))

# ===== CLOSE ADS =====
def close_ads(driver, main):
    for h in driver.window_handles:
        if h != main:
            driver.switch_to.window(h)
            driver.close()
    driver.switch_to.window(main)

# ===== STREAM MATCH =====
def open_stream(driver):
    main = driver.current_window_handle
    for _ in range(5):
        try:
            btns = driver.find_elements(By.CSS_SELECTOR,"a,button")
            valid = []
            for b in btns:
                txt = (b.text or "").lower()
                if any(w in txt for w in ["watch","live","stream","server","play"]):
                    if b.is_displayed():
                        valid.append(b)
            if valid:
                driver.execute_script("arguments[0].click();", random.choice(valid[:5]))
                time.sleep(5)
                close_ads(driver, main)
        except:
            pass

def play_video(driver):
    try:
        iframes = driver.find_elements(By.TAG_NAME,"iframe")
        for f in iframes:
            try:
                driver.switch_to.frame(f)
                vids = driver.find_elements(By.TAG_NAME,"video")
                if vids:
                    driver.execute_script("arguments[0].play();", vids[0])
                    driver.execute_script("arguments[0].requestFullscreen();", vids[0])
                    return True
                driver.switch_to.default_content()
            except:
                driver.switch_to.default_content()
    except:
        pass
    return False

def open_match_and_watch(driver, domain):
    time.sleep(6)
    els = driver.find_elements(By.TAG_NAME,"a")
    matches = []
    for e in els:
        txt = (e.text or "").lower()
        if any(w in txt for w in ["vs","match","live"]):
            matches.append(e)
    if not matches:
        matches = els
    driver.execute_script("arguments[0].click();", random.choice(matches[:10]))
    time.sleep(6)
    open_stream(driver)
    play_video(driver)
    duration = SITE_WATCH_TIME.get(domain, 600)
    start = time.time()
    while time.time() - start < duration:
        time.sleep(random.uniform(5,10))

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
        site = random.choice(SPORT_SITES)
        domain = urlparse(site).netloc.replace("www.","")
        new_tab(driver, site)
        open_match_and_watch(driver, domain)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
