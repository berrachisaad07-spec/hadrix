import time
import random
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException, InvalidSessionIdException, TimeoutException, NoSuchElementException

# ===== ⚙️ CONFIG =====
MY_CHANNEL = ""
SPORT_SITE = "https://www.saad-live.kozow.com/"
PROFILE_PATH = "C:/Temp/ChromeProfile"
WATCH_DURATION = 900  # 15 دقيقة
AD_WAIT_TIME = 40     # ثواني الانتظار في صفحة الإعلان
INTERACT_WITH_ADS = True   # ✅ تفعيل التفاعل مع الإعلانات
INTERACT_WITH_SOCIAL = True # ✅ تفعيل التفاعل مع شريط السوشيال

# ===== 🎯 AD & SOCIAL SELECTORS =====
AD_SELECTORS = [
    # إعلانات جوجل أدسنس
    "ins.adsbygoogle", "iframe[id*='google_ads']", "div[id*='google_ads']",
    # إعلانات عامة
    "div.ad-banner", "div.advertisement", "div.sponsored", "a[href*='adclick']",
    "a[href*='doubleclick']", "a[rel*='sponsored']", "div[class*='ad-']",
    # نوافذ منبثقة
    "div.popup", "div.modal-ad", "button.close-ad", "#ad-overlay",
    # روابط إعلانية شائعة
    "a[href*='bit.ly']", "a[href*='tinyurl']", "a[onclick*='ad']"
]

SOCIAL_SELECTORS = [
    # أزرار المشاركة
    "a[href*='facebook.com/share']", "a[href*='twitter.com/intent']", 
    "a[href*='whatsapp.com/send']", "a[href*='telegram.me/share']",
    # أزرار السوشيال بار
    "div.social-bar a", "div.share-buttons a", "ul.social-icons a",
    # أزرار المتابعة
    "a[title*='تابعنا']", "a[aria-label*='follow']", "button.follow"
]

