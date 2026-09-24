import os

def load_local_env():
    """تحميل المتغيرات من ملف .env محلياً إذا لم تكن موجودة في البيئة"""
    if os.path.exists(".env"):
        try:
            with open(".env", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        if k.strip() not in os.environ:
                            os.environ[k.strip()] = v.strip()
        except Exception:
            pass

load_local_env()

# الإعدادات العامة وقناة الإشعارات
NTFY_TOPIC = os.getenv("NTFY_TOPIC", "gp_constantine_chem4_alert_2026")
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"

# مفتاح الذكاء الاصطناعي وطراز النموذج
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-3.6-flash"

# روابط مصادر الكلية
FACULTY_BASE_URL = "https://fgp.univ-constantine3.dz"
FACULTY_POSTS_API = f"{FACULTY_BASE_URL}/wp-json/wp/v2/posts"
FACULTY_ANNONCES_FEED = f"{FACULTY_BASE_URL}/category/annonces/feed/"
FACULTY_ACTUALITES_FEED = f"{FACULTY_BASE_URL}/category/actualites/feed/"
FB_PAGE_URL = "https://web.facebook.com/profile.php?id=100083061713979"

# الكلمات المفتاحية المستهدفة لفلترة الأخبار
KEYWORDS = [
    "4 ing", "4ing", "4ème ingénieur", "4eme ingenieur", 
    "4ème année", "4eme annee", "quatrième année", "quatrieme annee",
    "génie chimique", "genie chimique", "gc", "chimique", "chimie",
    "emploi du temps", "planning", "examen", "examens", "tp", 
    "affichage", "rattrapage", "délibération", "deliberation",
    "règlement", "reprise", "stage", "consultation", "note"
]
