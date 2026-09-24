"""
نظام المراقبة اللحظية المستمرة (Real-time Live Monitor)
يقوم هذا السكربت بفحص موقع الكلية وصفحة فيسبوك كل 5 دقائق في الخلفية.
- بمجرد نشر أي إعلان جديد لدفعة 4 مهندس كيمياء، سيرن هاتفك فوراً (أولوية عاجلة Urgent).
- في الأوقات العادية، يظل صامتاً تماماً ولا يرسل أي إشعار حتى لا يزعجك.
"""

import time
import sys
from main import check_for_new_announcements

CHECK_INTERVAL_SECONDS = 300

def start_monitoring():
    print("=" * 60, flush=True)
    print("🚀 بدء تشغيل المراقبة اللحظية المباشرة (كل 5 دقائق)", flush=True)
    print("📱 ستصلك الإشعارات في نفس اللحظة التي يُنشر فيها الإعلان!", flush=True)
    print("🔇 لن يتم إرسال أي إشعار في الأوقات التي لا يوجد فيها جديد.", flush=True)
    print("=" * 60, flush=True)

    try:
        check_for_new_announcements()
    except Exception as e:
        print(f"⚠️ خطأ أثناء الفحص: {e}", flush=True)

    while True:
        try:
            print(f"\n⏳ انتهاء دورة الفحص. جاري الانتظار {CHECK_INTERVAL_SECONDS // 60} دقائق للدورة القادمة...", flush=True)
            time.sleep(CHECK_INTERVAL_SECONDS)
            check_for_new_announcements()
        except KeyboardInterrupt:
            print("\n🛑 تم إيقاف المراقبة يدوياً.", flush=True)
            break
        except Exception as e:
            print(f"\n⚠️ تنبيه: حدث خطأ مؤقت أثناء الفحص، سيتم إعادة المحاولة تلقائياً: {e}", flush=True)
            time.sleep(30)

if __name__ == "__main__":
    start_monitoring()