# ===== 🌐 BROWSER SETUP =====
def open_browser():
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={PROFILE_PATH}")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = {runtime: {}};
        """
    })
    return driver

# ===== 🖱️ HUMAN-LIKE CLICK =====
def human_click(driver, element):
    """نقر بشري: تمرير + تأخير + Hover + Click"""
    try:
        driver.execute_script("arguments[0].scrollIntoView({behavior:'smooth', block:'center'});", element)
        time.sleep(random.uniform(0.5, 1.5))
        
        # Hover قبل النقر (محاكاة بشرية)
        try:
            ActionChains(driver).move_to_element(element).pause(random.uniform(0.3, 0.8)).perform()
            time.sleep(random.uniform(0.2, 0.6))
        except:
            pass
        
        # نقر عبر جافاسكريبت لتجنب مشاكل الحماية
        driver.execute_script("arguments[0].click();", element)
        return True
    except Exception as e:
        print(f"⚠ Click failed: {e}")
        return False

# ===== 📢 INTERACT WITH ADS =====
def interact_with_ads(driver, main_handle):
    """التفاعل مع الإعلانات: نقر عشوائي + انتظار + إغلاق + رجوع"""
    if not INTERACT_WITH_ADS:
        return
    
    try:
        # جمع كل العناصر الإعلانية المحتملة
        ad_elements = []
        for selector in AD_SELECTORS:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for el in elements:
                    if el.is_displayed() and el.is_enabled():
                        ad_elements.append((selector, el))
            except:
                continue
        
        if not ad_elements:
            return
        
        # اختيار عنصر إعلاني عشوائي للنقر (بنسبة 30% فقط لمحاكاة المستخدم)
        if random.random() > 0.3:
            return
            
        selector, ad_elem = random.choice(ad_elements)
        print(f"🎯 Clicking ad: {selector[:40]}...")
        
        # حفظ عدد النوافذ قبل النقر
        handles_before = len(driver.window_handles)
        
        # النقر على الإعلان
        human_click(driver, ad_elem)
        time.sleep(2)
        
        # التحقق إذا فتح الإعلان نافذة/تبويب جديد
        if len(driver.window_handles) > handles_before:
            # التبديل للنافذة الجديدة (صفحة الإعلان)
            new_handle = [h for h in driver.window_handles if h != main_handle][-1]
            driver.switch_to.window(new_handle)
            print(f"📄 Ad page opened - waiting {AD_WAIT_TIME}s...")
            
            # محاكاة التصفح في صفحة الإعلان
            for _ in range(random.randint(3, 7)):
                driver.execute_script(f"window.scrollBy(0, {random.randint(100, 400)});")
                time.sleep(random.uniform(2, 6))
            
            # الانتظار الرئيسي (~40 ثانية مع تغيير بسيط)
            wait_time = AD_WAIT_TIME + random.randint(-5, 8)
            elapsed = 0
            while elapsed < wait_time:
                sleep_chunk = min(random.randint(8, 15), wait_time - elapsed)
                time.sleep(sleep_chunk)
                elapsed += sleep_chunk
                # تمرير عشوائي أثناء الانتظار
                try:
                    driver.execute_script(f"window.scrollBy(0, {random.randint(-200, 300)});")
                except:
                    pass
            
            # إغلاق صفحة الإعلان
            print("🔚 Closing ad page...")
            try:
                driver.close()
            except:
                pass
            
            # الرجوع للنافذة الرئيسية
            if main_handle in driver.window_handles:
                driver.switch_to.window(main_handle)
                print("✅ Returned to main site")
                time.sleep(2)
            else:
                # إذا أُغلقت النافذة الرئيسية بالخطأ، نعيد التوجيه
                driver.get(SPORT_SITE)
                time.sleep(4)
        else:
            # إذا لم يفتح تبويب جديد (إعلان داخل نفس الصفحة)
            print("⚡ In-page ad clicked - waiting 15s...")
            time.sleep(random.randint(12, 20))
            
    except Exception as e:
        print(f"⚠ Ad interaction error: {e}")
        # محاولة الرجوع للصفحة الرئيسية إذا ضاعنا
        try:
            if main_handle in driver.window_handles:
                driver.switch_to.window(main_handle)
        except:
            driver.get(SPORT_SITE)
            time.sleep(3)

# ===== 📱 INTERACT WITH SOCIAL BAR =====
def interact_with_social(driver):
    """التفاعل مع أزرار السوشيال (لايك، مشاركة، متابعة)"""
    if not INTERACT_WITH_SOCIAL:
        return
    
    try:
        social_elements = []
        for selector in SOCIAL_SELECTORS:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for el in elements:
                    if el.is_displayed() and el.is_enabled():
                        social_elements.append((selector, el))
            except:
                continue
        
        if not social_elements:
            return
        
        # نقر على عنصر سوشيال واحد عشوائي (بنسبة 25% فقط)
        if random.random() > 0.25:
            return
            
        selector, social_elem = random.choice(social_elements)
        print(f"📱 Social click: {selector[:35]}...")
        
        # بعض أزرار السوشيال تفتح نافذة منبثقة صغيرة
        handles_before = len(driver.window_handles)
        human_click(driver, social_elem)
        time.sleep(1.5)
        
        # إذا فتحت نافذة منبثقة صغيرة (مشاركة)، نغلقها بعد فترة قصيرة
        if len(driver.window_handles) > handles_before:
            try:
                # التبديل للنافذة الصغيرة
                popup = [h for h in driver.window_handles if h != driver.current_window_handle]
                if popup:
                    driver.switch_to.window(popup[-1])
                    time.sleep(random.randint(3, 7))  # انتظار قصير
                    driver.close()  # إغلاق النافذة المنبثقة
                    # الرجوع للنافذة الرئيسية
                    main = [h for h in driver.window_handles if h != popup[-1]]
                    if main:
                        driver.switch_to.window(main[0])
            except:
                pass
        
        time.sleep(random.uniform(1, 3))
        
    except Exception as e:
        print(f"⚠ Social interaction error: {e}")
        pass

# ===== 🚫 CLOSE UNWANTED POPUPS =====
def close_popups(driver):
    """إغلاق النوافذ المنبثقة غير المرغوبة (إعلانات مزعجة)"""
    try:
        close_selectors = [
            "button.close", "button[class*='close']", "span.close", 
            "a.modal-close", "div[role='button'][aria-label*='close']",
            "button.ad-close", "#close-popup"
        ]
        for sel in close_selectors:
            try:
                btns = driver.find_elements(By.CSS_SELECTOR, sel)
                for btn in btns:
                    if btn.is_displayed():
                        driver.execute_script("arguments[0].click();", btn)
                        time.sleep(0.5)
            except:
                continue
    except:
        pass

# ===== 🎬 YOUTUBE SHORTS =====
def youtube_session(driver):
    if not MY_CHANNEL:
        return True
    try:
        print("📺 Starting YouTube session...")
        driver.get("https://www.youtube.com")
        time.sleep(4)
        driver.get(MY_CHANNEL.rstrip("/") + "/shorts")
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
    for attempt in range(10):
        try:
            videos = driver.find_elements(By.TAG_NAME, "video")
            for v in videos:
                if v.is_displayed():
                    driver.execute_script("try{arguments[0].play();}catch(e){}", v)
                    print("🎬 Video started (main)")
                    return True
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
            time.sleep(1.5)
        except Exception as e:
            print(f"⚠ Play attempt {attempt+1}: {e}")
            pass
    return False

# ===== 🔘 OPEN STREAM BUTTON =====
def open_stream(driver):
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

# ===== 🧍 HUMAN BEHAVIOR =====
def human_scroll_and_click(driver, main_handle):
    try:
        for _ in range(random.randint(3, 6)):
            driver.execute_script(f"window.scrollBy(0, {random.randint(150, 500)});")
            time.sleep(random.uniform(0.7, 2.0))
        
        # ✅ التفاعل مع الإعلانات (إذا فُعّل)
        if INTERACT_WITH_ADS:
            interact_with_ads(driver, main_handle)
        
        # ✅ التفاعل مع السوشيال بار (إذا فُعّل)
        if INTERACT_WITH_SOCIAL:
            interact_with_social(driver)
        
        # إغلاق النوافذ المنبثقة المزعجة
        close_popups(driver)
        
        # البحث عن مباريات مباشرة
        live_xpath = "//div[contains(@class, 'containerMatch') and not(contains(@class, 'End')) and not(contains(.//text(), 'Game Over'))]"
        matches = driver.find_elements(By.XPATH, live_xpath)
        if matches and random.random() < 0.5:
            m = random.choice(matches)
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", m)
            time.sleep(1.5)
            try:
                link = m.find_element(By.TAG_NAME, "a")
                if random.random() < 0.35:
                    driver.execute_script("arguments[0].click();", link)
                    time.sleep(random.randint(5, 12))
                    if random.random() < 0.4:
                        driver.back()
                        time.sleep(3)
            except:
                pass
        if random.random() < 0.2:
            try:
                driver.back()
                time.sleep(2.5)
            except:
                pass
    except Exception as e:
        print(f"⚠ Human sim error: {e}")
        pass

# ===== ⚽ OPEN MATCH =====
def open_match_and_watch(driver):
    try:
        print(f"🔍 Searching LIVE matches on: {driver.current_url}")
        time.sleep(3)
        live_xpath = "//div[contains(@class, 'containerMatch') and not(contains(@class, 'End')) and not(contains(.//text(), 'Game Over'))]"
        matches = driver.find_elements(By.XPATH, live_xpath)
        print(f"📊 Found {len(matches)} LIVE matches")
        if not matches:
            print("⚠ No live matches, trying all...")
            matches = driver.find_elements(By.CSS_SELECTOR, "div.containerMatch")
            if not matches:
                print("❌ No matches found")
                return False
        match_container = random.choice(matches)
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", match_container)
        time.sleep(2)
        try:
            teams = match_container.find_elements(By.CSS_SELECTOR, "div.asm")
            team_names = [t.text for t in teams if t.text.strip()]
            print(f"🎯 Selected: {' vs '.join(team_names)}")
        except:
            pass
        try:
            link = match_container.find_element(By.TAG_NAME, "a")
            href = link.get_attribute("href")
            print(f"🔗 Opening: {href[:80]}...")
            driver.execute_script("arguments[0].click();", link)
        except Exception as e:
            print(f"⚠ Click via link failed: {e}")
            driver.execute_script("arguments[0].click();", match_container)
        time.sleep(6)
        print("🔎 Searching for stream button...")
        if open_stream(driver):
            time.sleep(2)
            if play_video(driver):
                print("✅ Stream is playing!")
            else:
                print("⚠ Could not auto-play video")
        else:
            print("⚠ No stream button found")
        return True
    except TimeoutException:
        print("⏱️ Timeout waiting for matches")
        return False
    except Exception as e:
        print(f"⚠ Match error: {e}")
        try:
            with open("C:/Temp/debug_match.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("💾 Saved debug page")
        except:
            pass
        return False

# ===== 🗂️ NEW TAB =====
def new_tab(driver, url):
    try:
        original = driver.current_window_handle
        driver.execute_script("window.open('','_blank');")
        WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
        new_handle = [h for h in driver.window_handles if h != original][-1]
        driver.switch_to.window(new_handle)
        driver.get(url)
        time.sleep(4)
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
    try:
        print("🔄 Attempting recovery...")
        driver.get(url)
        time.sleep(5)
        return True
    except:
        return False

# ===== 🎯 MAIN =====
def main():
    driver = None
    print("🚀 Saad Live Auto Watcher + ADS - Starting...")
    
    try:
        driver = open_browser()
        print("✅ Chrome started")
        
        if MY_CHANNEL:
            youtube_session(driver)
        
        print(f"🌐 Opening: {SPORT_SITE}")
        if not new_tab(driver, SPORT_SITE):
            print("❌ new_tab failed, trying direct...")
            driver.get(SPORT_SITE)
            time.sleep(5)
        
        main_handle = driver.current_window_handle
        
        if open_match_and_watch(driver):
            print(f"🎬 Watch loop - {WATCH_DURATION//60} min")
            start_time = time.time()
            while time.time() - start_time < WATCH_DURATION:
                try:
                    human_scroll_and_click(driver, main_handle)
                    if random.random() < 0.25:
                        print("🔄 Returning to homepage...")
                        driver.get(SPORT_SITE)
                        time.sleep(4)
                        open_match_and_watch(driver)
                        main_handle = driver.current_window_handle
                    time.sleep(random.randint(30, 70))
                except InvalidSessionIdException:
                    print("⚠ Session lost - recovering...")
                    if not recover_session(driver, SPORT_SITE):
                        break
                except Exception as e:
                    print(f"⚠ Loop error: {e}")
                    time.sleep(5)
                    continue
        else:
            print("⚠ Could not open match, browsing 30s...")
            time.sleep(30)
            
    except Exception as e:
        print(f"❌ Critical: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            try:
                print("🔚 Closing browser...")
                driver.quit()
            except:
                pass
        print("✅ Script finished")

if __name__ == "__main__":
    main()
