import time
import random
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# ==========================================
# ⚙️ الإعدادات (قم بتعديلها حسب حاجتك)
# ==========================================
MY_CHANNEL = "https://www.youtube.com/@ayat_khashia"

# مواقع البث (يمكنك إضافة أو حذف مواقع)
SPORT_SITES = [
    "https://www.kora48.com/",
    "https://www.yallagool77.com/",
    "https://www.koora4u.online/"
]

# مدة المشاهدة بالثواني لكل نوع
SITE_WATCH_TIME = {
    "youtube.com": 45,
    "kora48.com": 300,      # 5 دقائق
    "yallagool77.com": 300,
    "koora4u.online": 300
}

# ⚠️ هام: لاستخدام بروفايلك الأساسي المسجل فيه Gmail، غيّر المسار أدناه
# افتح كروم واكتب chrome://version/ وانسخ مسار "ملف التعريف" (Profile Path)
# مثال: C:\\Users\\YourName\\AppData\\Local\\Google\\Chrome\\User Data
# واترك اسم البروفايل "Default" أو "Profile 1"
CHROME_USER_DATA = r"C:\Users\YOUR_USERNAME\AppData\Local\Google\Chrome\User Data"
CHROME_PROFILE_NAME = "Profile 1"  # أو "Default"

# ==========================================
# 🚀 إعداد المتصفح
# ==========================================
def open_browser():
    options = webdriver.ChromeOptions()
    
    # تفعيل البروفايل الخاص بك
    options.add_argument(f"--user-data-dir={CHROME_USER_DATA}")
    options.add_argument(f"--profile-directory={CHROME_PROFILE_NAME}")
    
    # إعدادات تجنب الكشف وتسين الأداء
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-popup-blocking") # للسماح بفتح روابط البث
    
    print("🚀 جاري تشغيل المتصفح...")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# ==========================================
# 📺 جلسة يوتيوب شورتس
# ==========================================
def youtube_session(driver):
    print("📺 الدخول إلى يوتيوب...")
    driver.get("https://www.youtube.com")
    time.sleep(2)

    if MY_CHANNEL:
        shorts_page = MY_CHANNEL.rstrip("/") + "/shorts"
        print(f"🔗 فتح صفحة الشورتس: {shorts_page}")
        driver.get(shorts_page)
        time.sleep(4) # انتظار تحميل الـ DOM
        
        # تمرير بسيط للأسفل لضمان تحميل عناصر الشورتس
        driver.execute_script("window.scrollBy(0, 300);")
        time.sleep(2)

        try:
            shorts = driver.find_elements(By.CSS_SELECTOR, "a[href*='/shorts/']")
            valid_shorts = [s.get_attribute("href") for s in shorts if s.get_attribute("href") and "shorts" in s.get_attribute("href")]
            
            if valid_shorts:
                short_url = random.choice(valid_shorts)
                print(f"▶️ تم اختيار شورتس للمشاهدة: {short_url}")
                driver.get(short_url)
                time.sleep(3)

                # محاولة تشغيل الفيديو
                try:
                    wait = WebDriverWait(driver, 10)
                    video = wait.until(EC.presence_of_element_located((By.TAG_NAME, "video")))
                    driver.execute_script("arguments[0].play();", video)
                    print("✅ تم تشغيل الفيديو.")
                except TimeoutException:
                    print("⚠️ لم يتم العثور على مشغل الفيديو أو تم حظره.")

                # مدة المشاهدة
                watch_duration = random.randint(30, 50)
                print(f"⏳ مشاهدة لمدة {watch_duration} ثانية...")
                time.sleep(watch_duration)
            else:
                print("⚠️ لم يتم العثور على أي شورتس في القناة.")
        except Exception as e:
            print(f"❌ خطأ في جلسة اليوتيوب: {e}")

