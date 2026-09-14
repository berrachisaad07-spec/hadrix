import time
import random
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException, InvalidSessionIdException, TimeoutException

# ===== ⚙️ CONFIG =====
MY_CHANNEL = ""  # ضع رابط قناتك هنا إذا أردت مشاهدة شورتس أولاً
SPORT_SITE = "https://www.saad-live.kozow.com/"
PROFILE_PATH = "C:/Temp/ChromeProfile"
WATCH_DURATION = 900  # 15 دقيقة بالثواني

# ===== 🌐 BROWSER SETUP =====
def open_browser():
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={PROFILE_PATH}")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    # إضافات الاستقرار على ويندوز
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    # إخفاء علامات الأتمتة
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # حقن سكربت لإخفاء navigator.webdriver
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = {runtime: {}};
        """
    })
    return driver

# ===== 🎬 YOUTUBE SHORTS SESSION =====
def youtube_session(driver):
    if not MY_CHANNEL:
        return True
    try:
        print("📺 Starting YouTube session...")
        driver.get("https://www.youtube.com")
        time.sleep(4)
        
        channel_url = MY_CHANNEL.rstrip("/") + "/shorts"
        driver.get(channel_url)
        time.sleep(5)
        
        shorts = driver.find_elements(By.CSS_SELECTOR, "a[href*='/shorts/']")
        valid = [s.get_attribute("href") for s in shorts if s.get_attribute("href")]
        
        if valid:
            driver.get(random.choice(valid))
            time.sleep(3)
            try:
                video = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "video")))
                driver.execute_script("try{arguments[0].play();}catch(e){}", video)
            except:
                pass
            time.sleep(random.randint(20, 40))
        return True
    except Exception as e:
        print(f"⚠ YouTube error: {e}")
        return False

# ===== 🚫 CLOSE ADS & POPUPS =====
def close_ads(driver, main_handle):
    try:
        for h in driver.window_handles:
            if h != main_handle:
                try:
                    driver.switch_to.window(h)
                    driver.close()
                except:
                    pass
        driver.switch_to.window(main_handle)
        return True
    except:
        return False

# ===== ▶️ PLAY VIDEO =====
def play_video(driver):
    """محاولة تشغيل الفيديو داخل iframes"""
    for attempt in range(10):
        try:
            # البحث عن فيديو في الصفحة الرئيسية
            videos = driver.find_elements(By.TAG_NAME, "video")
            for v in videos:
                if v.is_displayed():
                    driver.execute_script("try{arguments[0].play();}catch(e){}", v)
                    print("🎬 Video started (main frame)")
                    return True
            
            # البحث داخل iframes
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                try:
                    driver.switch_to.frame(iframe)
                    videos = driver.find_elements(By.TAG_NAME, "video")
                    for v in videos:
                        if v.is_displayed():
                            driver.execute_script("try{arguments[0].play();}catch(e){}", v)
                            driver.switch_to.default_content()
                            print("🎬 Video started (iframe)")
                            return True
                    driver.switch_to.default_content()
                except:
                    driver.switch_to.default_content()
                    continue
            time.sleep(1.5)
        except Exception as e:
            print(f"⚠ Play attempt {attempt+1} failed: {e}")
            pass
    return False

# ===== 🔘 OPEN STREAM BUTTON =====
def open_stream(driver):
    """البحث والنقر على أزرار المشاهدة/البث"""
    main = driver.current_window_handle
    watch_words = ["بث", "مشاهدة", "شاهد", "يلا", "اضغط", "تشغيل", "live", "watch", "play", "server", "hd"]
    
    for _ in range(5):
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, "a, button, div[role='button']")
            for btn in elements:
                try:
                    txt = (btn.text or btn.get_attribute("title") or btn.get_attribute("aria-label") or "").lower()
                    if any(w in txt for w in watch_words):
                        if btn.is_displayed():
                            driver.execute_script("arguments[0].scrollIntoView({behavior:'smooth', block:'center'});", btn)
                            time.sleep(0.8)
                            driver.execute_script("arguments[0].click();", btn)
                            print("✅ Clicked watch button")
                            time.sleep(3)
                            close_ads(driver, main)
                            return True
                except:
                    continue
            driver.execute_script("window.scrollBy(0, 350);")
            time.sleep(1.5)
        except:
            pass
    return False

# ===== 🧍 HUMAN BEHAVIOR SIMULATION =====
def human_scroll_and_click(driver):
    """محاكاة سلوك بشري: تمرير، نقر عشوائي، رجوع"""
    try:
        # تمرير عشوائي للصفحة
        for _ in range(random.randint(3, 6)):
            driver.execute_script(f"window.scrollBy(0, {random.randint(150, 500)});")
            time.sleep(random.uniform(0.7, 2.0))
        
        # البحث عن مباريات مباشرة للتفاعل
        live_xpath = "//div[contains(@class, 'containerMatch') and not(contains(@class, 'End')) and not(contains(.//text(), 'Game Over'))]"
        matches = driver.find_elements(By.XPATH, live_xpath)
        
        if matches and random.random() < 0.5:
            m = random.choice(matches)
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", m)
            time.sleep(1.5)
            
            try:
                link = m.find_element(By.TAG_NAME, "a")
                if random.random() < 0.35:  # 35% فرصة للنقر
                    driver.execute_script("arguments[0].click();", link)
                    time.sleep(random.randint(5, 12))
                    if random.random() < 0.4:
                        driver.back()
                        time.sleep(3)
            except:
                pass
        
        # فرصة صغيرة للرجوع للخلف
        if random.random() < 0.2:
            try:
                driver.back()
                time.sleep(2.5)
            except:
                pass
    except Exception as e:
        print(f"⚠ Human sim error: {e}")
        pass

# ===== ⚽ FIND & OPEN MATCH (مخصص لسعد لايف) =====
def open_match_and_watch(driver):
    try:
        print(f"🔍 Searching for LIVE matches on: {driver.current_url}")
        time.sleep(3)  # انتظار تحميل الديناميكي
        
        # ⚠️ XPath فلتر: مباريات مباشرة فقط (بدون 'End' وبدون 'Game Over')
        live_xpath = "//div[contains(@class, 'containerMatch') and not(contains(@class, 'End')) and not(contains(.//text(), 'Game Over'))]"
        
        matches = driver.find_elements(By.XPATH, live_xpath)
        print(f"📊 Found {len(matches)} LIVE matches")
        
        if not matches:
            print("⚠ No live matches found, trying ALL matches for testing...")
            matches = driver.find_elements(By.CSS_SELECTOR, "div.containerMatch")
            if not matches:
                print("❌ No matches found at all")
                return False
        
        # اختيار مباراة عشوائية
        match_container = random.choice(matches)
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", match_container)
        time.sleep(2)
        
        # استخراج معلومات المباراة للطباعة
        try:
            teams = match_container.find_elements(By.CSS_SELECTOR, "div.asm")
            team_names = [t.text for t in teams if t.text.strip()]
            print(f"🎯 Selected: {' vs '.join(team_names)}")
        except:
            pass
        
        # النقر على رابط المباراة
        try:
            link = match_container.find_element(By.TAG_NAME, "a")
            href = link.get_attribute("href")
            print(f"🔗 Opening: {href[:80]}...")
            driver.execute_script("arguments[0].click();", link)
        except Exception as e:
            print(f"⚠ Click via link failed: {e}, trying container click...")
            driver.execute_script("arguments[0].click();", match_container)
            
        time.sleep(6)  # انتظار تحميل صفحة المباراة
        
        # === محاولة تشغيل البث ===
        print("🔎 Searching for stream button...")
        if open_stream(driver):
            time.sleep(2)
            if play_video(driver):
                print("✅ Stream is playing!")
            else:
                print("⚠ Could not auto-play video, but page is open")
        else:
            print("⚠ No stream button found, but match page is open")
        
        return True
        
    except TimeoutException:
        print("⏱️ Timeout waiting for matches")
        return False
    except Exception as e:
        print(f"⚠ Match error: {e}")
        # حفظ الصفحة للتحليل
        try:
            with open("C:/Temp/debug_match.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("💾 Saved debug page to C:/Temp/debug_match.html")
        except:
            pass
        return False

# ===== 🗂️ SAFE TAB NAVIGATION =====
def new_tab(driver, url):
    """فتح رابط في تبويب جديد بأمان"""
    try:
        original = driver.current_window_handle
        driver.execute_script("window.open('','_blank');")
        WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
        
        new_handle = [h for h in driver.window_handles if h != original][-1]
        driver.switch_to.window(new_handle)
        driver.get(url)
        time.sleep(4)
        
        # إغلاق التبويب الأصلي فقط
        if original in driver.window_handles:
            driver.switch_to.window(original)
            driver.close()
        
        driver.switch_to.window(new_handle)
        return True
    except InvalidSessionIdException:
        print("⚠ Session lost in new_tab")
        return False
    except Exception as e:
        print(f"⚠ new_tab error: {e}")
        return False

# ===== 🔄 RECOVERY =====
def recover_session(driver, url):
    """محاولة استعادة الجلسة إذا انقطعت"""
    try:
        print("🔄 Attempting session recovery...")
        driver.get(url)
        time.sleep(5)
        return True
    except:
        return False

# ===== 🎯 MAIN =====
def main():
    driver = None
    print("🚀 Saad Live Auto Watcher - Starting...")
    
    try:
        # 1️⃣ فتح المتصفح
        driver = open_browser()
        print("✅ Chrome started successfully")
        
        # 2️⃣ جلسة يوتيوب (اختياري)
        if MY_CHANNEL:
            youtube_session(driver)
        
        # 3️⃣ فتح موقع سعد لايف
        print(f"🌐 Opening: {SPORT_SITE}")
        if not new_tab(driver, SPORT_SITE):
            print("❌ new_tab failed, trying direct get...")
            driver.get(SPORT_SITE)
            time.sleep(5)
        
        # 4️⃣ فتح مباراة وبدء المشاهدة
        if open_match_and_watch(driver):
            print(f"🎬 Watch loop started - Duration: {WATCH_DURATION//60} minutes")
            start_time = time.time()
            
            while time.time() - start_time < WATCH_DURATION:
                try:
                    # محاكاة السلوك البشري
                    human_scroll_and_click(driver)
                    
                    # فرصة للعودة للرئيسية وتغيير المباراة
                    if random.random() < 0.25:
                        print("🔄 Returning to homepage...")
                        driver.get(SPORT_SITE)
                        time.sleep(4)
                        open_match_and_watch(driver)
                    
                    # انتظار بين الجولات
                    time.sleep(random.randint(30, 70))
                    
                except InvalidSessionIdException:
                    print("⚠ Session lost - attempting recovery...")
                    if not recover_session(driver, SPORT_SITE):
                        break
                except Exception as e:
                    print(f"⚠ Loop error: {e}")
                    time.sleep(5)
                    continue
        else:
            print("⚠ Could not open match, browsing homepage for 30 seconds...")
            time.sleep(30)
            
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 5️⃣ إغلاق المتصفح بشكل نظيف
        if driver:
            try:
                print("🔚 Closing browser...")
                driver.quit()
            except:
                pass
        print("✅ Script finished")

if __name__ == "__main__":
    main()
