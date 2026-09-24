import os
import json
import datetime
import config
from scraper import get_all_announcements
from summarizer import process_digest
from notifier import send_notification

HISTORY_FILE = "seen_posts.json"

def load_seen_posts() -> set:
    """تحميل قائمة المعرفات والروابط التي تم فحصها وإرسالها مسبقاً"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception as e:
            print(f"⚠️ خطأ في قراءة ملف السجل: {e}")
            return set()
    return set()

def save_seen_posts(seen_set: set):
    """حفظ الروابط والمعرفات في ملف السجل"""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(list(seen_set), f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ خطأ في حفظ ملف السجل: {e}")

def get_post_unique_id(post: dict) -> str:
    """استخراج معرف فريد للمنشور (رابطه أو عنوانه)"""
    return post.get('link') or post.get('title')

def check_for_new_announcements():
    """
    فحص فوري للمنشورات الجديدة وإرسال إشعار فقط في حال وجود جديد يخص رابعة مهندس كيمياء
    """
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now_str}] 🔍 جاري فحص المستجدات من المصادر...")
    
    seen_posts = load_seen_posts()
    is_first_run = (len(seen_posts) == 0)
    
    # 1. سحب الإعلانات
    posts = get_all_announcements()
    if not posts:
        print(f"[{now_str}] ℹ️ لم يتم العثور على أي منشورات حالياً.")
        return

    # إذا كانت هذه أول مرة يشتغل فيها النظام، نسجل المنشورات الحالية حتى لا نرسل منشورات قديمة
    if is_first_run:
        print("📌 التشغيل الأول للنظام: تم تسجيل المنشورات السابقة حتى لا تتكرر.")
        for p in posts:
            seen_posts.add(get_post_unique_id(p))
        save_seen_posts(seen_posts)
        print("✅ النظام جاهز الآن لمراقبة أي منشور جديد يُنشر من هذه اللحظة فصاعداً.")
        return

    # 2. تحديد المنشورات الجديدة كلياً (غير الموجودة في السجل)
    new_unseen_posts = []
    for p in posts:
        p_id = get_post_unique_id(p)
        if p_id not in seen_posts:
            new_unseen_posts.append(p)

    if not new_unseen_posts:
        # لا جديد: هدوء تام وبدون أي إشعار للهاتف
        print(f"[{now_str}] 💤 لا توجد منشورات جديدة. تم التخطي بدون إزعاج أو إرسال إشعار.")
        return

    print(f"[{now_str}] 🚨 تم اكتشاف {len(new_unseen_posts)} منشور جديد لم يُرَ من قبل!")

    # 3. التحقق من مطابقة المنشورات الجديدة لتخصص رابعة كيمياء وتلخيصها
    summary, download_url, source_url = process_digest(new_unseen_posts)

    # 4. تحديث السجل بجميع المنشورات الجديدة التي فحصناها
    for p in new_unseen_posts:
        seen_posts.add(get_post_unique_id(p))
    save_seen_posts(seen_posts)

    # 5. إذا كان المنشور الجديد يخص الطالب، نرسل إشعاراً فورياً عاجلاً
    if summary != "NO_UPDATES" and summary.strip():
        print(f"[{now_str}] ⚡ إرسال إشعار فوري لحظي بالمنشور الجديد إلى هاتفك!")
        send_notification(
            title="رابعة مهندس - هندسة كيميائية",
            message=summary,
            download_url=download_url,
            source_url=source_url,
            tags="rotating_light,mortar_board",
            priority="urgent"  # أولوية عاجلة يرن فوراً
        )
    else:
        print(f"[{now_str}] ℹ️ المنشورات الجديدة تخص تخصصات أخرى، لن يتم إرسال إشعار.")

if __name__ == "__main__":
    check_for_new_announcements()