# ==========================================
# ⚽ جلسة المواقع الرياضية
# ==========================================
def find_and_play_stream(driver):
    """محاولة ذكية للعثور على مشغل الفيديو داخل الـ iframes"""
    try:
        # البحث عن جميع الـ iframes في الصفحة
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"🔍 تم العثور على {len(iframes)} iframe. جاري الفحص...")
        
        for i, iframe in enumerate(iframes):
            try:
                # الانتقال إلى الـ iframe
                driver.switch_to.frame(iframe)
                
                # البحث عن زر تشغيل أو عنصر فيديو
                videos = driver.find_elements(By.TAG_NAME, "video")
                if videos:
                    print(f"✅ تم العثور على فيديو في iframe رقم {i+1}. جاري التشغيل...")
                    driver.execute_script("arguments[0].play();", videos[0])
                    # محاولة تكبير الشاشة للفيديو (اختياري)
                    # driver.execute_script("arguments[0].requestFullscreen();", videos[0])
                    return True
                
                # العودة للصفحة الرئيسية لفحص الـ iframe التالي
                driver.switch_to.default_content()
            except Exception:
                # في حال فشل الانتقال، نعود للأصل ونكمل
                driver.switch_to.default_content()
                continue
                
        print("⚠️ لم يتم العثور على مشغل فيديو قابل للتشغيل تلقائياً.")
        return False
    except Exception as e:
        print(f"❌ خطأ أثناء البحث عن الفيديو: {e}")
        driver.switch_to.default_content() # تأكد من العودة للوضع الافتراضي
        return False

def open_match_and_watch(driver, site_url):
    domain = urlparse(site_url).netloc.replace("www.", "")
    print(f"⚽ فتح موقع البث: {site_url}")
    
    # فتح تبويب جديد (أفضل طريقة في Selenium 4)
    driver.switch_to.new_window('tab')
    driver.get(site_url)
    
    try:
        # انتظار تحميل الصفحة الأساسية (يتجاوز انتظار Cloudflare أحياناً)
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        print("✅ تم تحميل صفحة الموقع.")
        
        # محاولة العثور على رابط يحتوي على كلمات مفتاحية للمباريات
        time.sleep(3) # انتظار إضافي لعناصر JS
        links = driver.find_elements(By.TAG_NAME, "a")
        match_links = []
        
        keywords = ["مشاهدة", "live", "server", "سيرفر", "watch", "يلا"]
        for link in links:
            text = (link.text or "").lower()
            if any(kw in text for kw in keywords) and link.is_displayed():
                match_links.append(link)
                
        if match_links:
            print(f"🎯 تم العثور على {len(match_links)} رابط محتمل للمباراة.")
            # اختيار رابط عشوائي من أول 3 روابط لتجنب الإعلانات الخادعة في الأسفل
            target_link = random.choice(match_links[:3])
            print(f"🔗 النقر على: {target_link.text}")
            
            # النقر باستخدام JavaScript لتجنب حظر النقرات العادية
            driver.execute_script("arguments[0].click();", target_link)
            time.sleep(5) # انتظار فتح الرابط أو الـ popup
            
            # محاولة تشغيل الفيديو
            find_and_play_stream(driver)
            
            # مدة البث
            duration = SITE_WATCH_TIME.get(domain, 300)
            print(f"⏳ البث قيد التشغيل. الانتظار لمدة {duration} ثانية...")
            
            # محاكاة نشاط بسيط (تحريك الماوس أو التمرير كل فترة) لمنع اعتبار الجلسة خاملة
            start_time = time.time()
            while time.time() - start_time < duration:
                time.sleep(15)
                driver.execute_script("window.scrollBy(0, random.randint(-50, 50));")
        else:
            print("⚠️ لم يتم العثور على روابط مباريات واضحة. جاري تشغيل الفاحص العام...")
            find_and_play_stream(driver)
            time.sleep(SITE_WATCH_TIME.get(domain, 300))
            
    except Exception as e:
        print(f"❌ خطأ في موقع البث: {e}")
    finally:
        # إغلاق تبويب الموقع الرياضي والعودة للتبويب الأصلي
        print("🔒 إغلاق تبويب الموقع الرياضي...")
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

# ==========================================
# 🏁 الدالة الرئيسية
# ==========================================
def main():
    driver = None
    try:
        driver = open_browser()
        
        # 1. جلسة اليوتيوب
        youtube_session(driver)
        
        # 2. جلسة المواقع الرياضية
        selected_site = random.choice(SPORT_SITES)
        open_match_and_watch(driver, selected_site)
        
        print("🎉 اكتملت جميع المهام بنجاح!")
        time.sleep(3)
        
    except Exception as e:
        print(f"❌ خطأ فادح في التشغيل: {e}")
    finally:
        if driver:
            print("🛑 جاري إغلاق المتصفح...")
            driver.quit()

if __name__ == "__main__":
    main()
