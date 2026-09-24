"""
سكربت فحص وتجربة النظام (System Test)
يقوم هذا السكربت بفحص:
1. إرسال إشعار تجريبي فوري إلى هاتفك على ntfy
2. فحص سحب الإعلانات من موقع الكلية وفيسبوك
3. فحص استجابة الذكاء الاصطناعي (Gemini)
"""

import sys
import config
from notifier import send_notification
from scraper import get_all_announcements
from summarizer import summarize_with_gemini

def test_ntfy():
    print(f"\n1️⃣ فحص تطبيق ntfy في الهاتف...")
    print(f"📡 القناة المستهدفة: {config.NTFY_TOPIC}")
    success = send_notification(
        title="🔔 اختبار الاتصال بنجاح!",
        message="مرحباً بك! نظام التلخيص والإشعارات اليومي لكلية هندسة الطرائق - رابعة كيمياء متصل بهاتفك بنجاح.",
        click_url=config.FACULTY_BASE_URL,
        tags="tada,mortar_board",
        priority="high"
    )
    if success:
        print("✅ تم إرسال الإشعار بنجاح! تفقد شاشة هاتفك الآن لتتأكد من ظهوره.")
    else:
        print("❌ فشل إرسال الإشعار.")

def test_scraper():
    print(f"\n2️⃣ فحص سحب الإعلانات من موقع الكلية وفيسبوك...")
    posts = get_all_announcements()
    print(f"✅ تم سحب {len(posts)} إعلان بنجاح.")
    for idx, p in enumerate(posts[:2], 1):
        print(f"   [{idx}] {p['title']} ({p['source']})")
    return posts

def test_ai(posts):
    print(f"\n3️⃣ فحص الذكاء الاصطناعي والتلخيص...")
    summary = summarize_with_gemini(posts)
    print("--- نتيجة التلخيص ---")
    print(summary)
    print("--------------------")

if __name__ == "__main__":
    print("🚀 بدء الفحص الشامل للنظام...")
    test_ntfy()
    posts = test_scraper()
    test_ai(posts)
    print("\n🏁 اكتمل الفحص الشامل!")
