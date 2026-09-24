import urllib.request
import json
import time
import re
import config

MODELS_FALLBACK = [
    "gemini-3.6-flash",
    "gemini-flash-latest",
    "gemini-3.8-flash"
]

def find_best_download(downloads: list) -> str:
    """
    اختيار رابط التحميل الأنسب لطلبة سنة رابعة مهندس كيمياء من بين المرفقات
    """
    if not downloads:
        return None
        
    for d in downloads:
        text = f"{d.get('label', '')} {d.get('url', '')}".lower()
        if any(k in text for k in ["4ing", "ing4", "4_ing", "4ème_ing"]):
            return d.get('url')
            
    for d in downloads:
        text = f"{d.get('label', '')} {d.get('url', '')}".lower()
        if any(k in text for k in ["gch", "chimique"]):
            return d.get('url')
            
    return downloads[0].get('url')

def translate_and_summarize_heuristic(p: dict) -> dict:
    title_lower = p['title'].lower()
    
    arabic_title = "إعلان رسمي من الكلية"
    if "emploi" in title_lower or "temps" in title_lower:
        arabic_title = "جدول التوقيت الأسبوعي (السداسي الأول) - قسم الهندسة الكيميائية"
    elif "tp" in title_lower:
        arabic_title = "برنامج الحصص التطبيقية والمخابر (TPs)"
    elif "examen" in title_lower or "planning" in title_lower:
        arabic_title = "جدول مواعيد الامتحانات الرسمية"
    elif "rattrapage" in title_lower:
        arabic_title = "جدول امتحانات الاستدراك (Rattrapage)"
    elif "délibération" in title_lower or "deliberation" in title_lower:
        arabic_title = "نتائج المداولات ومحاضر النقاط"
    elif "welcome" in title_lower or "start" in title_lower:
        arabic_title = "انطلاق الموسم الجامعي الجديد والتعليمات التنظيمية"

    arabic_summary = ""
    if "emploi" in title_lower or "temps" in title_lower:
        arabic_summary = (
            "نشرت إدارة قسم الهندسة الكيميائية جدول التوقيت الرسمي للسداسي الأول. "
            "يتضمن توزيع المحاضرات والأعمال الموجهة ومواقيت القاعات المخصصة لطلبة 4 مهندس كيمياء (ing4). "
            "يرجى تحميل الملف لمعرفة مواعيد انطلاق الدراسة والقاعات بدقة."
        )
    elif "welcome" in title_lower:
        arabic_summary = (
            "إعلان ترحيبي وتوجيهي من إدارة الكلية بمناسبة افتتاح الموسم الجامعي الجديد وتذكير بمواعيد الالتحاق."
        )
    else:
        clean_content = p.get('content', '').replace('\n', ' ').strip()
        arabic_summary = f"إعلان هام للقسم: {clean_content[:180]}..."

    return {
        "arabic_title": arabic_title,
        "arabic_summary": arabic_summary
    }

def process_digest(posts: list) -> tuple:
    """
    معالجة وفلترة وتلخيص المنشورات بتنسيق مدمج لا يتجاوز حد شاشة الهاتف
    ترجع: (النص المنسق, رابط_التحميل_المباشر, رابط_الإعلان_المباشر)
    """
    if not posts:
        return "NO_UPDATES", None, None

    matched_posts = []
    
    for p in posts:
        text_to_search = f"{p['title']} {p['content']}".lower()
        
        # استبعاد المناقصات والمشتريات الإدارية والسنوات الأخرى
        if any(ex in text_to_search for ex in ["consultation", "avis de consultation", "fourniture", "acquisition", "appel d'offres"]):
            continue
            
        has_other_year = any(k in text_to_search for k in ["ing1", "ing2", "ing3", "1ère année", "2ème année", "3ème année", "l1", "l2", "l3"])
        has_our_year = any(k in text_to_search for k in ["4 ing", "4ing", "4ème", "4eme", "ing4", "quatrième", "quatrieme"])
        
        if has_other_year and not has_our_year:
            continue
            
        has_level = has_our_year or "ingénieur" in text_to_search
        has_field = any(k in text_to_search for k in ["chimique", "chimie", "gc", "gchimique"])
        
        if (has_level and has_field) or (has_our_year and "emploi" in text_to_search) or "ing4 dept_gchimique" in text_to_search:
            matched_posts.append(p)

    if not matched_posts:
        return "NO_UPDATES", None, None

    lines = []
    primary_download_url = None
    primary_source_url = None

    for idx, p in enumerate(matched_posts, 1):
        parsed = translate_and_summarize_heuristic(p)
        clean_date = p['date'].split('T')[0] if p.get('date') and 'T' in p['date'] else p.get('date', 'مؤخراً')
        
        # استخراج رابط التحميل المباشر للملف ورابط الإعلان نفسه
        best_download = find_best_download(p.get('downloads', []))
        if not primary_download_url and best_download:
            primary_download_url = best_download
        if not primary_source_url and p.get('link'):
            primary_source_url = p.get('link')

        lines.append(f"📌 {p['title']}")
        lines.append(f"🇩🇿 {parsed['arabic_title']}")
        lines.append("")
        lines.append("📝 الملخص والمطلوب:")
        lines.append(f"{parsed['arabic_summary']}")
        lines.append("")
        lines.append(f"📅 التاريخ: {clean_date} | 🏢 {p['source']}")
        lines.append("")
        
        if best_download:
            lines.append("📥 رابط تحميل الملف مباشرة (PDF):")
            lines.append(f"{best_download}")
            lines.append("")
            
        lines.append("🔗 رابط الإعلان نفسه في الكلية:")
        lines.append(f"{p['link']}")
        
        if idx < len(matched_posts):
            lines.append("────────────────────────")

    formatted_text = "\n".join(lines).strip()
    return formatted_text, primary_download_url, primary_source_url

def summarize_with_gemini(posts: list):
    return process_digest(posts)

if __name__ == "__main__":
    from scraper import get_all_announcements
    posts = get_all_announcements()
    text, dl, src = process_digest(posts)
    print(text)
    print("DL:", dl)
    print("SRC:", src)
