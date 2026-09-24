import urllib.request
import json
import re
import html
from datetime import datetime
import config

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'fr-FR,fr;q=0.9,ar;q=0.8,en;q=0.7'
}

def clean_html(raw_html: str) -> str:
    """إزالة وسوم HTML وفك الرموز الخاصة للحصول على نص نظيف"""
    if not raw_html:
        return ""
    clean_text = re.sub(r'<[^>]+>', ' ', raw_html)
    clean_text = html.unescape(clean_text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    return clean_text

def extract_downloads(raw_html: str) -> list:
    """
    استخراج روابط تحميل الملفات المرفقة (PDF, Word, Excel, إلخ) من محتوى المنشور
    """
    downloads = []
    if not raw_html:
        return downloads

    matches = re.finditer(r'<a\s+(?:[^>]*?\s+)?href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', raw_html, re.DOTALL | re.IGNORECASE)
    seen_urls = set()

    for m in matches:
        href = m.group(1).strip()
        anchor_text = clean_html(m.group(2))
        href_lower = href.lower()

        # فحص إذا كان الرابط يشير لملف تحميل
        is_file = any(href_lower.endswith(ext) for ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar'])
        is_download_action = any(w in anchor_text.lower() for w in ['télécharger', 'telecharger', 'download', 'تحميل'])

        if (is_file or is_download_action) and href not in seen_urls:
            seen_urls.add(href)
            downloads.append({
                "url": href,
                "label": anchor_text if anchor_text else "تحميل الملف"
            })

    return downloads

def fetch_faculty_posts(limit: int = 15) -> list:
    """
    سحب أحدث الإعلانات مع استخراج روابط التحميل والمرفقات
    """
    url = f"{config.FACULTY_POSTS_API}?per_page={limit}"
    posts = []
    
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=12) as response:
            if response.status == 200:
                raw_data = response.read().decode('utf-8', errors='ignore')
                items = json.loads(raw_data)
                
                for item in items:
                    raw_content = item.get('content', {}).get('rendered', '')
                    raw_excerpt = item.get('excerpt', {}).get('rendered', '')
                    
                    title = clean_html(item.get('title', {}).get('rendered', ''))
                    content = clean_html(raw_content)
                    excerpt = clean_html(raw_excerpt)
                    post_date = item.get('date', '')
                    link = item.get('link', '')
                    
                    # استخراج الملفات والمرفقات القابلة للتحميل
                    downloads = extract_downloads(raw_content)
                    
                    posts.append({
                        "source": "موقع الكلية الرسمي (Faculté GP)",
                        "title": title,
                        "content": content if len(content) > len(excerpt) else excerpt,
                        "date": post_date,
                        "link": link,
                        "downloads": downloads
                    })
    except Exception as e:
        print(f"⚠️ تنبيه: تعذر سحب منشورات الموقع الرسمي: {e}")
        
    return posts

def fetch_facebook_posts() -> list:
    """
    سحب آخر المنشورات والتحديثات من صفحة فيسبوك
    """
    posts = []
    fb_url = "https://www.facebook.com/plugins/page.php?href=https%3A%2F%2Fwww.facebook.com%2Fprofile.php%3Fid%3D100083061713979&tabs=timeline"
    
    try:
        req = urllib.request.Request(fb_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=12) as response:
            if response.status == 200:
                html_content = response.read().decode('utf-8', errors='ignore')
                text_blocks = re.findall(r'<div[^>]*class=\"[^\"]*userContent[^\"]*\"[^>]*>(.*?)</div>', html_content)
                if not text_blocks:
                    clean_page = clean_html(html_content)
                    if any(kw in clean_page.lower() for kw in ['génie', 'chimique', 'ingénieur', 'département']):
                        posts.append({
                            "source": "صفحة فيسبوك الرسمية",
                            "title": "تحديثات ونشاطات من صفحة فيسبوك",
                            "content": clean_page[:400] + "...",
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "link": config.FB_PAGE_URL,
                            "downloads": []
                        })
                else:
                    for block in text_blocks:
                        clean_block = clean_html(block)
                        if clean_block:
                            posts.append({
                                "source": "صفحة فيسبوك الرسمية",
                                "title": clean_block[:60] + "...",
                                "content": clean_block,
                                "date": datetime.now().strftime("%Y-%m-%d"),
                                "link": config.FB_PAGE_URL,
                                "downloads": []
                            })
    except Exception as e:
        print(f"⚠️ تنبيه: تعذر فحص فيسبوك مباشرة: {e}")
        
    return posts

def get_all_announcements() -> list:
    all_posts = []
    web_posts = fetch_faculty_posts()
    all_posts.extend(web_posts)
    fb_posts = fetch_facebook_posts()
    all_posts.extend(fb_posts)
    return all_posts

if __name__ == "__main__":
    print("🔄 فحص استخراج المرفقات وروابط التحميل...")
    results = get_all_announcements()
    for p in results:
        if p.get('downloads'):
            print(f"\n📂 {p['title']}")
            for d in p['downloads']:
                print(f"  ⬇️ {d['label']}: {d['url']}")
