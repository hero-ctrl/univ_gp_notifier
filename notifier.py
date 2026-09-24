import urllib.request
from email.header import Header
import config

def send_notification(title: str, message: str, download_url: str = None, source_url: str = None, tags: str = "mortar_board", priority: str = "default"):
    """
    إرسال إشعار فوري إلى تطبيق ntfy في الهاتف.
    - منع تقسيم العنوان عبر maxlinelen لضمان عدم حذف أي حرف مثل 'كيميائية'.
    - زر مباشر لتحميل ملف PDF وزر مباشر لفتح صفحة الإعلان نفسه مباشرة.
    """
    url = config.NTFY_URL
    
    # منع تقسيم العنوان الطويل لكي يظهر كاملاً بدون أي حذف
    encoded_title = Header(title, 'utf-8', maxlinelen=999999).encode()
    
    headers = {
        'Title': encoded_title,
        'Priority': priority,
        'Tags': tags,
        'Content-Type': 'text/plain; charset=utf-8'
    }
    
    # تجهيز الأزرار المباشرة (تحميل الملف + فتح الإعلان مباشرة)
    actions = []
    if download_url:
        actions.append(f"view, Telecharger le fichier (PDF), {download_url}")
    if source_url:
        actions.append(f"view, Voir l annonce directement, {source_url}")
        
    if actions:
        headers['Actions'] = "; ".join(actions)
        
    data = message.encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            if res.status == 200:
                print(f"✅ تم إرسال الإشعار المنسق بنجاح إلى: {config.NTFY_TOPIC}")
                return True
    except Exception as e:
        print(f"❌ تعذر إرسال الإشعار إلى ntfy: {e}")
        return False

if __name__ == "__main__":
    print("🔄 تجربة إرسال...")
    send_notification(
        title="رابعة مهندس - هندسة كيميائية",
        message="تجربة العنوان الكامل",
        download_url="https://fgp.univ-constantine3.dz/wp-content/uploads/2026/09/Emploi-du-temps-actualise-S1_4ING-GCH_2026-2027-1.pdf",
        source_url="https://fgp.univ-constantine3.dz/fr/emplois-du-temps-des-niveaux-m1-et-m2-ing3-et-ing4-dept_gchimique-2026-2027/"
    )
