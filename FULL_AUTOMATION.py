import time
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# ===== CONFIG =====
PROFILES = [f'Profile {i}' for i in range(1,7)]  # 6 بروفايلات

SEARCH_KEYWORDS = [
    "football highlights",
    "champions league",
    "morocco football"
]

WATCH_TIME = (60,120)
FACEBOOK_TIME = 120
MATCH_TIME = 120

SPORT_SITES = [
    "https://www.kora48.com/",
    "https://www.yallagool77.com/"
]

visited_matches = set()

# ===== HUMAN =====
def human_behavior(driver):
    try:
        actions = [
            lambda: driver.execute_script(f"window.scrollBy(0,{random.randint(200,800)});"),
            lambda: driver.find_element(By.TAG_NAME,"body").send_keys(Keys.ARROW_DOWN),
        ]
        random.choice(actions)()
        time.sleep(random.uniform(1,3))
    except:
        pass

# ===== BROWSER =====
def open_browser(profile):
    options = webdriver.ChromeOptions()
    options.add_argument("--user-data-dir=C:/Temp/ChromeProfile")
    options.add_argument(f"--profile-directory={profile}")
    options.add_argument("--start-maximized")

    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

# ===== GMAIL =====
def wait_for_gmail(driver, timeout=60):
    driver.get("https://mail.google.com")
    time.sleep(5)

    start = time.time()

    while time.time() - start < timeout:
        try:
            if "mail.google.com/mail" in driver.current_url.lower():
                return True
        except:
            pass

        try:
            driver.find_element(By.CSS_SELECTOR,"div[role='main']")
            return True
        except NoSuchElementException:
            pass

        time.sleep(5)

    return False

# ===== YOUTUBE =====
def youtube_session(driver):
    driver.get("https://www.youtube.com")
    time.sleep(3)

    keyword = random.choice(SEARCH_KEYWORDS)

    try:
        box = WebDriverWait(driver,10).until(
            EC.presence_of_element_located((By.NAME,"search_query"))
        )
        box.send_keys(keyword)
        box.send_keys(Keys.ENTER)
    except:
        return

    time.sleep(4)

    vids = driver.find_elements(By.CSS_SELECTOR,"a#video-title")
    links = [v.get_attribute("href") for v in vids if v.get_attribute("href")]

    if not links:
        return

    driver.get(random.choice(links))
    time.sleep(3)

    # ===== FULL SCREEN =====
    try:
        video = WebDriverWait(driver,10).until(
            EC.presence_of_element_located((By.TAG_NAME,"video"))
        )
        video.send_keys("f")  # اضغط على f ليدخل fullscreen
        time.sleep(2)
    except:
        try:
            driver.find_element(By.CSS_SELECTOR,"button.ytp-fullscreen-button").click()
        except:
            pass

    start = time.time()
    total = random.randint(*WATCH_TIME)

    while time.time() - start < total:
        try:
            video = driver.find_element(By.TAG_NAME,"video")
            driver.execute_script("arguments[0].play();", video)
        except:
            pass

        human_behavior(driver)
        time.sleep(random.uniform(2,4))

# ===== FACEBOOK REELS =====
def facebook_reels(driver):
    main_tab = driver.current_window_handle

    try:
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])

        driver.get("https://www.facebook.com/reel/")
        time.sleep(6)

        start = time.time()

        while time.time() - start < FACEBOOK_TIME:
            human_behavior(driver)

            try:
                driver.find_element(By.TAG_NAME,"body").send_keys(Keys.ARROW_DOWN)
            except:
                pass

            time.sleep(random.uniform(5,10))

    finally:
        driver.close()
        driver.switch_to.window(main_tab)

# ===== MATCH =====
def open_match_and_watch(driver):
    time.sleep(5)

    links = driver.find_elements(By.TAG_NAME,"a")
    match_links = []

    for l in links:
        try:
            href = l.get_attribute("href")
            if href and any(w in href.lower() for w in ["match","live","watch"]):
                if href not in visited_matches:
                    match_links.append(href)
        except:
            pass

    if not match_links:
        return

    match_url = random.choice(match_links[:10])
    visited_matches.add(match_url)

    driver.get(match_url)
    time.sleep(6)

    start = time.time()
    while time.time() - start < MATCH_TIME:
        human_behavior(driver)
        time.sleep(random.uniform(4,8))

    driver.back()
    time.sleep(5)

def run_match(driver):
    main_tab = driver.current_window_handle

    try:
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])

        driver.get(random.choice(SPORT_SITES))
        time.sleep(5)

        open_match_and_watch(driver)

    finally:
        driver.close()
        driver.switch_to.window(main_tab)

# ===== MAIN =====
def main():
    for profile in PROFILES:
        print(f"🚀 {profile}")

        driver = open_browser(profile)

        if not wait_for_gmail(driver):
            driver.quit()
            continue

        youtube_session(driver)
        facebook_reels(driver)
        run_match(driver)

        driver.quit()

        delay = random.randint(15,45)
        print("⏳", delay)
        time.sleep(delay)

if __name__ == "__main__":
    main()
