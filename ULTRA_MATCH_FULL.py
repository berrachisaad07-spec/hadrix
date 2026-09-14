import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ===== CONFIG =====
MY_CHANNEL = "https://www.youtube.com/@ayat_khashia"  # حط القناة هنا
SEARCH_KEYWORDS = [
    "football highlights",
    "live match today",
    "champions league",
    "ronaldo skills",
    "messi goals",
    "morocco football",
    "botola pro highlights"
]

SPORT_SITES = [
    "https://www.kora48.com/",
    "https://www.yallagool77.com/",
    "https://www.koora4u.online/"
]

SHORTS_TIME = (15, 40)
VIDEO_TIME = (300, 600)
MATCH_TIME = 120  # ثواني لكل ماتش

visited_matches = set()

# ===== BROWSER =====
def open_browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--user-data-dir=C:/Temp/ChromeProfile")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# ===== HUMAN =====
def human_behavior(driver):
    try:
        driver.execute_script(f"window.scrollBy(0,{random.randint(200,800)});")
        time.sleep(random.uniform(1,3))

        if random.random() < 0.3:
            driver.execute_script("let v=document.querySelector('video'); if(v){v.volume=Math.random();}")

        if random.random() < 0.3:
            driver.execute_script("let v=document.querySelector('video'); if(v){v.muted=!v.muted;}")

    except:
        pass

# ===== YOUTUBE =====
def get_links(driver):
    driver.get(MY_CHANNEL)
    time.sleep(4)

    links = set()
    for _ in range(5):
        driver.execute_script("window.scrollBy(0,800);")
        time.sleep(2)
        vids = driver.find_elements(By.CSS_SELECTOR,"a#video-title, a[href*='/shorts/']")
        for v in vids:
            href = v.get_attribute("href")
            if href:
                links.add(href)
    return list(links)

def youtube_session(driver):
    if not MY_CHANNEL:
        return
    links = get_links(driver)
    if not links:
        return
    driver.get(random.choice(links))
    time.sleep(3)

    start = time.time()
    total = random.randint(120,180)

    while time.time() - start < total:
        try:
            video = driver.find_element(By.TAG_NAME,"video")
            driver.execute_script("arguments[0].play();", video)
            if "/shorts/" not in driver.current_url:
                driver.execute_script("arguments[0].requestFullscreen();", video)
        except:
            pass

        duration = random.randint(*SHORTS_TIME) if "/shorts/" in driver.current_url else random.randint(*VIDEO_TIME)
        t = time.time()
        while time.time() - t < duration:
            human_behavior(driver)
            time.sleep(random.uniform(2,4))

        # NEXT
        try:
            btn = WebDriverWait(driver,5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,"button[aria-label*='Next'],button[aria-label*='suivante']"))
            )
            btn.click()
        except:
            driver.find_element(By.TAG_NAME,"body").send_keys(Keys.ARROW_DOWN)

        time.sleep(2)

# ===== YOUTUBE SEARCH =====
def youtube_search(driver):
    driver.get("https://www.youtube.com")
    time.sleep(3)

    keyword = random.choice(SEARCH_KEYWORDS)
    print("Searching:", keyword)

    try:
        search_box = WebDriverWait(driver,10).until(
            EC.presence_of_element_located((By.NAME,"search_query"))
        )
        search_box.clear()
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.ENTER)
    except:
        return

    time.sleep(4)

    for _ in range(3):
        driver.execute_script("window.scrollBy(0,800);")
        time.sleep(2)

    videos = driver.find_elements(By.CSS_SELECTOR,"a#video-title")
    links = [v.get_attribute("href") for v in videos if v.get_attribute("href")]

    if not links:
        return

    driver.get(random.choice(links))
    time.sleep(3)

    start = time.time()
    total = random.randint(120,180)

    while time.time() - start < total:
        try:
            video = driver.find_element(By.TAG_NAME,"video")
            driver.execute_script("arguments[0].play();", video)
            driver.execute_script("arguments[0].requestFullscreen();", video)
        except:
            pass

        t = time.time()
        duration = random.randint(40,90)
        while time.time() - t < duration:
            human_behavior(driver)
            time.sleep(random.uniform(2,4))

        # NEXT
        try:
            btn = WebDriverWait(driver,5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,"button[aria-label*='Next']"))
            )
            btn.click()
        except:
            break

        time.sleep(2)

# ===== MATCH SYSTEM 🔥 =====
def open_match_and_watch(driver):
    time.sleep(5)

    links = driver.find_elements(By.TAG_NAME,"a")
    match_links = []

    for l in links:
        href = l.get_attribute("href")
        if href and any(w in href.lower() for w in ["match","live","watch"]):
            if href not in visited_matches:
                match_links.append(href)

    if not match_links:
        print("No matches found")
        return

    match_url = random.choice(match_links[:10])
    visited_matches.add(match_url)

    print("Opening:", match_url)
    driver.get(match_url)
    time.sleep(6)

    start = time.time()
    while time.time() - start < MATCH_TIME:
        human_behavior(driver)
        time.sleep(random.uniform(4,8))

    driver.back()
    time.sleep(5)

# ===== TAB =====
def new_tab(driver, url):
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(url)
    time.sleep(5)

# ===== MAIN =====
def main():
    driver = open_browser()
    try:
        while True:
            # قناة YouTube
            youtube_session(driver)

            # البحث في YouTube
            youtube_search(driver)

            # مواقع الماتشات
            site = random.choice(SPORT_SITES)
            new_tab(driver, site)

            for _ in range(3):
                open_match_and_watch(driver)

            time.sleep(random.randint(5,10))
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
